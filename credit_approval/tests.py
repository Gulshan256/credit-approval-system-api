from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from .models import Customer, Loan

class CustomerRegistrationAPITest(TestCase):
    def setUp(self):
        # Create an instance of the API client
        self.client = APIClient()

    def test_register_customer_valid_data(self):
        # URL for the register_customer API
        url = reverse('register-customer')

        # Data for a valid customer registration
        valid_data = {
            'first_name': 'Rohan',
            'last_name': 'Sharma',
            'age': 25,
            'monthly_salary': 5000,
            'phone_number': 7089652123
        }

        # Make a POST request to the API with valid data
        response = self.client.post(url, valid_data, format='json')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response data matches the expected data
        expected_data = {
            'customer_id': response.data['customer_id'],
            'name': 'Rohan Sharma',
            'age': 25,
            'monthly_income': 5000,
            'approved_limit': round(36 * 5000 / 100000) * 100000,
            'phone_number': 7089652123
        }
        self.assertEqual(response.data, expected_data)

        # Assert that the customer is created in the database
        self.assertTrue(Customer.objects.filter(first_name='Rohan', last_name='Sharma').exists())

    def test_register_customer_invalid_data(self):
        # URL for the register_customer API
        url = reverse('register-customer')



        # Assert that the customer is not created in the database
        self.assertFalse(Customer.objects.filter(first_name='Alice', last_name='Smith').exists())



class CheckEligibilityAPITest(TestCase):
    def setUp(self):
        # Create an instance of the API client
        self.client = APIClient()

        # Set up test data (customer and loan)
        self.customer = Customer.objects.create(
            first_name='Rohan',
            last_name='Sharma',
            age=30,
            monthly_salary=5000,
            phone_number='7089652123',
            approved_limit=10000
        )
        self.loan = Loan.objects.create(
            customer_id=self.customer,
            loan_id=1,
            loan_amount=5000,
            tenure=12,
            interest_rate=10,
            monthly_repayment=500,
            emis_paid_on_time=0
        )

    def test_check_eligibility_valid_data(self):
        # URL for the check_eligibility API
        url = reverse('check_eligibility')

        # Data for a valid eligibility check
        valid_data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': 3000,
            'interest_rate': 8.5,
            'tenure': 6
        }

        # Make a POST request to the API with valid data
        response = self.client.post(url, valid_data, format='json')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response data matches the expected data
        expected_data = {
            'customer_id': self.customer.customer_id,
            'approval': False,
            'interest_rate': 8.5,
            'corrected_interest_rate': 8.5,
            'tenure': 6,
            'monthly_installment': 500  
        }

    
        
        self.assertEqual(response.data, expected_data)

    def test_check_eligibility_invalid_data(self):
        # URL for the check_eligibility API
        url = reverse('check_eligibility')

        # Data for an invalid eligibility check
        invalid_data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': 15000,
            'interest_rate': 5.0,
            'tenure': 12
        }

        # Make a POST request to the API with invalid data
        response = self.client.post(url, invalid_data, format='json')

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the response contains the expected error message
        expected_error = {'loan_amount': ['Loan amount exceeds the approved limit']}
        self.assertEqual(response.data, expected_error)





class CreateLoanAPITest(TestCase):
    def setUp(self):
        # Create an instance of the API client
        self.client = APIClient()

        # Set up test data (customer)
        self.customer = Customer.objects.create(
            first_name='Rohan',
            last_name='Sharma',
            age=30,
            monthly_salary=5000,
            phone_number='7089652123',
            approved_limit=10000
        )

    def test_create_loan_valid_data(self):
        # URL for the create_loan API
        url = reverse('create_loan')

        # Data for a valid loan creation
        valid_data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': 3000,
            'interest_rate': 8.5,
            'tenure': 6
        }

        # Make a POST request to the API with valid data
        response = self.client.post(url, valid_data, format='json')

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response data contains the loan_id
        self.assertIn('loan_id', response.data)

        # Assert that the loan is created in the database
        self.assertTrue(Loan.objects.filter(loan_id=response.data['loan_id']).exists())

    def test_create_loan_invalid_data(self):
        # URL for the create_loan API
        url = reverse('create_loan')

        # Data for an invalid loan creation (loan_amount > approved_limit)
        invalid_data = {
            'customer_id': self.customer.customer_id,
            'loan_amount': 12000,
            'interest_rate': 6.0,
            'tenure': 12
        }

        # Make a POST request to the API with invalid data
        response = self.client.post(url, invalid_data, format='json')

        # Assert that the response status code is 400 (Bad Request)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Assert that the response contains the expected error message
        expected_error = {'loan_amount': ['Loan amount exceeds the approved limit']}
        self.assertEqual(response.data, expected_error)

        # Assert that the loan is not created in the database
        self.assertFalse(Loan.objects.filter(loan_amount=12000).exists())


