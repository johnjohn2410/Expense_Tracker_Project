from django.shortcuts import render, redirect
from .models import Expense
from .forms import ExpenseForm, SignUpForm  # Make sure SignUpForm is imported
from django.contrib.auth import login


# Signup view
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = SignUpForm()  # This should be in the 'else' block, not inside 'if form.is_valid()'
    return render(request, 'registration/signup.html', {'form': form})


# Display all expenses
def index(request):
    category = request.GET.get('category')
    if category:
        expenses = Expense.objects.filter(category=category)
    else:
        expenses = Expense.objects.all()

    categories = Expense.objects.values_list('category', flat=True).distinct()
    return render(request, 'tracker/index.html', {'expenses': expenses, 'categories': categories})


# Add a new expense
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = ExpenseForm()
    return render(request, 'tracker/add_expense.html', {'form': form})
