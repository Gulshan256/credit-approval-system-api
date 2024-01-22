from django.db import models



class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    age = models.IntegerField()
    phone_number = models.BigIntegerField()
    monthly_salary = models.IntegerField()
    approved_limit = models.IntegerField()
    current_debt = models.IntegerField(blank=True, null=True)

    
    # define table name
    class Meta:
        db_table = "customer"
        ordering = ['customer_id']
        
    
    
    

class Loan(models.Model):
    id=models.AutoField(primary_key=True)
    customer_id = models.ForeignKey(Customer, on_delete=models.CASCADE)
    loan_id = models.IntegerField()
    loan_amount = models.IntegerField()
    tenure = models.IntegerField()
    interest_rate = models.IntegerField()
    monthly_repayment = models.IntegerField()
    emis_paid_on_time = models.IntegerField()
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True,)

 
    class Meta:
        db_table = "loan"
        ordering = ['customer_id']

    
