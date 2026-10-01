from django.contrib import admin

from .models import Transaction, IncomePool, BudgetAllocation, InvestmentOption, User

# Register your models here.
admin.site.register(Transaction)
admin.site.register(IncomePool)
admin.site.register(BudgetAllocation)
admin.site.register(InvestmentOption)
admin.site.register(User)
