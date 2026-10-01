import json

from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.http import JsonResponse
from django.utils import timezone
from .forms import CustomUserCreationForm 
from .models import IncomePool, BudgetAllocation, Transaction, InvestmentOption
from datetime import date


@login_required
def index(request):
    today = date.today()
    
    current_pool = IncomePool.objects.filter(
        user=request.user, 
        month_year__year=today.year, 
        month_year__month=today.month
    ).first()
    
    return render(request, 'index.html', {
        'current_pool': current_pool,
        'current_month': today.strftime('%B %Y')
    })


def register(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome to your financial dashboard, {user.username}!")
            return redirect('index')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field.title()}: {error}")
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'register.html', {'form': form})


@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request) 
        user.delete()    
        
        return JsonResponse({
            'status': 'success',
            'redirect_url': '/login/?deleted=true'
        })
        
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@login_required
def add_income(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            amount = data.get('amount')
            source = data.get('source', 'Salary')
            today = date.today()
            
            pool, created = IncomePool.objects.update_or_create(
                user=request.user,
                month_year__year=today.year,
                month_year__month=today.month,
                defaults={
                    'total_amount': amount,
                    'source': source,
                    'month_year': date(today.year, today.month, 1)
                }
            )
            return JsonResponse({'status': 'success', 'message': 'Income pool saved!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)


@login_required
def add_allocation(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            today = date.today()
            
            pool = IncomePool.objects.filter(
                user=request.user, 
                month_year__year=today.year, 
                month_year__month=today.month
            ).first()
            
            if not pool:
                return JsonResponse({'status': 'error', 'message': 'No income pool initialized first.'}, status=400)
            
            BudgetAllocation.objects.create(
                pool=pool,
                category=data['category'],
                description=data['description'],
                amount=data['amount']
            )
            return JsonResponse({'status': 'success', 'message': 'Allocation saved!'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'message': 'POST required'}, status=405)


@login_required
def monthly_summary(request, year, month):
    user = request.user
    
    pool = IncomePool.objects.filter(user=user, month_year__year=year, month_year__month=month).first()
    total_income = pool.total_amount if pool else 0

    allocations = BudgetAllocation.objects.filter(pool=pool) if pool else []
    budget_summary = {}
    for alloc in allocations:
        budget_summary[alloc.description] = {
            'allocated': float(alloc.amount),
            'spent': 0.0,
            'category_type': alloc.category
        }

    all_user_transactions = Transaction.objects.filter(user=user)
    
    transactions = []
    for tx in all_user_transactions:
        try:
            tx_date = tx.date if hasattr(tx.date, 'year') else datetime.strptime(str(tx.date).split()[0], "%Y-%m-%d")
            if tx_date.year == int(year) and tx_date.month == int(month):
                transactions.append(tx)
        except Exception:
            continue 

    total_needs = sum(float(tx.amount) for tx in transactions if tx.category == 'EXPENSE')
    total_wants = sum(float(tx.amount) for tx in transactions if tx.category == 'WANT')
    total_savings = sum(float(tx.amount) for tx in transactions if tx.category == 'SAVING')

    for tx in transactions:
        desc_name = tx.description
        spent_amt = float(tx.amount)
        
        if desc_name in budget_summary:
            budget_summary[desc_name]['spent'] += spent_amt
        else:
            budget_summary[desc_name] = {
                'allocated': 0.0, 
                'spent': spent_amt,
                'category_type': tx.category
            }

    recent_transactions = []
    sorted_txs = sorted(transactions, key=lambda x: getattr(x, 'id', 0), reverse=True)[:10]
    
    for tx in sorted_txs:
        if hasattr(tx.date, 'strftime'):
            local_time = timezone.localtime(tx.date)
            time_str = local_time.strftime('%d %b, %I:%M %p')
        else:
            time_str = str(tx.date)
            
        recent_transactions.append({
            'description': tx.description,
            'category': tx.category,
            'amount': float(tx.amount),
            'action_time': time_str 
        })

    unallocated_cash = float(total_income) - sum(float(alloc.amount) for alloc in allocations)

    return JsonResponse({
        'total_income': float(total_income),
        'total_actual_spent': float(total_needs + total_wants),
        'total_actual_saved': float(total_savings),
        'total_unallocated': max(0.0, unallocated_cash),
        'category_comparison': budget_summary,
        'recent_transactions': recent_transactions
    })


@login_required
def add_transaction(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            today = date.today()
            
            envelope = BudgetAllocation.objects.filter(
                pool__user=request.user,
                pool__month_year__year=today.year,
                pool__month_year__month=today.month,
                description=data['category'] 
            ).first()
            
            inferred_category = envelope.category if envelope else 'EXPENSE'
            
            transaction = Transaction.objects.create(
                user=request.user,
                amount=data['amount'],
                category=inferred_category,
                description=data['category']
            )
            
            return JsonResponse({
                'status': 'success',
                'message': f"Recorded KES {transaction.amount} under your {data['category']} envelope!"
            })
        except KeyError as e:
            return JsonResponse({'status': 'error', 'message': f'Missing field: {str(e)}'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)


@login_required
def manage_finance(request):
    today = date.today()
    
    pool = IncomePool.objects.filter(user=request.user, month_year__year=today.year, month_year__month=today.month).first()
    allocations = BudgetAllocation.objects.filter(pool=pool) if pool else []
    
    all_user_transactions = Transaction.objects.filter(user=request.user)
    
    current_month_transactions = []
    for tx in all_user_transactions:
        try:
            tx_date = tx.date if hasattr(tx.date, 'year') else datetime.strptime(str(tx.date).split()[0], "%Y-%m-%d")
            if tx_date.year == today.year and tx_date.month == today.month:
                
                if hasattr(tx.date, 'hour'): 
                    tx.local_time_display = timezone.localtime(tx.date).strftime('%d %b, %I:%M %p')
                else:
                    tx.local_time_display = tx_date.strftime('%d %b')
                
                current_month_transactions.append(tx)
        except Exception:
            continue 

    current_month_transactions.sort(key=lambda x: getattr(x, 'id', 0), reverse=True)
    
    return render(request, 'manage_finance.html', {
        'pool': pool,
        'allocations': allocations,
        'transactions': current_month_transactions 
    })


@login_required
def update_finance_data(request):
    if request.method == 'POST':
        today = date.today()
        
        delete_tx_id = request.POST.get('delete_transaction_id')
        if delete_tx_id:
            Transaction.objects.filter(id=delete_tx_id, user=request.user).delete()
            messages.success(request, "Transaction permanently removed from ledger.")
            return redirect('manage_finance')

        delete_alloc_id = request.POST.get('delete_allocation_id')
        if delete_alloc_id:
            BudgetAllocation.objects.filter(id=delete_alloc_id, pool__user=request.user).delete()
            messages.success(request, "Envelope allocation permanently removed.")
            return redirect('manage_finance') 

        pool_id = request.POST.get('pool_id')
        if pool_id:
            pool = IncomePool.objects.filter(id=pool_id, user=request.user).first()
            if pool:
                pool.total_amount = request.POST.get('pool_amount')
                pool.source = request.POST.get('pool_source')
                pool.save()

        for key, value in request.POST.items():
            if key.startswith('alloc_amount_'):
                alloc_id = key.replace('alloc_amount_', '')
                BudgetAllocation.objects.filter(id=alloc_id, pool__user=request.user).update(amount=value)
                
            elif key.startswith('tx_amount_'):
                tx_id = key.replace('tx_amount_', '')
                desc_value = request.POST.get(f'tx_desc_{tx_id}')
                Transaction.objects.filter(id=tx_id, user=request.user).update(
                    amount=value,
                    description=desc_value
                )
                
        messages.success(request, "Financial ledger metrics updated successfully!")
        return redirect('manage_finance')
        
    return redirect('index')
