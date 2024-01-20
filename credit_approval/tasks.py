# credit_approval/tasks.py
from celery import shared_task
import pandas as pd
from .models import Customer, Loan

@shared_task
def ingest_customer_data():
    # Read customer data from Excel and save to Customer model
    customer_data = pd.read_excel('ApprovalHub/customer_data.xlsx')
    Customer.objects.bulk_create([Customer(**row) for _, row in customer_data.iterrows()])

@shared_task
def ingest_loan_data():
    # Read loan data from Excel and save to Loan model
    loan_data = pd.read_excel('ApprovalHub/loan_data.xlsx') #C:\Users\kumar\Desktop\Backend Internship Assignment\ApprovalHub\loan_data.xlsx
    Loan.objects.bulk_create([Loan(**row) for _, row in loan_data.iterrows()])
