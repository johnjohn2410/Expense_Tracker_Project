from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from tracker.models import Account, Category, Transaction


@pytest.mark.django_db
def test_create_basic_transaction():
    user = User.objects.create_user(username="u1", password="x")
    cat = Category.objects.create(name="Groceries", is_system=True)
    acc = Account.objects.create(name="Cash", account_type="cash", user=user)
    t = Transaction.objects.create(
        user=user,
        transaction_type="expense",
        amount=Decimal("1.23"),
        currency="USD",
        date=timezone.now().date(),
        description="Test",
        category=cat,
        account=acc,
    )
    assert t.fingerprint  # auto-generated
    assert "Test" in str(t)
