from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from .models import Transaction, Category, Account, Budget

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=False, widget=forms.EmailInput(
        attrs={"class": "form-control", "placeholder": " ", "autocomplete": "email"}))
    username = forms.CharField(widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": " ", "autocomplete": "username"}))
    password1 = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": " ", "autocomplete": "new-password"}))
    password2 = forms.CharField(widget=forms.PasswordInput(
        attrs={"class": "form-control", "placeholder": " ", "autocomplete": "new-password"}))

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': ' ',
        'autocomplete': 'username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': ' ',
        'autocomplete': 'current-password'
    }))

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'amount', 'currency', 'date', 'description', 'notes', 'category', 'account', 'merchant']
        widgets = {
            'transaction_type': forms.HiddenInput(),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': ' ',
                'step': '0.01',
                'min': '0'
            }),
            'currency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' ',
                'maxlength': '3'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': ' '
            }),
            'description': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' '
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': ' ',
                'rows': 3
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'account': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'merchant': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' '
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set empty labels for selects to enable floating
        if 'category' in self.fields and hasattr(self.fields['category'], 'empty_label'):
            self.fields['category'].empty_label = ''
        if 'account' in self.fields and hasattr(self.fields['account'], 'empty_label'):
            self.fields['account'].empty_label = ''
        
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(is_system=True)
            )
            self.fields['account'].queryset = Account.objects.filter(user=user)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        return amount

class ExpenseForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = ['transaction_type', 'amount', 'currency', 'date', 'description', 'notes', 'category', 'account', 'merchant']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].initial = 'expense'
        self.fields['transaction_type'].widget = forms.HiddenInput()

class IncomeForm(TransactionForm):
    class Meta(TransactionForm.Meta):
        fields = ['transaction_type', 'amount', 'currency', 'date', 'description', 'notes', 'category', 'account', 'merchant']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['transaction_type'].initial = 'income'
        self.fields['transaction_type'].widget = forms.HiddenInput()

class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = ['name', 'amount', 'currency', 'period', 'start_date', 'end_date', 'category', 'accounts']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' '
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': ' ',
                'step': '0.01',
                'min': '0'
            }),
            'currency': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' ',
                'maxlength': '3'
            }),
            'period': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': ' '
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': ' '
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'accounts': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Set empty labels for selects to enable floating
        if 'period' in self.fields and hasattr(self.fields['period'], 'empty_label'):
            self.fields['period'].empty_label = ''
        if 'category' in self.fields and hasattr(self.fields['category'], 'empty_label'):
            self.fields['category'].empty_label = ''
        if 'accounts' in self.fields and hasattr(self.fields['accounts'], 'empty_label'):
            self.fields['accounts'].empty_label = ''
        
        if user:
            self.fields['category'].queryset = Category.objects.filter(
                Q(user=user) | Q(is_system=True)
            )
            self.fields['accounts'].queryset = Account.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date >= end_date:
            raise forms.ValidationError('Start date must be before end date.')
        
        return cleaned_data
