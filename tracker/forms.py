from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.utils import timezone
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
    # Override currency field to be a ChoiceField instead of CharField
    currency = forms.ChoiceField(
        choices=[
            ("", ""),  # Empty choice for floating labels
            ("USD", "USD"),
            ("EUR", "EUR"),
            ("GBP", "GBP"),
            ("CAD", "CAD"),
            ("AUD", "AUD"),
        ],
        widget=forms.Select(attrs={"class": "form-select", "required": True})
    )
    
    class Meta:
        model = Transaction
        fields = [
            "amount", "currency", "date", "description", "notes",
            "category", "account", "merchant",
        ]
        widgets = {
            "amount":     forms.NumberInput(attrs={"class": "form-control", "placeholder": " ", "required": True}),
            "date":       forms.DateInput(attrs={"type": "date", "class": "form-control", "placeholder": " ", "required": True}),
            "description":forms.TextInput(attrs={"class": "form-control", "placeholder": " ", "required": True}),
            "notes":      forms.Textarea(attrs={"class": "form-control", "placeholder": " ", "rows": 3}),
            "category":   forms.Select(attrs={"class": "form-select", "required": True}),
            "account":    forms.Select(attrs={"class": "form-select", "required": True}),
            "merchant":   forms.TextInput(attrs={"class": "form-control", "placeholder": " "}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Scope FK choices to the current user
        self.fields["account"].queryset  = Account.objects.filter(user=user)
        self.fields["category"].queryset = Category.objects.filter(
            Q(user=user) | Q(is_system=True)
        )
        

        
        # Set empty labels for selects to enable floating
        if 'category' in self.fields and hasattr(self.fields['category'], 'empty_label'):
            self.fields['category'].empty_label = ''
        if 'account' in self.fields and hasattr(self.fields['account'], 'empty_label'):
            self.fields['account'].empty_label = ''
        
        # Add empty choices for floating labels to work
        if 'category' in self.fields:
            category_choices = list(self.fields['category'].choices)
            if category_choices and category_choices[0][0] != '':
                self.fields['category'].choices = [('', '')] + list(category_choices)
        
        if 'account' in self.fields:
            account_choices = list(self.fields['account'].choices)
            if account_choices and account_choices[0][0] != '':
                self.fields['account'].choices = [('', '')] + list(account_choices)
        
        self._user = user

    def clean(self):
        cleaned_data = super().clean()
        
        # Ensure amount is positive
        amount = cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError('Amount must be greater than zero.')
        
        # Ensure date is not in the future
        date = cleaned_data.get('date')
        if date and date > timezone.now().date():
            raise forms.ValidationError('Date cannot be in the future.')
        
        return cleaned_data

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.user = self._user
        if commit:
            obj.save()
        return obj



class ExpenseForm(TransactionForm):
    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.transaction_type = "expense"
        if commit:
            obj.save()
        return obj

class IncomeForm(TransactionForm):
    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.transaction_type = "income"
        if commit:
            obj.save()
        return obj

class BudgetForm(forms.ModelForm):
    # Override currency field to be a ChoiceField
    currency = forms.ChoiceField(
        choices=[
            ("", ""),  # Empty choice for floating labels
            ("USD", "USD"),
            ("EUR", "EUR"),
            ("GBP", "GBP"),
            ("CAD", "CAD"),
            ("AUD", "AUD"),
        ],
        widget=forms.Select(attrs={"class": "form-select", "required": True})
    )
    
    # Explicit ModelMultipleChoiceField so Django knows this is M2M
    accounts = forms.ModelMultipleChoiceField(
        queryset=Account.objects.none(),
        required=False,                               # optional; user can add accounts later
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": 4})
        # ^ `multiple` is automatically added by SelectMultiple
    )

    class Meta:
        model = Budget
        fields = ["name", "amount", "currency", "period", "start_date", "end_date", "category", "accounts"]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': ' ',
                'required': True
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': ' ',
                'step': '0.01',
                'min': '0',
                'required': True
            }),
            'start_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': ' ',
                'required': True
            }),
            'end_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': ' ',
                'required': True
            }),
            'period': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
                'required': False
            }),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["accounts"].queryset = Account.objects.filter(user=user)
        self.fields["category"].queryset = Category.objects.filter(
            Q(user=user) | Q(is_system=True)
        )
        
        # Set empty labels for selects to enable floating
        if 'period' in self.fields and hasattr(self.fields['period'], 'empty_label'):
            self.fields['period'].empty_label = ''
        if 'category' in self.fields and hasattr(self.fields['category'], 'empty_label'):
            self.fields['category'].empty_label = ''
        
        # Add period choices
        self.fields["period"].choices = [
            ("", ""),  # Empty choice for floating labels
            ("monthly", "Monthly"),
            ("weekly", "Weekly"),
            ("yearly", "Yearly"),
        ]
        
        # Add empty choices for floating labels to work
        if 'category' in self.fields:
            category_choices = list(self.fields['category'].choices)
            if category_choices and category_choices[0][0] != '':
                self.fields['category'].choices = [('', '')] + list(category_choices)


