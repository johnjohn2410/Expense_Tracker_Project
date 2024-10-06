from django.shortcuts import render, redirect
from .models import Expense
from .forms import ExpenseForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from .forms import SignUpForm
def signup(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
        else:
            form = SignUpForm()
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
    # Update the path to the template to 'tracker/add_expense.html'
    return render(request, 'tracker/add_expense.html', {'form': form})
