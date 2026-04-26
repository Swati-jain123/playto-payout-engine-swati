from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from app.models.transaction import Transaction
from app.models.payout import Payout
from app.services.ledger import LedgerService
from rest_framework.permissions import AllowAny


class DashboardView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):

        merchant = getattr(request, "merchant", None)

        if not merchant:
            return Response(
                {"error": "Merchant not found"},
                status=status.HTTP_403_FORBIDDEN
            )

        # ✅ ALWAYS compute from ledger (SOURCE OF TRUTH)
        balance = LedgerService.get_merchant_balance(merchant.id)
        held_balance = LedgerService.get_held_balance(merchant.id)

        transactions = (
            Transaction.objects
            .filter(merchant=merchant)
            .exclude(transaction_type__in=["HOLD", "RELEASE"])
            .order_by("-created_at")[:50]
        )

        payouts = (
            Payout.objects
            .filter(merchant=merchant)
            .order_by("-created_at")[:50]
        )

        return Response({
            "balance": balance,
            "held_balance": held_balance,
            "total_balance": balance + held_balance,

            "recent_transactions": [
                {
                    "type": t.transaction_type,
                    "amount_paise": t.amount_paise,
                    "reference_id": t.reference_id,
                    "created_at": t.created_at.isoformat()
                }
                for t in transactions
            ],

            "recent_payouts": [
                {
                    "id": p.id,
                    "amount_paise": p.amount_paise,
                    "status": p.status,
                    "failure_reason": p.failure_reason,
                    "created_at": p.created_at.isoformat()
                }
                for p in payouts
            ]
        })