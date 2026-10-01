from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(
        template_name='login.html',
        redirect_authenticated_user=True  
    ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('finance/account/delete/', views.delete_account, name='delete_account'),
    path('finance/income/add/', views.add_income, name='add_income'),
    path('finance/allocation/add/', views.add_allocation, name='add_allocation'),
    path('finance/transaction/add/', views.add_transaction, name='add_transaction'),
    path('finance/summary/<int:year>/<int:month>/', views.monthly_summary, name='monthly_summary'),
    path('finance/manage/', views.manage_finance, name='manage_finance'),
    path('finance/manage/update/', views.update_finance_data, name='update_finance_data')
]
