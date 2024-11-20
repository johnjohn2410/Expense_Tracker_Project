import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from django.utils.text import normalize_newlines
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.urls import reverse
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.models import User
from .models import Expense, Income, UserProfile
from .forms import SignUpForm, LoginForm, ExpenseForm, IncomeForm, BudgetForm
# import matplotlib.pyplot as plt
# from io import BytesIO
# import base64

from decimal import *

getcontext().prec = 2


# Home page view
def index(request):
    return render(request, 'tracker/index.html', {})


# Home expense view
def home_expense(request):
    if request.user.is_authenticated:
        # Get selected categories from request
        category_filters = request.GET.getlist('category')

        if category_filters:
            # If categories are selected, filter by those categories
            expenses = Expense.objects.filter(category__in=category_filters, user=request.user)
        else:
            # Otherwise, get all expenses
            expenses = Expense.objects.filter(user=request.user)

        # Calculate total expenses and filtered expenses
        total_expenses = Expense.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
        filtered_expenses = expenses.aggregate(total=Sum('amount'))['total'] or 0
        total_income = Income.objects.filter(user=request.user).aggregate(total=Sum('amount'))['total'] or 0
        remaining_balance = total_income - total_expenses

        # Retrieve user's monthly budget
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        budget = user_profile.monthly_budget
        budget_check = budget * 3 / 4

        # Generate warnings based on budget and spending
        if budget == 0:
            warning = "Warning: Your budget is at 0, please update it"
        elif total_expenses > budget:
            warning = "Warning: You are overspending this month!"
        elif budget > total_expenses > budget_check:
            warning = "Warning: You are nearing your budget limit for this month!"
        else:
            warning = None

        # Budget used percentage calculation
        budget_used_color = 0
        if budget <= 0:
            budget_used_amount = None
        else:
            budget_used_amount = int((total_expenses / budget) * 100)
            if budget_used_amount < 75:
                budget_used_color = 0  # Good (green)
            elif 100 > budget_used_amount > 75:
                budget_used_color = 1  # Warning (orange)
            else:
                budget_used_color = 2  # Bad (red)

        categories = Expense.objects.values_list('category', flat=True).distinct()
        return render(request, 'tracker/home_expense.html', {
            'expenses': expenses,
            'categories': categories,
            'category_filters': category_filters,
            'total_expenses': total_expenses,
            'filtered_expenses': filtered_expenses,
            'total_income': total_income,
            'remaining_balance': remaining_balance,
            'budget': budget,
            'budget_used_amount': budget_used_amount,
            'budget_used_color': budget_used_color,
            'warning': warning,
        })
    else:
        categories = Expense.objects.none()
        return redirect('index')


# Signup page
def user_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # Deactivate account until email confirmation
            user.save()

            # Email verification
            current_site = get_current_site(request)
            mail_subject = 'Activate your Expense Tracker account'
            message = render_to_string('tracker/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            send_mail(
                mail_subject,
                '',
                'noreply@expensetracker.com',
                [to_email],
                html_message=message,
            )

            return render(request, 'tracker/email_verification_sent.html')
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
def add_expense(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = ExpenseForm(request.POST)
            if form.is_valid():
                expense = form.save(commit=False)
                expense.user = request.user
                expense.save()
                return redirect('home_expense')
        else:
            form = ExpenseForm()
        return render(request, 'tracker/add_expense.html', {'form': form})
    else:
        return redirect('index')


# Delete expense pseudo-page
def delete_expense(request, expense_id):
    if request.user.is_authenticated:
        try:
            expense = Expense.objects.get(pk=expense_id, user=request.user)
            expense.delete()
        except Expense.DoesNotExist:
            pass  # Optionally handle the case where the expense does not exist.
        return redirect('home_expense')
    else:
        return redirect('index')


# Add income page
def add_income(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = IncomeForm(request.POST)
            if form.is_valid():
                income = form.save(commit=False)
                income.user = request.user
                income.save()
                return redirect('home_expense')
        else:
            form = IncomeForm()
        return render(request, 'tracker/add_income.html', {'form': form})
    else:
        return redirect('index')


# Export expenses to CSV
def export_expenses(request):
    if request.user.is_authenticated:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

        writer = csv.writer(response)
        writer.writerow(['Category', 'Amount', 'Date'])

        expenses = Expense.objects.filter(user=request.user)
        for expense in expenses:
            writer.writerow([expense.category, expense.amount, expense.date])

        return response
    else:
        return redirect('index')


# Update budget page
def update_budget(request):
    if request.user.is_authenticated:
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            form = BudgetForm(request.POST, instance=user_profile)
            if form.is_valid():
                form.save()
                return redirect('home_expense')
        else:
            form = BudgetForm(instance=user_profile)
        return render(request, 'tracker/update_budget.html', {'form': form})
    else:
        return redirect('index')
