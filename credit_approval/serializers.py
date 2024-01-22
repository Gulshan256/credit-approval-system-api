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