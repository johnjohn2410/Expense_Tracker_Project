from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from tracker.models import Account, Category, UserProfile


class Command(BaseCommand):
    help = "Set up initial data for the expense tracker"

    def handle(self, *args, **options):
        self.stdout.write("Setting up initial data...")

        # Create system categories
        system_categories = [
            {"name": "Food & Dining", "description": "Restaurants, groceries, etc."},
            {"name": "Transportation", "description": "Gas, public transit, rideshare"},
            {"name": "Shopping", "description": "Clothing, electronics, etc."},
            {"name": "Entertainment", "description": "Movies, games, hobbies"},
            {"name": "Bills & Utilities", "description": "Rent, electricity, internet"},
            {"name": "Healthcare", "description": "Medical expenses, prescriptions"},
            {"name": "Travel", "description": "Vacations, business trips"},
            {"name": "Education", "description": "Courses, books, training"},
            {"name": "Income", "description": "Salary, freelance, investments"},
            {"name": "Other", "description": "Miscellaneous expenses"},
        ]

        for cat_data in system_categories:
            category, created = Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "description": cat_data["description"],
                    "is_system": True,
                    "is_active": True,
                },
            )
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Create default account types
        default_accounts = [
            {"name": "Cash", "account_type": "cash", "balance": 0, "currency": "USD"},
            {
                "name": "Checking Account",
                "account_type": "checking",
                "balance": 0,
                "currency": "USD",
            },
            {
                "name": "Savings Account",
                "account_type": "savings",
                "balance": 0,
                "currency": "USD",
            },
            {
                "name": "Credit Card",
                "account_type": "credit",
                "balance": 0,
                "currency": "USD",
            },
        ]

        # Create accounts for existing users
        for user in User.objects.all():
            for acc_data in default_accounts:
                account, created = Account.objects.get_or_create(
                    name=acc_data["name"],
                    user=user,
                    defaults={
                        "account_type": acc_data["account_type"],
                        "balance": acc_data["balance"],
                        "currency": acc_data["currency"],
                        "is_active": True,
                    },
                )
                if created:
                    self.stdout.write(
                        f"Created account {account.name} for user {user.username}"
                    )

            # Create user profile if it doesn't exist
            profile, created = UserProfile.objects.get_or_create(user=user)
            if created:
                self.stdout.write(f"Created user profile for {user.username}")

        self.stdout.write(
            self.style.SUCCESS("Initial data setup completed successfully!")
        )
