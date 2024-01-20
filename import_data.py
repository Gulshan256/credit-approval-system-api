import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ApprovalHub.settings')
import django
django.setup()
import json
from credit_approval.models import Customer, Loan

# export data form customer_data.xlsx to customer model
import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
df = pd.read_excel('customer_data.xlsx', sheet_name='Sheet1')
print("Column headings:")
print(df.columns)

for index, row in df.iterrows():
    Customer.objects.create(
        customer_id=row['Customer ID'],
        first_name=row['First Name'],
        last_name=row['Last Name'],
        age=row['Age'],
        phone_number=row['Phone Number'],
        monthly_salary=row['Monthly Salary'],
        approved_limit=row['Approved Limit'],
    )


# export data form loan_data.xlsx to loan model
    
df = pd.read_excel('loan_data.xlsx', sheet_name='Sheet1')
print("Column headings:")
print(df.columns)

for index, row in df.iterrows():
    Loan.objects.create(
        customer_id_id=row['Customer ID'],
        loan_id=row['Loan ID'],
        loan_amount=row['Loan Amount'],
        tenure=row['Tenure'],
        interest_rate=row['Interest Rate'],
        monthly_repayment=row['Monthly payment'],
        emis_paid_on_time=row['EMIs paid on Time'],
        start_date=row['Date of Approval'],
        end_date=row['End Date'],
    )




