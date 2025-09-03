from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid


class TimestampedModel(models.Model):
    """Abstract base model with created_at and updated_at fields"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """Abstract base model with soft delete functionality"""
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
    
    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()
    
    def hard_delete(self, using=None, keep_parents=False):
        super().delete(using, keep_parents)


class Category(models.Model):
    """Expense categories with system and custom support"""
    SYSTEM_CATEGORIES = [
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
    
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    color = models.CharField(max_length=7, default='#3B82F6')  # Hex color
    is_system = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    
    class Meta:
        verbose_name_plural = 'Categories'
        unique_together = ['name', 'user']
    
    def __str__(self):
        return self.name


class Account(models.Model):
    """Financial accounts (bank, credit card, cash, etc.)"""
    ACCOUNT_TYPES = [
        ('checking', 'Checking Account'),
        ('savings', 'Savings Account'),
        ('credit_card', 'Credit Card'),
        ('cash', 'Cash'),
        ('investment', 'Investment Account'),
        ('loan', 'Loan'),
        ('other', 'Other'),
    ]
    
    name = models.CharField(max_length=100)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES)
    balance = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    institution = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['name', 'user']
    
    def __str__(self):
        return f"{self.name} ({self.get_account_type_display()})"


class Transaction(TimestampedModel, SoftDeleteModel):
    """Enhanced transaction model supporting both expenses and income"""
    TRANSACTION_TYPES = [
        ('expense', 'Expense'),
        ('income', 'Income'),
        ('transfer', 'Transfer'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    date = models.DateField()
    description = models.CharField(max_length=200)
    notes = models.TextField(blank=True)
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    transfer_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True, related_name='transfer_transactions')
    
    # Metadata
    merchant = models.CharField(max_length=200, blank=True)
    location = models.CharField(max_length=200, blank=True)
    tags = models.JSONField(default=list, blank=True)
    
    # Import tracking
    import_source = models.CharField(max_length=100, blank=True)
    import_id = models.CharField(max_length=100, blank=True)
    fingerprint = models.CharField(max_length=64, blank=True)  # For deduplication
    
    # Recurring transaction support
    is_recurring = models.BooleanField(default=False)
    recurring_pattern = models.JSONField(default=dict, blank=True)
    next_occurrence = models.DateField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['user', 'category']),
            models.Index(fields=['user', 'account']),
            models.Index(fields=['fingerprint']),
        ]
    
    def __str__(self):
        return f"{self.description} - {self.amount} {self.currency}"
    
    def save(self, *args, **kwargs):
        if not self.fingerprint:
            self.fingerprint = self.generate_fingerprint()
        super().save(*args, **kwargs)
    
    def generate_fingerprint(self):
        """Generate a unique fingerprint for deduplication"""
        import hashlib
        fingerprint_data = f"{self.user.id}|{self.date}|{self.amount}|{self.merchant}|{self.account.id}|{self.import_id}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()


class Budget(TimestampedModel):
    """Budget management with periods and rollover support"""
    BUDGET_PERIODS = [
        ('monthly', 'Monthly'),
        ('weekly', 'Weekly'),
        ('yearly', 'Yearly'),
    ]
    
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    period = models.CharField(max_length=20, choices=BUDGET_PERIODS, default='monthly')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    allow_rollover = models.BooleanField(default=False)
    rollover_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    accounts = models.ManyToManyField(Account, blank=True)
    
    class Meta:
        unique_together = ['name', 'user', 'period']
    
    def __str__(self):
        return f"{self.name} - {self.amount} {self.currency} ({self.get_period_display()})"
    
    @property
    def spent_amount(self):
        """Calculate total spent in this budget period"""
        return Transaction.objects.filter(
            user=self.user,
            category=self.category,
            date__gte=self.start_date,
            date__lte=self.end_date,
            transaction_type='expense',
            is_deleted=False
        ).aggregate(total=models.Sum('amount'))['total'] or 0
    
    @property
    def remaining_amount(self):
        """Calculate remaining budget amount"""
        return self.amount - self.spent_amount
    
    @property
    def usage_percentage(self):
        """Calculate budget usage percentage"""
        if self.amount <= 0:
            return 0
        return min(100, (self.spent_amount / self.amount) * 100)


class BudgetPeriod(TimestampedModel):
    """Individual budget periods for tracking and rollover"""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='periods')
    start_date = models.DateField()
    end_date = models.DateField()
    allocated_amount = models.DecimalField(max_digits=15, decimal_places=2)
    spent_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    rollover_from_previous = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    
    class Meta:
        unique_together = ['budget', 'start_date']
    
    def __str__(self):
        return f"{self.budget.name} - {self.start_date} to {self.end_date}"


class Rule(TimestampedModel):
    """Auto-categorization rules"""
    RULE_TYPES = [
        ('contains', 'Contains'),
        ('regex', 'Regular Expression'),
        ('exact', 'Exact Match'),
        ('amount_range', 'Amount Range'),
    ]
    
    name = models.CharField(max_length=100)
    rule_type = models.CharField(max_length=20, choices=RULE_TYPES)
    pattern = models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    priority = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    # Relationships
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-priority', 'name']
        unique_together = ['name', 'user']
    
    def __str__(self):
        return f"{self.name} → {self.category.name}"
    
    def matches_transaction(self, transaction):
        """Check if this rule matches a transaction"""
        if not self.is_active:
            return False
        
        if self.rule_type == 'contains':
            return (self.pattern.lower() in transaction.description.lower() or 
                   self.pattern.lower() in transaction.merchant.lower())
        elif self.rule_type == 'regex':
            import re
            try:
                return (re.search(self.pattern, transaction.description, re.IGNORECASE) or
                       re.search(self.pattern, transaction.merchant, re.IGNORECASE))
            except re.error:
                return False
        elif self.rule_type == 'exact':
            return (self.pattern.lower() == transaction.description.lower() or
                   self.pattern.lower() == transaction.merchant.lower())
        elif self.rule_type == 'amount_range':
            try:
                min_amount, max_amount = map(float, self.pattern.split('-'))
                return min_amount <= float(transaction.amount) <= max_amount
            except (ValueError, AttributeError):
                return False
        
        return False


class Attachment(TimestampedModel):
    """File attachments (receipts, invoices, etc.)"""
    transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/%Y/%m/%d/')
    filename = models.CharField(max_length=255)
    file_type = models.CharField(max_length=100)
    file_size = models.IntegerField()  # Size in bytes
    description = models.CharField(max_length=200, blank=True)
    
    # OCR data
    ocr_text = models.TextField(blank=True)
    ocr_confidence = models.FloatField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.filename} - {self.transaction.description}"


class Import(TimestampedModel):
    """Import tracking and history"""
    IMPORT_STATUS = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    IMPORT_SOURCES = [
        ('csv', 'CSV'),
        ('ofx', 'OFX/QFX'),
        ('manual', 'Manual Entry'),
        ('api', 'API Import'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=20, choices=IMPORT_SOURCES)
    filename = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=IMPORT_STATUS, default='pending')
    
    # Processing results
    total_records = models.IntegerField(default=0)
    processed_records = models.IntegerField(default=0)
    skipped_records = models.IntegerField(default=0)
    error_records = models.IntegerField(default=0)
    
    # Metadata
    notes = models.TextField(blank=True)
    error_log = models.JSONField(default=list, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.source} import by {self.user.username} - {self.status}"


# Legacy model compatibility
class Expense(Transaction):
    """Legacy expense model for backward compatibility"""
    class Meta:
        proxy = True
    
    def save(self, *args, **kwargs):
        self.transaction_type = 'expense'
        super().save(*args, **kwargs)


class Income(Transaction):
    """Legacy income model for backward compatibility"""
    class Meta:
        proxy = True
    
    def save(self, *args, **kwargs):
        self.transaction_type = 'income'
        super().save(*args, **kwargs)


class UserProfile(TimestampedModel):
    """Enhanced user profile with additional settings"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    monthly_budget = models.DecimalField(max_digits=11, decimal_places=2, default=0.00)
    
    # Preferences
    default_currency = models.CharField(max_length=3, default='USD')
    timezone = models.CharField(max_length=50, default='UTC')
    language = models.CharField(max_length=10, default='en')
    
    # Notification settings
    email_notifications = models.BooleanField(default=True)
    budget_alerts = models.BooleanField(default=True)
    weekly_reports = models.BooleanField(default=False)
    
    # Security
    two_factor_enabled = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username}'s profile"
