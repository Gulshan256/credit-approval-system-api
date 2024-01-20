from datetime import datetime,date, timedelta
import traceback
from dateutil.relativedelta import relativedelta
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum
from .models import Customer, Loan
from .serializers import CustomerRegistrationSerializer,EligibilityCheckSerializer,CreateLoanSerializer,LoanDetailsSerializer,LoanDetailsCustomerSerializer,CheckEligibilityRequestSerializer,CheckEligibilityResponseSerializer,CreateLoanRequestSerializer,CreateLoanResponseSerializer
from rest_framework.decorators import api_view

from .tasks import ingest_customer_data, ingest_loan_data
from django.db.models import Sum
from django.db import models

# Create your views here.


def index(request):
    return HttpResponse("Hello, world. You're at the credit_approval index.")



def import_data(request):
    ingest_customer_data.delay()
    ingest_loan_data.delay()
    return HttpResponse("Data import started")



@api_view(['POST'])
def register_customer(request):
    if request.method == 'POST':
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            response_data = serializer.save()
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    else:
        return Response({'error': 'Method not allowed'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)








@api_view(['POST'])
def check_eligibility(request):
    try:
        serializer = CheckEligibilityRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']

        # Placeholder logic for credit score calculation
        credit_score = calculate_credit_score(customer_id)
        # if credit_score is zero then return a meaningful message response
        if credit_score == 0:
            return Response({'customer_id': customer_id,
            'approval': False,
            'message': "Credit score is zero, please try again later"}, status=status.HTTP_200_OK)

        # Placeholder logic for eligibility check and interest rate correction
        approval, corrected_interest_rate = check_loan_eligibility(customer_id, credit_score, loan_amount, interest_rate)
        # if approval and corrected_interest_rate both are false then return a meaningful message response
        if approval == False and corrected_interest_rate == 0:
            return Response({'customer_id': customer_id,
            'approval': False,
            'message': "Loan not approved, your current loan amount is greater than approved limit"}, status=status.HTTP_200_OK)

        # Calculate monthly installment based on corrected interest rate
        monthly_installment = calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure)

        response_data = {
            'customer_id': customer_id,
            'approval': approval,
            'interest_rate': interest_rate,
            'corrected_interest_rate': corrected_interest_rate,
            'tenure': tenure,
            'monthly_installment': monthly_installment,
        }

        response_serializer = CheckEligibilityResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(traceback.format_exc())}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def check_loan_eligibility(customer_id, credit_score, loan_amount, interest_rate):
    try:
        customer = Customer.objects.get(customer_id=customer_id)

        loans = Loan.objects.filter(customer_id=customer_id)

        total_current_loan_amount = loans.exclude(end_date__lt=date.today()).aggregate(Sum('loan_amount'))['loan_amount__sum']
        approved_limit = customer.approved_limit

        if total_current_loan_amount is not None and total_current_loan_amount > approved_limit:
            return False, 0  # If sum of current loans > approved limit, don't approve any loans

        if credit_score > 50:
            return True, interest_rate  # Approve loan as is

        elif 50 > credit_score > 30:
            return True, max(interest_rate, 12.0)  # Approve loans with interest rate > 12%

        elif 30 > credit_score > 10:
            return True, max(interest_rate, 16.0)  # Approve loans with interest rate > 16%

        else:
            return False, 0  # Don't approve any loans if credit score < 10

    except Exception as e:
        print(f"Error checking loan eligibility: {str(e)}")
        return False, 0  # Default to not approving loans if an error occurs
    

def calculate_monthly_installment(loan_amount, interest_rate, tenure):
    try:
        print('loan_amount',loan_amount,'interest_rate',interest_rate,'tenure',tenure)
        if tenure == 0:
            raise ValueError("Tenure cannot be zero")

        monthly_interest_rate = interest_rate / 12 / 100
        num_installments = tenure
        monthly_installment = (loan_amount * monthly_interest_rate) / (1 - (1 + monthly_interest_rate) ** -num_installments)
        return monthly_installment

    except ValueError as ve:
        print(f"ValueError calculating monthly installment: {str(ve)}")
        return 0.0

    except Exception as e:
        print(f"Error calculating monthly installment: {str(traceback.format_exc())}")
        return 0.0

