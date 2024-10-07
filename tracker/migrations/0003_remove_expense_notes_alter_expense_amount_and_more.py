# Generated by Django 5.1.1 on 2024-10-07 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tracker', '0002_expense_notes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='expense',
            name='notes',
        ),
        migrations.AlterField(
            model_name='expense',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.CharField(choices=[('Groceries', 'Groceries'), ('Eating out', 'Eating out'), ('Transportation', 'Transportation'), ('Communication', 'Communication'), ('Housing', 'Housing'), ('Personal Care', 'Personal Care'), ('Health and Wellness', 'Health and Wellness'), ('Education', 'Education'), ('Entertainment', 'Entertainment'), ('Debt Payments', 'Debt Payments'), ('Pets', 'Pets'), ('Miscellaneous', 'Miscellaneous')], max_length=50),
        ),
    ]
