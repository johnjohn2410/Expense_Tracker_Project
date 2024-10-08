from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import SignUpForm, LoginForm  # Ensure correct casing here
from .models import Expense
from .forms import ExpenseForm

# Home page
def index(request):
    category = request.GET.get('category')
    if category:
        expenses = Expense.objects.filter(category=category)
    else:
        expenses = Expense.objects.all()
    categories = Expense.objects.values_list('category', flat=True).distinct()
    return render(request, 'tracker/index.html', {'expenses': expenses, 'categories': categories})

# Signup page
def user_signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)  # Match the form name here
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignUpForm()  # Match the form name here
    return render(request, 'registration/signup.html', {'form': form})  # Update the path here

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
                return redirect('index')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})

# Logout page
def user_logout(request):
    logout(request)
    return redirect('login')

# Add expense page
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ExpenseForm()
    return render(request, 'tracker/add_expense.html', {'form': form})
