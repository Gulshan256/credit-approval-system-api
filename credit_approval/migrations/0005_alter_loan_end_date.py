# Generated by Django 5.0.1 on 2024-01-22 18:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('credit_approval', '0004_alter_loan_start_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='loan',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