def calculate_credit_score(customer_id):
    try:
        loans = Loan.objects.filter(customer_id=customer_id, end_date__gte=date.today())

        total_loan_amount = loans.aggregate(Sum('loan_amount'))['loan_amount__sum']
        num_loans = loans.count()

        if total_loan_amount is not None and num_loans > 0:
            average_loan_amount = total_loan_amount / num_loans
            return min(int((average_loan_amount / 1000) * 10), 100)

    except Exception as e:
        print(f"Error calculating credit score: {str(e)}")

    return 0  # Default credit score if calculation fails

#  /create-loan
@api_view(['POST'])
def create_loan(request):
    try:
        serializer = CreateLoanRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer_id = serializer.validated_data['customer_id']
        loan_amount = serializer.validated_data['loan_amount']
        interest_rate = serializer.validated_data['interest_rate']
        tenure = serializer.validated_data['tenure']

        # Placeholder logic for credit score calculation
        credit_score = calculate_credit_score(customer_id)

        # Placeholder logic for eligibility check and interest rate correction
        approval, corrected_interest_rate = check_loan_eligibility(customer_id, credit_score, loan_amount, interest_rate)

        if approval:
            # Create a new Loan if the loan is approved
            loan = Loan.objects.create(
                customer_id=Customer.objects.get(customer_id=customer_id),
                loan_amount=loan_amount,
                tenure=tenure,
                interest_rate=corrected_interest_rate,
                monthly_repayment=calculate_monthly_installment(loan_amount, corrected_interest_rate, tenure),
                emis_paid_on_time=0,  # Assuming no EMIs have been paid on time initially
                start_date=date.today(),
                end_date=date.today() + timedelta(days=(30 * tenure)),  # Assuming each month has 30 days
            )

            response_data = {
                'loan_id': loan.id,
                'customer_id': customer_id,
                'loan_approved': True,
                'message': 'Loan approved',
                'monthly_installment': loan.monthly_repayment,
            }
        else:
            response_data = {
                'loan_id': None,
                'customer_id': customer_id,
                'loan_approved': False,
                'message': 'Loan not approved',
                'monthly_installment': 0.0,
            }

        response_serializer = CreateLoanResponseSerializer(response_data)
        return Response(response_serializer.data, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




@api_view(['GET'])
def view_loan_by_loan_id(request, loan_id):
    try:
        loan = Loan.objects.get(loan_id=loan_id)
        serializer = LoanDetailsSerializer({
            'loan_id': loan.loan_id,
            'customer': {
                'customer_id': loan.customer_id.customer_id,
                'first_name': loan.customer_id.first_name,
                'last_name': loan.customer_id.last_name,
                'phone_number': loan.customer_id.phone_number,
                'age': loan.customer_id.age,
            },
            'loan_amount': loan.loan_amount,
            'interest_rate': loan.interest_rate,
            'monthly_installment': loan.monthly_repayment,
            'tenure': loan.tenure,
        })
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Loan.DoesNotExist:
        return Response({'error': 'Loan not found'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
def view_loans_by_customer(request, customer_id):
    try:
        current_date = date.today()
        loans = Loan.objects.filter(
            customer_id=customer_id,
            start_date__lte=current_date,
            end_date__gte=current_date
        )

        loan_data = []
        for loan in loans:
            # Calculate repayments_left based on complete months until the end date
            remaining_months = relativedelta(loan.end_date, current_date).months
            repayments_left = max(0, loan.tenure - remaining_months)



            serializer = LoanDetailsCustomerSerializer({
                'loan_id': loan.loan_id,
                'loan_amount': loan.loan_amount,
                'interest_rate': loan.interest_rate,
                'monthly_installment': loan.monthly_repayment,
                'tenure': loan.tenure,
                'repayments_left': repayments_left,
            })
            loan_data.append(serializer.data)

        return Response(loan_data, status=status.HTTP_200_OK)
    except Loan.DoesNotExist:
        return Response({'error': 'No loans found for the customer'}, status=status.HTTP_404_NOT_FOUND)
    



