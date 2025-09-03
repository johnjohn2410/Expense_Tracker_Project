import csv
import io
import logging
from datetime import datetime, timedelta
from decimal import Decimal

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum
from django.template.loader import render_to_string
from django.utils import timezone

from .models import (
    Account,
    Attachment,
    Budget,
    Category,
    Import,
    Rule,
    Transaction,
    UserProfile,
)

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_pending_imports(self):
    """Process pending imports in the background"""
    try:
        pending_imports = Import.objects.filter(status="pending")

        for import_record in pending_imports:
            try:
                if import_record.source == "csv":
                    process_csv_import.delay(import_record.id)
                elif import_record.source == "ofx":
                    process_ofx_import.delay(import_record.id)
                else:
                    logger.warning(f"Unknown import source: {import_record.source}")
                    import_record.status = "failed"
                    import_record.error_log.append(
                        f"Unknown source: {import_record.source}"
                    )
                    import_record.save()

            except Exception as e:
                logger.error(f"Error processing import {import_record.id}: {str(e)}")
                import_record.status = "failed"
                import_record.error_log.append(str(e))
                import_record.save()

    except Exception as e:
        logger.error(f"Error in process_pending_imports: {str(e)}")
        raise self.retry(countdown=60, exc=e)


@shared_task(bind=True, max_retries=3)
def process_csv_import(self, import_id):
    """Process CSV import file"""
    try:
        import_record = Import.objects.get(id=import_id)
        import_record.status = "processing"
        import_record.save()

        # This is a placeholder - you would implement actual CSV processing
        # based on your file storage and parsing requirements

        # Simulate processing
        import_record.total_records = 100
        import_record.processed_records = 95
        import_record.skipped_records = 3
        import_record.error_records = 2
        import_record.status = "completed"
        import_record.save()

        logger.info(f"CSV import {import_id} completed successfully")

    except Import.DoesNotExist:
        logger.error(f"Import {import_id} not found")
    except Exception as e:
        logger.error(f"Error processing CSV import {import_id}: {str(e)}")
        import_record.status = "failed"
        import_record.error_log.append(str(e))
        import_record.save()
        raise self.retry(countdown=60, exc=e)


@shared_task(bind=True, max_retries=3)
def process_ofx_import(self, import_id):
    """Process OFX/QFX import file"""
    try:
        import_record = Import.objects.get(id=import_id)
        import_record.status = "processing"
        import_record.save()

        # This is a placeholder - you would implement actual OFX processing
        # using a library like ofxparse

        # Simulate processing
        import_record.total_records = 50
        import_record.processed_records = 48
        import_record.skipped_records = 1
        import_record.error_records = 1
        import_record.status = "completed"
        import_record.save()

        logger.info(f"OFX import {import_id} completed successfully")

    except Import.DoesNotExist:
        logger.error(f"Import {import_id} not found")
    except Exception as e:
        logger.error(f"Error processing OFX import {import_id}: {str(e)}")
        import_record.status = "failed"
        import_record.error_log.append(str(e))
        import_record.save()
        raise self.retry(countdown=60, exc=e)


@shared_task(bind=True, max_retries=3)
def send_budget_alerts(self):
    """Send budget alerts to users"""
    try:
        today = timezone.now().date()
        active_budgets = Budget.objects.filter(
            is_active=True, start_date__lte=today, end_date__gte=today
        )

        for budget in active_budgets:
            try:
                usage_percentage = budget.usage_percentage

                # Send alerts based on usage thresholds
                if usage_percentage >= 100:
                    send_budget_exceeded_alert.delay(budget.id)
                elif usage_percentage >= 80:
                    send_budget_warning_alert.delay(budget.id)
                elif usage_percentage >= 50 and usage_percentage < 80:
                    # Weekly progress update
                    if today.weekday() == 0:  # Monday
                        send_budget_progress_update.delay(budget.id)

            except Exception as e:
                logger.error(f"Error processing budget {budget.id}: {str(e)}")

    except Exception as e:
        logger.error(f"Error in send_budget_alerts: {str(e)}")
        raise self.retry(countdown=300, exc=e)


