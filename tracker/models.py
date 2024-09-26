from django.db import models

class Expense(models.Model):
    category = models.CharField(max_length=100)
    amount = models.FloatField()
    date = models.DateField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.category} - ${self.amount} on {self.date}"
