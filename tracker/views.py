import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.db.models import Sum
from django.utils.text import normalize_newlines

from .models import Expense, Income, UserProfile
from .forms import SignUpForm, LoginForm, ExpenseForm, IncomeForm, BudgetForm
# import matplotlib.pyplot as plt
# from io import BytesIO
# import base64

# Home page
def index(request):
    return render(request, 'tracker/index.html', {})

def home_expense(request):
    if request.user.is_authenticated:
        category = request.GET.get('category')
        if category:
            expenses = Expense.objects.filter(category=category, user=request.user)
        else:
            expenses = Expense.objects.filter(user=request.user)

        total_expenses = sum(exp.amount for exp in expenses)
        total_income = sum(inc.amount for inc in Income.objects.filter(user=request.user))
        remaining_balance = total_income - total_expenses

        # Retrieve user's monthly budget
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        budget = user_profile.monthly_budget
        # Variable for 75% of set budget, used for usage warning
        budget_check = budget * 3/4
        # Warning messages about user's budget
        if budget == 0:
            warning = "Warning: Your budget is at 0, please update it"
        elif total_expenses > budget:
            warning = "Warning: You are overspending this month!"
        elif budget > total_expenses > budget_check:
            warning = "Warning: You are nearing your budget limit for this month!"
        else:
            warning = None

        # Budget Used Percentage
        # Error-Checking prevents usage of variable if budget is invalid, dividing by zero is bad
        budget_used_color = 0
        if budget <= 0:
            budget_used_amount = None
        else:
            budget_used_amount = int((total_expenses / budget) * 100)
            # Variable for determining color display in html
            if budget_used_amount < 75:
                budget_used_color = 0 #good = green
            elif 100 > budget_used_amount > 75:
                budget_used_color = 1 #warning = orange
            else:
                budget_used_color = 2 #bad = red

        # Get categories and prepare data for pie chart
        # category_totals = expenses.values('category').annotate(total=Sum('amount'))
        # labels = [item['category'] for item in category_totals if item['total'] > 0]
        # sizes = [item['total'] for item in category_totals if item['total'] > 0]

        # if sizes:  # Only create a pie chart if there are valid positive values
        #     # Create the pie chart
        #     plt.switch_backend('Agg')  # Use Agg backend for non-GUI environments
        #     fig, ax = plt.subplots(figsize=(6, 6))
        #     ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        #     ax.axis('equal')  # Equal aspect ratio ensures the pie is drawn as a circle.

        #     # Save the chart to a BytesIO buffer
        #     buf = BytesIO()
        #     plt.savefig(buf, format='png')
        #     buf.seek(0)
        #     encoded_image = base64.b64encode(buf.read()).decode('utf-8')
        #     buf.close()
        # else:
        #     encoded_image = None

        encoded_image = None  # Make sure there's a default for 'encoded_image'

        categories = Expense.objects.values_list('category', flat=True).distinct()
        return render(request, 'tracker/home_expense.html', {
            'expenses': expenses,
            'categories': categories,
            'total_expenses': total_expenses,
            'total_income': total_income,
            'remaining_balance': remaining_balance,
            'budget': budget,
            'budget_used_amount': budget_used_amount,
            'budget_used_color': budget_used_color,
            'warning': warning,
            'pie_chart': encoded_image,  # Set this to None to avoid errors in templates
        })
    else:
        return redirect('index')

# Signup page
def user_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})

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