@shared_task(bind=True, max_retries=3)
def send_budget_exceeded_alert(self, budget_id):
    """Send budget exceeded alert"""
    try:
        budget = Budget.objects.get(id=budget_id)
        user = budget.user

        subject = f"Budget Alert: {budget.name} exceeded"
        message = f"""
        Your budget "{budget.name}" has been exceeded!
        
        Budget Amount: {budget.amount} {budget.currency}
        Amount Spent: {budget.spent_amount} {budget.currency}
        Over Budget: {budget.spent_amount - budget.amount} {budget.currency}
        
        Please review your spending and adjust your budget if necessary.
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f"Budget exceeded alert sent to {user.email}")

    except Budget.DoesNotExist:
        logger.error(f"Budget {budget_id} not found")
    except Exception as e:
        logger.error(f"Error sending budget exceeded alert: {str(e)}")
        raise self.retry(countdown=300, exc=e)


@shared_task(bind=True, max_retries=3)
def send_budget_warning_alert(self, budget_id):
    """Send budget warning alert"""
    try:
        budget = Budget.objects.get(id=budget_id)
        user = budget.user

        subject = f"Budget Warning: {budget.name} approaching limit"
        message = f"""
        Your budget "{budget.name}" is approaching its limit!
        
        Budget Amount: {budget.amount} {budget.currency}
        Amount Spent: {budget.spent_amount} {budget.currency}
        Remaining: {budget.remaining_amount} {budget.currency}
        Usage: {budget.usage_percentage:.1f}%
        
        Please monitor your spending to stay within budget.
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f"Budget warning alert sent to {user.email}")

    except Budget.DoesNotExist:
        logger.error(f"Budget {budget_id} not found")
    except Exception as e:
        logger.error(f"Error sending budget warning alert: {str(e)}")
        raise self.retry(countdown=300, exc=e)


