from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from tracker.models import Expense, Income, UserProfile

class DateClick(forms.DateInput):
    input_type = 'date'

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        fields = ['category', 'amount', 'date']
        widgets = {
            'category': forms.Select(choices=Expense.CATEGORY_CHOICES),
            'date': DateClick(),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError("Expense amount must be a positive number.")
        return amount

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class IncomeForm(forms.ModelForm):
    class Meta:
        model = Income
        fields = ['amount', 'date']
        widgets = {
            'date': DateClick(),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is None or amount <= 0:
            raise forms.ValidationError("Income amount must be a positive number.")
        return amount

class BudgetForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['monthly_budget']