class ViewLoanAPITest(TestCase):
    def setUp(self):
        # Create an instance of the API client
        self.client = APIClient()

        # Set up test data (customer and loan)
        self.customer = Customer.objects.create(
            first_name='Rohan',
            last_name='Sharma',
            age=30,
            monthly_salary=5000,
            phone_number='7089652123',
            approved_limit=10000
        )
        self.loan = Loan.objects.create(
            customer_id=self.customer,
            loan_id=1,
            loan_amount=3000,
            tenure=6,
            interest_rate=8.5,
            monthly_repayment=500,
            emis_paid_on_time=0
        )

    def test_view_loan_valid_data(self):
        # URL for the view_loan API with a valid loan ID
        url = reverse('view_loan_by_loan_id', kwargs={'loan_id': self.loan.loan_id})

        # Make a GET request to the API
        response = self.client.get(url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response data matches the expected data
        expected_data = {
            'loan_id': self.loan.loan_id,
            'customer': {
                'customer_id': self.customer.customer_id,
                'first_name': self.customer.first_name,
                'last_name': self.customer.last_name,
                'phone_number': self.customer.phone_number,
                'age': self.customer.age,
            },
            'loan_amount': self.loan.loan_amount,
            'interest_rate': self.loan.interest_rate,
            'monthly_installment': self.loan.monthly_repayment,
            'tenure': self.loan.tenure,
        }
        self.assertEqual(response.data, expected_data)

    def test_view_loan_invalid_data(self):
        # URL for the view_loan API with an invalid loan ID
        url = reverse('view_loan_by_loan_id', kwargs={'loan_id': 9999})

        # Make a GET request to the API with an invalid loan ID
        response = self.client.get(url)

        # Assert that the response status code is 404 (Not Found)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert that the response contains the expected error message
        expected_error = {'error': 'Loan not found'}
        self.assertEqual(response.data, expected_error)


class ViewLoansByCustomerAPITest(TestCase):
    def setUp(self):
        # Create an instance of the API client
        self.client = APIClient()

        # Set up test data (customer and loans)
        self.customer = Customer.objects.create(
            first_name='Rohan',
            last_name='Sharma',
            age=30,
            monthly_salary=5000,
            phone_number='7089652123',
            approved_limit=10000
        )
        self.loan1 = Loan.objects.create(
            customer_id=self.customer,
            loan_id=1,
            loan_amount=3000,
            tenure=6,
            interest_rate=8.5,
            monthly_repayment=500,
            emis_paid_on_time=0
        )
        self.loan2 = Loan.objects.create(
            customer_id=self.customer,
            loan_id=2,
            loan_amount=5000,
            tenure=12,
            interest_rate=10.0,
            monthly_repayment=500,
            emis_paid_on_time=0
        )

    def test_view_loans_by_customer_valid_data(self):
        # URL for the view_loans_by_customer API with a valid customer ID
        url = reverse('view_loans_by_customer', kwargs={'customer_id': self.customer.customer_id})

        # Make a GET request to the API
        response = self.client.get(url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert that the response data contains a list of loans
        self.assertIsInstance(response.data, list)

        # Assert that the response data matches the expected data
        expected_data = [
            {
                'loan_id': self.loan1.loan_id,
                'loan_amount': self.loan1.loan_amount,
                'interest_rate': self.loan1.interest_rate,
                'monthly_installment': self.loan1.monthly_repayment,
                'repayments_left': 0  # Replace with the expected value based on your logic
            },
            {
                'loan_id': self.loan2.loan_id,
                'loan_amount': self.loan2.loan_amount,
                'interest_rate': self.loan2.interest_rate,
                'monthly_installment': self.loan2.monthly_repayment,
                'repayments_left': 0  # Replace with the expected value based on your logic
            }
        ]
        self.assertEqual(response.data, expected_data)

    def test_view_loans_by_customer_invalid_data(self):
        # URL for the view_loans_by_customer API with an invalid customer ID
        url = reverse('view_loans_by_customer', kwargs={'customer_id': 9999})

        # Make a GET request to the API with an invalid customer ID
        response = self.client.get(url)

        # Assert that the response status code is 404 (Not Found)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # Assert that the response contains the expected error message
        expected_error = {'error': 'Customer not found'}
        self.assertEqual(response.data, expected_error)
