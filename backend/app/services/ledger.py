from django.db import transaction
from django.db.models import Sum, Case, When, F, BigIntegerField
from app.models.transaction import Transaction
from app.models.payout import Payout

class LedgerService:

    @staticmethod
    def get_merchant_balance(merchant_id):
        """
        Available balance = CREDIT + RELEASE - DEBIT - HOLD
        """
        result = Transaction.objects.filter(merchant_id=merchant_id).aggregate(
            total=Sum(
                Case(
                    When(transaction_type='CREDIT', then=F('amount_paise')),
                    When(transaction_type='RELEASE', then=F('amount_paise')),
                    When(transaction_type='DEBIT', then=-F('amount_paise')),
                    When(transaction_type='HOLD', then=-F('amount_paise')),
                    default=0,
                    output_field=BigIntegerField()
                )
            )
        )
        return result["total"] or 0

    @staticmethod
    def get_held_balance(merchant_id):
        """Held balance = sum of all pending/processing payouts from Payout model"""
        return Payout.objects.filter(
            merchant_id=merchant_id,
            status__in=["PENDING", "PROCESSING"]
        ).aggregate(
            total=Sum("amount_paise")
        )["total"] or 0

    @staticmethod
    def hold_funds(merchant_id, amount_paise, reference_id):
        with transaction.atomic():
            # Lock rows for this merchant to prevent race conditions
            # Note: In some DBs, select_for_update() on a filter might lock more than you think
            Transaction.objects.select_for_update().filter(merchant_id=merchant_id)
            
            current_balance = LedgerService.get_merchant_balance(merchant_id)
            
            if current_balance < amount_paise:
                return False
            
            # Idempotency check: Don't create the same hold twice
            if Transaction.objects.filter(reference_id=reference_id).exists():
                return True
            
            Transaction.objects.create(
                merchant_id=merchant_id,
                amount_paise=amount_paise,
                transaction_type="HOLD",
                reference_id=reference_id,
                metadata={"type": "payout_hold"}
            )
            return True

    @staticmethod
    def release_funds(merchant_id, amount_paise, reference_id, is_success=False):
        with transaction.atomic():
            if is_success:
                # 1. Release the hold
                rel_ref = f"rel_{reference_id}"
                if not Transaction.objects.filter(reference_id=rel_ref).exists():
                    Transaction.objects.create(
                        merchant_id=merchant_id,
                        transaction_type="RELEASE",
                        amount_paise=amount_paise,
                        reference_id=rel_ref,
                        metadata={"payout_reference": reference_id, "note": "Releasing hold for debit"}
                    )
                
                # 2. Apply the actual debit
                deb_ref = f"deb_{reference_id}"
                if not Transaction.objects.filter(reference_id=deb_ref).exists():
                    Transaction.objects.create(
                        merchant_id=merchant_id,
                        transaction_type="DEBIT",
                        amount_paise=amount_paise,
                        reference_id=deb_ref,
                        metadata={"payout_reference": reference_id}
                    )
            else:
                # Failure case: Just release the hold
                rel_ref = f"rel_{reference_id}"
                if not Transaction.objects.filter(reference_id=rel_ref).exists():
                    Transaction.objects.create(
                        merchant_id=merchant_id,
                        transaction_type="RELEASE",
                        amount_paise=amount_paise,
                        reference_id=rel_ref,
                        metadata={"payout_reference": reference_id, "note": "Failed payout return"}
                    )