from django.db import models

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
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        return f"{self.category} - {self.amount}"
