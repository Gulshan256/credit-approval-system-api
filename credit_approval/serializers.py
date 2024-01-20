# credit_approval/serializers.py
from datetime import datetime
from rest_framework import serializers
from .models import Customer,Loan
from django.db.models import Sum
from django.db.models import Sum, Value
from django.db.models.functions import Coalesce
from .loan_eligibility import *




class CustomerRegistrationSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'age','monthly_salary', 'phone_number']

        """
        Request body:
        {
            "first_name": "John",
            "last_name": "Doe",
            "age": 30,
            "monthly_income": 100000,
            "phone_number": 9876543210
        }
        """
        
        

    def validate(self, data):
        first_name = data['first_name']
        last_name = data['last_name']
        age = data['age']
        monthly_salary = data['monthly_salary']
        phone_number = data['phone_number']

        # Check if the customer already exists
        if Customer.objects.filter(first_name=first_name, last_name=last_name, age=age, monthly_salary=monthly_salary, phone_number=phone_number).exists():
            raise serializers.ValidationError(f"Customer with name {first_name} {last_name} already exists")

        # Check if the age is between 18 and 60
        if age < 18 or age > 60:
            raise serializers.ValidationError(f"Age {age} is not between 18 and 60")

        return data
    
    def create(self, validated_data):
        first_name = validated_data['first_name']
        last_name = validated_data['last_name']
        age = validated_data['age']
        monthly_income = validated_data['monthly_salary']
        phone_number = validated_data['phone_number']

        # Calculate approved_limit using the provided formula
        approved_limit = round(36 * monthly_income / 100000) * 100000

        # Create a new customer with the calculated approved_limit
        customer = Customer.objects.create(approved_limit=approved_limit, **validated_data)

        # Prepare the response body
        response_data = {
            'customer_id': customer.customer_id,
            'name': f"{customer.first_name} {customer.last_name}",
            'age': age,
            'monthly_income': monthly_income,
            'approved_limit': approved_limit,
            'phone_number': phone_number
        }

        return response_data


    

class EligibilityCheckSerializer(serializers.ModelSerializer):

    class Meta:
        model = Loan
        fields = ['customer_id', 'loan_amount', 'interest_rate', 'tenure']


    def validate(self, data):
        customer_id = data['customer_id']
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']

        # Check if the customer exists
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            raise serializers.ValidationError(f"Customer with id {customer_id} does not exist")

        # Check if the loan_amount is greater than the approved_limit
        if loan_amount > customer.approved_limit:
            raise serializers.ValidationError(f"Loan amount {loan_amount} is greater than the approved limit {customer.approved_limit}")

        # Check if the sum of all current EMIs > 50% of monthly salary
        if Loan.objects.filter(customer_id=customer.customer_id).aggregate(
                                monthly_repayment_sum=Coalesce(Sum('monthly_repayment'), Value(0))
                )['monthly_repayment_sum'] > 0.5 * customer.monthly_salary:
            raise serializers.ValidationError(f"Sum of all current EMIs is greater than 50% of monthly salary")

        # Check if the interest rate matches the slab
        credit_rating=self.calculate_credit_rating(customer)
        if credit_rating >= 50:
            if interest_rate < 12:
                data['corrected_interest_rate'] = 12
        elif 50 > credit_rating >= 30:
            if interest_rate < 16:
                data['corrected_interest_rate'] = 16
        elif 30 > credit_rating >= 10:
            if interest_rate < 20:
                data['corrected_interest_rate'] = 20
        else:
            raise serializers.ValidationError(f"Credit rating is less than 10")
       
        return data
    
    def create(self, validated_data):
        # Extracting validated data
        customer_id = validated_data['customer_id']
        loan_amount = validated_data['loan_amount']
        interest_rate = validated_data['interest_rate']
        tenure = validated_data['tenure']

        # Retrieve the customer instance using the provided customer_id
        try:
            customer = Customer.objects.get(customer_id=customer_id)
        except Customer.DoesNotExist:
            raise serializers.ValidationError(f"Customer with id {customer_id} does not exist")

        # Calculate monthly_installment using the provided formula
        monthly_installment = calculate_monthly_installment(loan_amount,interest_rate,tenure)

        # Create a new loan
        loan = Loan.objects.create(
            customer=customer.customer_id,  # Use the customer instance here
            loan_amount=loan_amount,
            interest_rate=interest_rate,
            tenure=tenure,
            monthly_repayment=monthly_installment
        )

        # Prepare the response body
        response_data = {
            'customer_id': customer_id,
            'approval': True,
            'interest_rate': interest_rate,
            'corrected_interest_rate': validated_data.get('corrected_interest_rate', interest_rate),
            'tenure': tenure,
            'monthly_installment': monthly_installment
        }

        return response_data


    def calculate_credit_rating(self,customer):

        lones = Loan.objects.filter(customer_id=customer)
        total_ratings_weights = 100
        weights = {
		"past_loans_paid_on_time": 0.4,
		"num_past_loans": 0.25,
		"current_year_loans": 0.2,
		"loan_approved_volume": 0.1,
	    }

        # Calculate the number of past loans paid on time
        past_loans_paid_on_time = sum(loan.emis_paid_on_time for loan in lones)

        # Calculate the number of past loans
        num_past_loans = lones.count()

        # Calculate the number of loans taken in the current year
        current_year_loans = sum(loan.start_date.year == datetime.now().year for loan in lones)

        # Calculate the total loan amount approved in the past
        loan_approved_volume = sum(loan.loan_amount for loan in lones)

        # Calculate the credit rating
        credit_rating = round(
            (past_loans_paid_on_time * weights['past_loans_paid_on_time'] +
            num_past_loans * weights['num_past_loans'] +
            current_year_loans * weights['current_year_loans'] +
            loan_approved_volume * weights['loan_approved_volume']) / total_ratings_weights * 100
        )

        return credit_rating






class CreateLoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['customer_id', 'loan_amount', 'interest_rate', 'tenure']

    def validate(self, data):
        customer_id = data['customer_id']
        loan_amount = data['loan_amount']
        interest_rate = data['interest_rate']
        tenure = data['tenure']

        # Check if the customer exists
        try:
            customer = Customer.objects.get(customer_id=customer_id.customer_id)
        except Customer.DoesNotExist:
            raise serializers.ValidationError(f"Customer with id {customer_id} does not exist")

        # Check if the loan_amount is greater than the approved_limit
        if loan_amount > customer.approved_limit:
            raise serializers.ValidationError(f"Loan amount {loan_amount} is greater than the approved limit {customer.approved_limit}")

        # Check if the sum of all current EMIs > 50% of monthly salary
        if Loan.objects.filter(customer_id=customer).aggregate(
                                monthly_repayment_sum=Coalesce(Sum('monthly_repayment'), Value(0))
                )['monthly_repayment_sum'] > 0.5 * customer.monthly_salary:
            raise serializers.ValidationError(f"Sum of all current EMIs is greater than 50% of monthly salary")

        # Check if the interest rate matches the slab
        credit_rating=self.calculate_credit_rating(customer)
        if credit_rating >= 50:
            if interest_rate < 12:
                data['corrected_interest_rate'] = 12
        elif 50 > credit_rating >= 30:
            if interest_rate < 16:
                data['corrected_interest_rate'] = 16
        elif 30 > credit_rating >= 10:
            if interest_rate < 20:
                data['corrected_interest_rate'] = 20
        else:
            raise serializers.ValidationError(f"Credit rating is less than 10")
       
        return data
    

    def calculate_credit_rating(self,customer):

        loans = Loan.objects.filter(customer_id=customer)
        
        weights = {
            "past_loans_paid_on_time": 0.4,
            "num_past_loans": 0.25,
            "current_year_loans": 0.2,
            "loan_approved_volume": 0.1,
        }

        # Calculate the number of past loans paid on time
        past_loans_paid_on_time = sum(loan.emis_paid_on_time for loan in loans)

        # Calculate the number of past loans
        num_past_loans = loans.count()

        # Calculate the number of loans taken in the current year
        current_year_loans = sum(loan.start_date.year == datetime.now().year for loan in loans)

        # Calculate the total loan amount approved in the past
        loan_approved_volume = sum(loan.loan_amount for loan in loans)

        data = {
            "past_loans_paid_on_time": past_loans_paid_on_time,
            "num_past_loans": num_past_loans,
            "current_year_loans": current_year_loans,
            "loan_approved_volume": loan_approved_volume,
            "current_loans_sum": loans.aggregate(Sum('loan_amount'))['loan_amount__sum'],
            "approved_limit": 3000000,
        }

        # print(data)

        # Check if current loans exceed approved limit
        if data["current_loans_sum"] > data["approved_limit"]:
            return 0

        scores = {
            "past_loans_paid_on_time": {
                100: 5,
                95: 4,
                90: 3,
                80: 2,
                0: 1,
            }.get(data["past_loans_paid_on_time"], 0),
            "num_past_loans": {
                0: 5,
                3: 4,
                6: 3,
                9: 2,
                12: 1,
            }.get(data["num_past_loans"], 1),
            "current_year_loans": {
                0: 5,
                2: 4,
                4: 3,
                6: 1,
            }.get(data["current_year_loans"], 1),
            "loan_approved_volume": {
                "High": 5,
                "Moderate": 3,
                "Low": 1,
            }.get(data["loan_approved_volume"], 1),
        }

        # calculate ttal score out of 100
        total_score = sum(scores.values())

        # calculate credit rating
        credit_rating = round(total_score / 25 * 100)

        return credit_rating
        




class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['customer_id', 'first_name', 'last_name', 'phone_number', 'age']

class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ['loan_id', 'loan_amount', 'interest_rate', 'monthly_repayment', 'tenure']




class LoanDetailsSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    customer = CustomerSerializer()  # Use the CustomerSerializer here
    loan_amount = serializers.IntegerField()
    interest_rate = serializers.FloatField()
    monthly_installment = serializers.FloatField()
    tenure = serializers.IntegerField()


class LoanDetailsCustomerSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    loan_amount = serializers.IntegerField()
    interest_rate = serializers.FloatField()
    monthly_installment = serializers.FloatField()
    tenure = serializers.IntegerField()
    repayments_left = serializers.IntegerField()





class CheckEligibilityRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()

class CheckEligibilityResponseSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    approval = serializers.BooleanField()
    interest_rate = serializers.FloatField()
    corrected_interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()


class CreateLoanRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()


class CreateLoanResponseSerializer(serializers.Serializer):
    loan_id = serializers.IntegerField()
    customer_id = serializers.IntegerField()
    loan_amount = serializers.FloatField()
    interest_rate = serializers.FloatField()
    tenure = serializers.IntegerField()
    monthly_installment = serializers.FloatField()