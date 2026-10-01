from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date

# Create your models here.

# Help our evalulating program to know which kind of risk taker the user is 
# This way the program can recommend the best investment option to the user
class User(AbstractUser):
    RISK_CHOICES = [
        ('LOW', 'Low Risk (e.g., M-Akiba, CBK Treasury Bills, Fixed Deposit)'),
        ('MED', 'Medium Risk (e.g., Money Market Funds, Balanced Funds)'),
        ('HIGH', 'High Risk (e.g., NSE Stocks, Real Estate Trusts, Crypto)'),
    ]
    risk_tolerance = models.CharField(max_length=4, choices=RISK_CHOICES, default='MED')
    preferred_currency = models.CharField(max_length=3, default='KES')


class IncomePool(models.Model):
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    source = models.CharField(max_length=100, default="Salary", blank=True)
    month_year = models.DateField(default=date.today, help_text="The month this pool belongs to")

    class Meta:
        unique_together = ('user', 'month_year')

# Only shows which amt goes to either savings, expenses and wants
class BudgetAllocation(models.Model):

    TYPE_CHOICES = [
        ('EXPENSE', 'Need / Core Expense'),
        ('WANT', 'Want / Lifestyle'),
        ('SAVING', 'Saving / Investment Contribution'),
    ]

    pool = models.ForeignKey(IncomePool, on_delete=models.CASCADE, related_name='allocations')
    category = models.CharField(max_length=7, choices=TYPE_CHOICES)
    description = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=12, decimal_places=2) 

    class Meta:
        unique_together = ('pool', 'category')


# Shows in detail where each specific amt has gone
class Transaction(models.Model):
    TYPE_CHOICES = [
        ('EXPENSE', 'Need / Core Expense'),
        ('WANT', 'Want / Lifestyle'),
        ('SAVING', 'Saving / Investment Contribution'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    category = models.CharField(max_length=7, choices=TYPE_CHOICES)
    description = models.CharField(max_length=50)
    date = models.DateTimeField(auto_now_add=True)



class InvestmentOption(models.Model):
    name = models.CharField(max_length=100)
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    risk_level = models.CharField(max_length=4, choices=User.RISK_CHOICES)
    description = models.TextField()
