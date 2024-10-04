from django.shortcuts import render, redirect
from .models import Expense
from .forms import ExpenseForm

# Display all expenses
def index(request):
    expenses = Expense.objects.all()
    # Update the path to the template to 'tracker/index.html'
    return render(request, 'tracker/index.html', {'expenses': expenses})


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
