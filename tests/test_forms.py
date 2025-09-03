from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from tracker.forms import BudgetForm, ExpenseForm
from tracker.models import Account, Category


@pytest.mark.django_db
def test_expense_form_is_valid():
    user = User.objects.create_user(username="u2", password="x")
    acc = Account.objects.create(name="Cash", account_type="cash", user=user)
    cat = Category.objects.create(name="Dining Out", is_system=True)

    form = ExpenseForm(
        user,
        data={
            "amount": "10.00",
            "currency": "USD",
            "date": str(timezone.now().date()),
            "description": "coffee",
            "notes": "",
            "category": cat.id,
            "account": acc.id,
            "merchant": "Cafe",
        },
    )
    assert form.is_valid(), form.errors
    obj = form.save()
    assert obj.transaction_type == "expense"


@pytest.mark.django_db
def test_budget_form_is_valid_without_accounts():
    user = User.objects.create_user(username="u3", password="x")
    cat = Category.objects.create(name="Utilities", is_system=True)

    form = BudgetForm(
        user,
        data={
            "name": "Monthly Utilities",
            "amount": "100.00",
            "currency": "USD",
            "period": "monthly",
            "start_date": "2025-01-01",
            "end_date": "2025-01-31",
            "category": cat.id,
            "accounts": [],  # ManyToMany can be empty; we made it optional
        },
    )
    assert form.is_valid(), form.errors
