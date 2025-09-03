import csv
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .forms import SignUpForm, LoginForm, ExpenseForm, IncomeForm, BudgetForm
from .models import Transaction, Category, Account, Budget, UserProfile

from decimal import *

getcontext().prec = 2


# Health check endpoint
@csrf_exempt
@require_http_methods(["GET"])
def health_check(request):
    """Health check endpoint for monitoring"""
    try:
        # Check database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        # Check if we can query models
        user_count = UserProfile.objects.count()
        
        health_status = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'database': 'connected',
            'user_count': user_count,
            'version': '1.0.0'
        }
        
        return JsonResponse(health_status, status=200)
        
    except Exception as e:
        health_status = {
            'status': 'unhealthy',
            'timestamp': timezone.now().isoformat(),
            'error': str(e),
            'version': '1.0.0'
        }
        return JsonResponse(health_status, status=503)


# Custom error handlers
def custom_404(request, exception):
    """Custom 404 error handler"""
    return render(request, 'tracker/404.html', status=404)

def custom_500(request):
    """Custom 500 error handler"""
    return render(request, 'tracker/500.html', status=500)


# Home page view
def index(request):
    return render(request, 'tracker/index.html')


# Home expense view
@login_required
def home_expense(request):
    user = request.user
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    expenses = Transaction.objects.filter(
        user=user,
        transaction_type='expense',
        date__gte=month_start
    ).order_by('-date')
    
    income = Transaction.objects.filter(
        user=user,
        transaction_type='income',
        date__gte=month_start
    ).order_by('-date')
    
    total_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
    total_income = income.aggregate(total=Sum('amount'))['total'] or 0
    
    try:
        user_profile = UserProfile.objects.get(user=user)
        monthly_budget = user_profile.monthly_budget if hasattr(user_profile, 'monthly_budget') else 0
    except UserProfile.DoesNotExist:
        monthly_budget = 0
    
    budget_used_percentage = (total_expenses / monthly_budget * 100) if monthly_budget > 0 else 0
    
    context = {
        'expenses': expenses,
        'income': income,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net_income': total_income - total_expenses,
        'monthly_budget': monthly_budget,
        'budget_used_percentage': budget_used_percentage,
        'user_profile': user_profile if 'user_profile' in locals() else None,
    }
    
    return render(request, 'tracker/home_expense.html', context)


# Signup page
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('user_login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


# Activate account
def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()

        # Send welcome email
        mail_subject = 'Welcome to Expense Tracker!'
        message = f'Hi {user.username}, welcome to Expense Tracker! We are glad to have you on board. We hope that using our Expense Tracker will help make managing your finances stress free! If you have any questions feel free to reach us at expensetracker3340@gmail.com\n-John, Charles, Omar, Derek'
        send_mail(mail_subject, message, 'noreply@expensetracker.com', [user.email])

        login(request, user)
        return redirect('home_expense')
    else:
        return render(request, 'tracker/activation_invalid.html')


# Login page
def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('home_expense')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


# Logout page
def user_logout(request):
    logout(request)
    return redirect('index')


# Add expense page
@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST, user=request.user)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.transaction_type = 'expense'
            expense.save()
            messages.success(request, 'Expense added successfully!')
            return redirect('home_expense')
    else:
        form = ExpenseForm(user=request.user)
    return render(request, 'tracker/add_expense.html', {'form': form})


# Delete expense pseudo-page
@login_required
def delete_expense(request, expense_id):
    try:
        expense = Transaction.objects.get(pk=expense_id, user=request.user, transaction_type='expense')
        expense.delete()
        messages.success(request, 'Expense deleted successfully!')
    except Transaction.DoesNotExist:
        messages.error(request, 'Expense not found.')
    return redirect('home_expense')


# Add income page
@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST, user=request.user)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.transaction_type = 'income'
            income.save()
            messages.success(request, 'Income added successfully!')
            return redirect('home_expense')
    else:
        form = IncomeForm(user=request.user)
    return render(request, 'tracker/add_income.html', {'form': form})


# Export expenses to CSV
@login_required
def export_expenses(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Category', 'Amount', 'Date', 'Description'])

    expenses = Transaction.objects.filter(user=request.user, transaction_type='expense')
    for expense in expenses:
        category_name = expense.category.name if expense.category else 'Uncategorized'
        writer.writerow([category_name, expense.amount, expense.date, expense.description])

    return response


# Update budget page
@login_required
def update_budget(request):
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    
    if request.method == 'POST':
        form = BudgetForm(request.POST, user=request.user)
        if form.is_valid():
            budget = form.save(commit=False)
            budget.user = request.user
            budget.save()
            form.save_m2m()
            messages.success(request, 'Budget updated successfully!')
            return redirect('home_expense')
    else:
        form = BudgetForm(user=request.user)
    
    return render(request, 'tracker/update_budget.html', {'form': form})
