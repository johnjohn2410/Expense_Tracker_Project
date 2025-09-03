import json
from datetime import datetime, timedelta

from django.db.models import F, Q, Sum
from django.shortcuts import render
from django.utils import timezone
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

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

from .serializers import (
    AccountSerializer,
    AttachmentSerializer,
    BudgetPeriodSerializer,
    BudgetSerializer,
    CategorySerializer,
    DashboardSerializer,
    ImportSerializer,
    RuleSerializer,
    TransactionBulkSerializer,
    TransactionSerializer,
    UserProfileSerializer,
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Custom permission to only allow owners of an object to edit it."""

    def has_object_permission(self, request, view, obj):
        # Read permissions for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for the owner
        return obj.user == request.user


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = "page_size"
    max_page_size = 100


class CategoryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing expense categories"""

    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        """Filter categories by user and include system categories"""
        return Category.objects.filter(Q(user=self.request.user) | Q(is_system=True))

    @action(detail=False, methods=["get"])
    def system_categories(self, request):
        """Get system-defined categories"""
        categories = Category.objects.filter(is_system=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def custom_categories(self, request):
        """Get user-defined categories"""
        categories = Category.objects.filter(user=request.user, is_active=True)
        serializer = self.get_serializer(categories, many=True)
        return Response(serializer.data)


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing financial accounts"""

    serializer_class = AccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "institution", "notes"]
    ordering_fields = ["name", "balance", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return Account.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def update_balance(self, request, pk=None):
        account = self.get_object()
        new_balance = request.data.get("balance")
        if new_balance is not None:
            account.balance = new_balance
            account.save()
            serializer = self.get_serializer(account)
            return Response(serializer.data)
        return Response(
            {"error": "Balance is required"}, status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get account summary with balances"""
        accounts = self.get_queryset()
        total_balance = sum(account.current_balance for account in accounts)

        summary = {
            "total_accounts": accounts.count(),
            "total_balance": total_balance,
            "accounts": AccountSerializer(accounts, many=True).data,
        }
        return Response(summary)


class TransactionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing transactions"""

    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["description", "notes", "merchant"]
    ordering_fields = ["date", "amount", "created_at"]
    ordering = ["-date"]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set user and apply categorization rules"""
        transaction = serializer.save(user=self.request.user)
        from .tasks import apply_categorization_rules

        apply_categorization_rules.delay(transaction.id)

    def apply_categorization_rules(self, transaction):
        """Apply auto-categorization rules to transaction"""
        rules = Rule.objects.filter(user=self.request.user, is_active=True).order_by(
            "-priority"
        )

        for rule in rules:
            if rule.matches_transaction(transaction):
                transaction.category = rule.category
                transaction.save()
                break

    @action(detail=False, methods=["post"])
    def bulk_create(self, request):
        """Bulk create transactions"""
        serializer = TransactionBulkSerializer(data=request.data)
        if serializer.is_valid():
            transactions_data = serializer.validated_data["transactions"]
            skip_duplicates = serializer.validated_data["skip_duplicates"]
            apply_rules = serializer.validated_data["apply_rules"]

            created_transactions = []
            skipped_count = 0

            for transaction_data in transactions_data:
                # Check for duplicates if enabled
                if skip_duplicates:
                    fingerprint = self.generate_fingerprint(
                        transaction_data, request.user
                    )
                    if Transaction.objects.filter(fingerprint=fingerprint).exists():
                        skipped_count += 1
                        continue

                transaction_data["user"] = request.user.id
                transaction_serializer = TransactionSerializer(data=transaction_data)
                if transaction_serializer.is_valid():
                    transaction = transaction_serializer.save()
                    if apply_rules:
                        self.apply_categorization_rules(transaction)
                    created_transactions.append(transaction)

            return Response(
                {
                    "created_count": len(created_transactions),
                    "skipped_count": skipped_count,
                    "transactions": TransactionSerializer(
                        created_transactions, many=True
                    ).data,
                }
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def generate_fingerprint(self, transaction_data, user):
        """Generate fingerprint for duplicate detection"""
        import hashlib

        fingerprint_data = f"{user.id}|{transaction_data.get('date')}|{transaction_data.get('amount')}|{transaction_data.get('merchant', '')}|{transaction_data.get('account')}|{transaction_data.get('import_id', '')}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()

    @action(detail=False, methods=["get"])
    def summary(self, request):
        """Get transaction summary for current month"""
        start_date = request.query_params.get("start_date")
        end_date = request.query_params.get("end_date")

        queryset = self.get_queryset()
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        summary = queryset.aggregate(
            total_income=Sum("amount", filter=Q(transaction_type="income")),
            total_expenses=Sum("amount", filter=Q(transaction_type="expense")),
            total_transfers=Sum("amount", filter=Q(transaction_type="transfer")),
        )

        return Response(summary)


class BudgetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing budgets"""

    serializer_class = BudgetSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "amount", "created_at"]
    ordering = ["name"]

    def get_queryset(self):
        return Budget.objects.filter(user=self.request.user)

    @action(detail=True, methods=["get"])
    def progress(self, request, pk=None):
        """Get budget progress details"""
        budget = self.get_object()

        progress = {
            "budget": BudgetSerializer(budget).data,
            "spent_amount": budget.spent_amount,
            "remaining_amount": budget.remaining_amount,
            "usage_percentage": budget.usage_percentage,
            "days_remaining": (budget.end_date - timezone.now().date()).days,
        }

        return Response(progress)


class BudgetPeriodViewSet(viewsets.ModelViewSet):
    """ViewSet for managing budget periods"""

    serializer_class = BudgetPeriodSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["notes"]
    ordering_fields = ["start_date", "end_date", "created_at"]
    ordering = ["-start_date"]

    def get_queryset(self):
        return BudgetPeriod.objects.filter(budget__user=self.request.user)


class RuleViewSet(viewsets.ModelViewSet):
    """ViewSet for managing auto-categorization rules"""

    serializer_class = RuleSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["pattern", "description"]
    ordering_fields = ["priority", "created_at"]
    ordering = ["-priority"]

    def get_queryset(self):
        return Rule.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def test(self, request, pk=None):
        """Test a rule against sample text"""
        rule = self.get_object()
        test_data = request.data.get("transaction_data", {})

        mock_transaction = type("MockTransaction", (), test_data)()
        matches = rule.matches_transaction(mock_transaction)

        return Response(
            {"matches": matches, "rule_pattern": rule.pattern, "test_data": test_data}
        )


class AttachmentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing file attachments"""

    serializer_class = AttachmentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["filename", "description"]
    ordering_fields = ["filename", "file_size", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Attachment.objects.filter(transaction__user=self.request.user)

    def perform_create(self, serializer):
        """Set file metadata on creation"""
        attachment = serializer.save()

        # Set file metadata
        attachment.filename = attachment.file.name.split("/")[-1]
        attachment.file_type = attachment.file.content_type
        attachment.file_size = attachment.file.size
        attachment.save()


class ImportViewSet(viewsets.ModelViewSet):
    """ViewSet for managing import history"""

    serializer_class = ImportSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["filename", "notes"]
    ordering_fields = ["created_at", "total_records"]
    ordering = ["-created_at"]

    def get_queryset(self):
        return Import.objects.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def retry(self, request, pk=None):
        import_obj = self.get_object()
        if import_obj.status == "failed":
            from .tasks import process_pending_imports

            process_pending_imports.delay(import_obj.id)
            return Response({"message": "Import retry initiated"})
        return Response(
            {"error": "Can only retry failed imports"},
            status=status.HTTP_400_BAD_REQUEST,
        )


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profiles"""

    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return UserProfile.objects.filter(user=self.request.user)

    def get_object(self):
        """Get or create user profile"""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

    @action(detail=False, methods=["get", "put", "patch"])
    def me(self, request):
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        if request.method == "GET":
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        elif request.method in ["PUT", "PATCH"]:
            serializer = self.get_serializer(
                profile, data=request.data, partial=request.method == "PATCH"
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DashboardViewSet(viewsets.ViewSet):
    """ViewSet for dashboard data"""

    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=["get"])
    def overview(self, request):
        """Get dashboard overview data"""
        user = request.user
        today = timezone.now().date()
        month_start = today.replace(day=1)

        monthly_expenses = (
            Transaction.objects.filter(
                user=user, transaction_type="expense", date__gte=month_start
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        monthly_income = (
            Transaction.objects.filter(
                user=user, transaction_type="income", date__gte=month_start
            ).aggregate(total=Sum("amount"))["total"]
            or 0
        )

        recent_transactions = Transaction.objects.filter(user=user).order_by("-date")[
            :5
        ]

        active_budgets = Budget.objects.filter(user=user, is_active=True)[:5]

        return Response(
            {
                "monthly_expenses": monthly_expenses,
                "monthly_income": monthly_income,
                "net_income": monthly_income - monthly_expenses,
                "recent_transactions": TransactionSerializer(
                    recent_transactions, many=True
                ).data,
                "active_budgets": BudgetSerializer(active_budgets, many=True).data,
            }
        )
