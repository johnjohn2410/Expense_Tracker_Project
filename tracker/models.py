from django.db import models

class Expense(models.Model):
    CATEGORY_CHOICES = [
        ('Groceries', 'Groceries'),
        ('Eating out', 'Eating out'),
        ('Transportation', 'Transportation'),
        ('Communication', 'Communication'),
        ('Housing', 'Housing'),
        ('Personal Care', 'Personal Care'),
        ('Health and Wellness', 'Health and Wellness'),
        ('Education', 'Education'),
        ('Entertainment', 'Entertainment'),
        ('Debt Payments', 'Debt Payments'),
        ('Pets', 'Pets'),
        ('Miscellaneous', 'Miscellaneous'),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.category} - {self.amount}"
