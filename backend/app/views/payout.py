from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from app.models.payout import Payout
from app.models.idempotency import IdempotencyRecord
from app.services.ledger import LedgerService
from app.tasks import process_payout


# -----------------------------
# Payout Request
# -----------------------------
class PayoutRequestView(APIView):

    def post(self, request):
        merchant = getattr(request, "merchant", None)

        if not merchant:
            return Response({'error': 'Merchant not authenticated'}, status=401)

        idempotency_key = request.headers.get('Idempotency-Key')

        if not idempotency_key:
            return Response({'error': 'Idempotency-Key header is required'}, status=400)

        # ✅ Idempotency check with expiry
        existing = IdempotencyRecord.objects.filter(
            idempotency_key=idempotency_key,
            merchant_id=merchant.id
        ).first()

        if existing:
            if existing.expires_at > timezone.now():
                return Response(existing.response_data, status=200)
            else:
                existing.delete()

        amount_paise = request.data.get('amount_paise')
        bank_account_id = request.data.get('bank_account_id')

        if not amount_paise or not bank_account_id:
            return Response({'error': 'amount_paise and bank_account_id required'}, status=400)

        amount_paise = int(amount_paise)

        with transaction.atomic():

            balance = LedgerService.get_merchant_balance(merchant.id)

            if balance < amount_paise:
                return Response({'error': 'Insufficient balance'}, status=400)

            hold_ref = f"hold_{idempotency_key}"

            success = LedgerService.hold_funds(
                merchant.id,
                amount_paise,
                hold_ref
            )

            if not success:
                return Response({'error': 'Failed to hold funds'}, status=400)

            payout = Payout.objects.create(
                merchant=merchant,
                amount_paise=amount_paise,
                bank_account_id=bank_account_id,
                idempotency_key=idempotency_key,
                status='PENDING'
            )

            response_data = {
                'payout_id': payout.id,
                'status': payout.status,
                'amount_paise': payout.amount_paise,
                'created_at': payout.created_at.isoformat()
            }

            # ✅ FIXED HERE
            IdempotencyRecord.objects.create(
                idempotency_key=idempotency_key,
                merchant_id=merchant.id,
                response_data=response_data,
                expires_at=timezone.now() + timedelta(hours=24)
            )

            process_payout.delay(payout.id)

            return Response(response_data, status=201)
# -----------------------------
# Payout Status
# -----------------------------
class PayoutStatusView(APIView):

    def get(self, request, payout_id):
        merchant = getattr(request, "merchant", None)  # ✅ FIXED

        if not merchant:
            return Response(
                {'error': 'Merchant not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        payout = Payout.objects.filter(
            id=payout_id,
            merchant=merchant
        ).first()

        if not payout:
            return Response(
                {'error': 'Payout not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response({
            'payout_id': payout.id,
            'status': payout.status,
            'amount_paise': payout.amount_paise,
            'bank_account_id': payout.bank_account_id,
            'failure_reason': payout.failure_reason,
            'created_at': payout.created_at.isoformat(),
            'completed_at': payout.completed_at.isoformat() if payout.completed_at else None
        })

# -----------------------------
# Merchant Balance
# -----------------------------

class MerchantBalanceView(APIView):

    def get(self, request):
        merchant = getattr(request, "merchant", None)  # ✅ FIXED

        if not merchant:
            return Response(
                {'error': 'Merchant not authenticated'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # ✅ ALWAYS compute from ledger
        balance = LedgerService.get_merchant_balance(merchant.id)
        held_balance = LedgerService.get_held_balance(merchant.id)

        return Response({
            'available_balance_paise': balance,
            'held_balance_paise': held_balance,
            'total_balance_paise': balance + held_balance
        })