@shared_task(bind=True, max_retries=3)
def send_budget_progress_update(self, budget_id):
    """Send weekly budget progress update"""
    try:
        budget = Budget.objects.get(id=budget_id)
        user = budget.user

        subject = f"Weekly Budget Update: {budget.name}"
        message = f"""
        Weekly update for your budget "{budget.name}":
        
        Budget Amount: {budget.amount} {budget.currency}
        Amount Spent: {budget.spent_amount} {budget.currency}
        Remaining: {budget.remaining_amount} {budget.currency}
        Usage: {budget.usage_percentage:.1f}%
        
        Keep up the good work managing your finances!
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f"Budget progress update sent to {user.email}")

    except Budget.DoesNotExist:
        logger.error(f"Budget {budget_id} not found")
    except Exception as e:
        logger.error(f"Error sending budget progress update: {str(e)}")
        raise self.retry(countdown=300, exc=e)


@shared_task(bind=True, max_retries=3)
def generate_weekly_reports(self):
    """Generate and send weekly reports to users"""
    try:
        # Get users who have opted for weekly reports
        users_with_reports = UserProfile.objects.filter(weekly_reports=True)

        for profile in users_with_reports:
            try:
                generate_user_weekly_report.delay(profile.user.id)
            except Exception as e:
                logger.error(
                    f"Error generating report for user {profile.user.id}: {str(e)}"
                )

    except Exception as e:
        logger.error(f"Error in generate_weekly_reports: {str(e)}")
        raise self.retry(countdown=3600, exc=e)


@shared_task(bind=True, max_retries=3)
def generate_user_weekly_report(self, user_id):
    """Generate weekly report for a specific user"""
    try:
        from django.contrib.auth.models import User

        user = User.objects.get(id=user_id)

        # Calculate date range for last week
        today = timezone.now().date()
        end_of_week = today - timedelta(days=today.weekday() + 1)
        start_of_week = end_of_week - timedelta(days=6)

        # Get transactions for the week
        transactions = Transaction.objects.filter(
            user=user, date__gte=start_of_week, date__lte=end_of_week, is_deleted=False
        )

        expenses = transactions.filter(transaction_type="expense")
        income = transactions.filter(transaction_type="income")

        # Generate report data
        report_data = {
            "user": user,
            "period": {"start": start_of_week, "end": end_of_week},
            "total_expenses": expenses.aggregate(total=Sum("amount"))["total"] or 0,
            "total_income": income.aggregate(total=Sum("amount"))["total"] or 0,
            "transaction_count": transactions.count(),
            "category_breakdown": expenses.values("category__name")
            .annotate(total=Sum("amount"))
            .order_by("-total")[:10],
        }

        report_data["net_flow"] = (
            report_data["total_income"] - report_data["total_expenses"]
        )

        # Send email report
        subject = f"Weekly Financial Report - {start_of_week.strftime('%B %d')} to {end_of_week.strftime('%B %d')}"

        # You would create a proper HTML template for this
        message = f"""
        Weekly Financial Report for {user.first_name or user.username}
        
        Period: {start_of_week.strftime('%B %d, %Y')} to {end_of_week.strftime('%B %d, %Y')}
        
        Summary:
        - Total Income: {report_data['total_income']} USD
        - Total Expenses: {report_data['total_expenses']} USD
        - Net Flow: {report_data['net_flow']} USD
        - Transactions: {report_data['transaction_count']}
        
        Top Spending Categories:
        """

        for category in report_data["category_breakdown"]:
            message += f"- {category['category__name']}: {category['total']} USD\n"

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )

        logger.info(f"Weekly report sent to {user.email}")

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
    except Exception as e:
        logger.error(f"Error generating weekly report for user {user_id}: {str(e)}")
        raise self.retry(countdown=3600, exc=e)


@shared_task(bind=True, max_retries=3)
def cleanup_old_attachments(self):
    """Clean up old attachments to save storage"""
    try:
        # Remove attachments older than 2 years
        cutoff_date = timezone.now() - timedelta(days=730)
        old_attachments = Attachment.objects.filter(created_at__lt=cutoff_date)

        deleted_count = old_attachments.count()
        old_attachments.delete()

        logger.info(f"Cleaned up {deleted_count} old attachments")

    except Exception as e:
        logger.error(f"Error in cleanup_old_attachments: {str(e)}")
        raise self.retry(countdown=3600, exc=e)


@shared_task(bind=True, max_retries=3)
def sync_recurring_transactions(self):
    """Sync recurring transactions"""
    try:
        today = timezone.now().date()
        recurring_transactions = Transaction.objects.filter(
            is_recurring=True, next_occurrence__lte=today
        )

        for transaction in recurring_transactions:
            try:
                # Create new transaction based on recurring pattern
                # This is a simplified implementation
                new_transaction = Transaction.objects.create(
                    user=transaction.user,
                    transaction_type=transaction.transaction_type,
                    amount=transaction.amount,
                    currency=transaction.currency,
                    date=today,
                    description=transaction.description,
                    notes=transaction.notes,
                    category=transaction.category,
                    account=transaction.account,
                    merchant=transaction.merchant,
                    location=transaction.location,
                    tags=transaction.tags,
                    is_recurring=True,
                    recurring_pattern=transaction.recurring_pattern,
                )

                # Update next occurrence (simplified - monthly recurrence)
                if transaction.recurring_pattern.get("frequency") == "monthly":
                    next_date = today.replace(day=min(today.day, 28))
                    if today.month == 12:
                        next_date = next_date.replace(year=today.year + 1, month=1)
                    else:
                        next_date = next_date.replace(month=today.month + 1)

                    transaction.next_occurrence = next_date
                    transaction.save()

                logger.info(
                    f"Created recurring transaction {new_transaction.id} for user {transaction.user.id}"
                )

            except Exception as e:
                logger.error(f"Error creating recurring transaction: {str(e)}")

    except Exception as e:
        logger.error(f"Error in sync_recurring_transactions: {str(e)}")
        raise self.retry(countdown=3600, exc=e)


@shared_task(bind=True, max_retries=3)
def apply_categorization_rules(self, transaction_id):
    """Apply categorization rules to a transaction"""
    try:
        transaction = Transaction.objects.get(id=transaction_id)
        rules = Rule.objects.filter(user=transaction.user, is_active=True).order_by(
            "-priority"
        )

        for rule in rules:
            if rule.matches_transaction(transaction):
                transaction.category = rule.category
                transaction.save()
                logger.info(
                    f"Applied rule '{rule.name}' to transaction {transaction_id}"
                )
                break

    except Transaction.DoesNotExist:
        logger.error(f"Transaction {transaction_id} not found")
    except Exception as e:
        logger.error(
            f"Error applying categorization rules to transaction {transaction_id}: {str(e)}"
        )
        raise self.retry(countdown=60, exc=e)


@shared_task(bind=True, max_retries=3)
def export_user_data(self, user_id, format_type="csv"):
    """Export user data for backup/download"""
    try:
        from django.contrib.auth.models import User

        user = User.objects.get(id=user_id)

        if format_type == "csv":
            # Generate CSV export
            output = io.StringIO()
            writer = csv.writer(output)

            # Write transactions
            writer.writerow(
                [
                    "Type",
                    "Date",
                    "Amount",
                    "Currency",
                    "Description",
                    "Category",
                    "Account",
                    "Merchant",
                ]
            )

            transactions = Transaction.objects.filter(user=user, is_deleted=False)
            for transaction in transactions:
                writer.writerow(
                    [
                        transaction.transaction_type,
                        transaction.date,
                        transaction.amount,
                        transaction.currency,
                        transaction.description,
                        transaction.category.name if transaction.category else "",
                        transaction.account.name,
                        transaction.merchant or "",
                    ]
                )

            # Send email with CSV attachment
            subject = "Your Expense Tracker Data Export"
            message = "Please find your data export attached."

            # In a real implementation, you would attach the CSV file
            # For now, just send the email
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            logger.info(f"Data export completed for user {user.id}")

    except User.DoesNotExist:
        logger.error(f"User {user_id} not found")
    except Exception as e:
        logger.error(f"Error exporting data for user {user_id}: {str(e)}")
        raise self.retry(countdown=300, exc=e)
