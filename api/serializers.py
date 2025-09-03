from django.contrib.auth.models import User
from rest_framework import serializers

from tracker.models import (
    Account,
    Attachment,
    Budget,
    BudgetPeriod,
    Category,
    Import,
    Rule,
    Transaction,
    UserProfile,
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AccountSerializer(serializers.ModelSerializer):
    current_balance = serializers.SerializerMethodField()

    class Meta:
        model = Account
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_current_balance(self, obj):
        return obj.balance


class TransactionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    account_name = serializers.CharField(source="account.name", read_only=True)

    class Meta:
        model = Transaction
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at", "fingerprint"]


class BudgetSerializer(serializers.ModelSerializer):
    spent_amount = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    usage_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_spent_amount(self, obj):
        return obj.spent_amount

    def get_remaining_amount(self, obj):
        return obj.remaining_amount

    def get_usage_percentage(self, obj):
        return obj.usage_percentage


class BudgetPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = BudgetPeriod
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class RuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rule
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class AttachmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attachment
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class ImportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Import
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = UserProfile
        fields = "__all__"
        read_only_fields = ["id", "created_at", "updated_at"]


class DashboardSerializer(serializers.Serializer):
    monthly_expenses = serializers.DecimalField(max_digits=10, decimal_places=2)
    monthly_income = serializers.DecimalField(max_digits=10, decimal_places=2)
    net_income = serializers.DecimalField(max_digits=10, decimal_places=2)
    recent_transactions = TransactionSerializer(many=True)
    active_budgets = BudgetSerializer(many=True)


class TransactionBulkSerializer(serializers.Serializer):
    transactions = TransactionSerializer(many=True)

    def create(self, validated_data):
        user = self.context["user"]
        transactions_data = validated_data["transactions"]
        created_transactions = []

        for transaction_data in transactions_data:
            transaction_data["user"] = user
            transaction = Transaction.objects.create(**transaction_data)
            created_transactions.append(transaction)

        return created_transactions
