from celery import shared_task
from django.db import transaction
from django.utils import timezone
from app.models.payout import Payout
from app.services.bank_simulator import BankSimulator
from app.services.ledger import LedgerService
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def process_payout(self, payout_id):
    try:
        # =========================
        # 1. LOCK + UPDATE STATUS
        # =========================
        with transaction.atomic():
            payout = (
                Payout.objects
                .select_for_update()
                .select_related("merchant")
                .get(id=payout_id)
            )

            if payout.status != "PENDING":
                return

            payout.status = "PROCESSING"
            payout.processing_started_at = timezone.now()
            payout.save()

        # =========================
        # 2. BANK CALL (OUTSIDE LOCK)
        # =========================
        result = BankSimulator.process_payout(
            payout.amount_paise,
            payout.bank_account_id
        )

        # =========================
        # 3. FINAL UPDATE
        # =========================
        with transaction.atomic():
            payout = Payout.objects.select_for_update().get(id=payout_id)

            if result["success"] is True:

                payout.status = "COMPLETED"
                payout.completed_at = timezone.now()
                payout.save()

                LedgerService.release_funds(
                    payout.merchant_id,
                    payout.amount_paise,
                    f"payout_{payout.id}",
                    is_success=True
                )

            elif result["success"] is False:

                payout.status = "FAILED"
                payout.failure_reason = result.get("failure_reason", "Unknown")
                payout.save()

                LedgerService.release_funds(
                    payout.merchant_id,
                    payout.amount_paise,
                    f"payout_{payout.id}",
                    is_success=False
                )

            else:
                # stuck case → requeue
                raise self.retry(countdown=10)

    except Exception as e:
        raise self.retry(exc=e, countdown=60)

@shared_task
def process_pending_payouts():
    """
    Scan for pending payouts and process them.
    """
    pending_payouts = Payout.objects.filter(status='PENDING')
    
    for payout in pending_payouts:
        process_payout.delay(payout.id)