from django.db import models
from django.contrib.auth.models import User

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Communication', 'Communication'),
        ('Childcare', 'Childcare'),
        ('Dining Out', 'Dining Out'),
        ('Education', 'Education'),
        ('Entertainment', 'Entertainment'),
        ('Gas', 'Gas'),
        ('Groceries', 'Groceries'),
        ('Housing', 'Housing'),
        ('Maintenance', 'Maintenance'),
        ('Medical', 'Medical'),
        ('Office Supplies', 'Office Supplies'),
        ('Personal Care', 'Personal Care'),
        ('Pets', 'Pets'),
        ('Recurring Expense', 'Recurring Expense'),
        ('Transportation', 'Transportation'),
        ('Travel', 'Travel'),
        ('Utilities', 'Utilities'),
        ('Miscellaneous', 'Miscellaneous'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link each expense to a user

    def __str__(self):
        return f"{self.category} - {self.amount}"

class Income(models.Model):
    amount = models.DecimalField(max_digits=11, decimal_places=2)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Link income to a user

    def __str__(self):
        return f"Income: {self.amount} on {self.date}"

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_budget = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.user.username}'s profile"
