# credit_approval/urls.py
from django.urls import path
from .views import  register_customer, check_eligibility,view_loan_by_loan_id,view_loans_by_customer,create_loan

urlpatterns = [

    path('register/', register_customer, name='register-customer'),
    path('check-eligibility/', check_eligibility, name='check_eligibility'),
    path('create-loan/', create_loan, name='create_loan'),
    path('view-loan/<int:loan_id>/',view_loan_by_loan_id , name='view_loan_by_loan_id'),
    path('view-loans/<int:customer_id>/', view_loans_by_customer, name='view_loans_by_customer'),

    
    
]
