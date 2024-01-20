# Create your tests here.
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from .models import Customer, Loan
from django.urls import reverse




class RegisterCustomerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_customer_success(self):
        url = '/api/register-customer/'
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 30,
            'phone_number': '1234567890',
            'monthly_salary': 5000
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add additional assertions to check the response data

    def test_register_customer_invalid_data(self):
        url = '/api/register-customer/'
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 'thirty',
            'phone_number': '1234567890',
            'monthly_salary': 5000
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Add additional assertions to check the response data

    def test_register_customer_method_not_allowed(self):
        url = '/api/register-customer/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # Add additional assertions to check the response data




class RegisterCustomerTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_customer_success(self):
        url = '/api/register-customer/'
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 30,
            'phone_number': '1234567890',
            'monthly_salary': 5000
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add additional assertions to check the response data

    def test_register_customer_invalid_data(self):
        url = '/api/register-customer/'
        data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'age': 'thirty',
            'phone_number': '1234567890',
            'monthly_salary': 5000
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Add additional assertions to check the response data

    def test_register_customer_method_not_allowed(self):
        url = '/api/register-customer/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # Add additional assertions to check the response data

    def test_check_eligibility_success(self):
        url = '/api/check-eligibility/'
        data = {
            'customer_id': 1,
            'loan_amount': 10000,
            'tenure': 12,
            'interest_rate': 5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add additional assertions to check the response data

    def test_check_eligibility_invalid_data(self):
        url = '/api/check-eligibility/'
        data = {
            'customer_id': 1,
            'loan_amount': 'ten thousand',
            'tenure': 12,
            'interest_rate': 5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Add additional assertions to check the response data

    def test_check_eligibility_method_not_allowed(self):
        url = '/api/check-eligibility/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        # Add additional assertions to check the response datafrom django.test import TestCase


class ViewLoanDetailsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_view_loan_details_success(self):
        loan = Loan.objects.create(amount=10000, interest_rate=5, tenure=12)
        url = reverse('view_loan_details', args=[loan.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Add additional assertions to check the response data

    def test_view_loan_details_not_found(self):
        url = reverse('view_loan_details', args=[999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        # Add additional assertions to check the response data