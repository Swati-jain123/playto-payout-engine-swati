from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # 👈 Add this import
from app.models.merchant import Merchant
from app.models.transaction import Transaction
from django.core.management import call_command

class DebugDBView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        merchants = Merchant.objects.all()
        transactions = Transaction.objects.all().order_by('-id')[:10]

        from django.contrib.auth.models import User

        return Response({
            "status": "connected",

            "counts": {
                "users": User.objects.count(),
                "merchants": merchants.count(),
                "transactions": transactions.count(),
            },

            "merchants": [
                {
                    "id": m.id,
                    "user_email": getattr(m.user, "email", None),
                    "user_id": m.user.id,
                    "business": m.business_name
                }
                for m in merchants
            ],

            "recent_transactions": [
                {
                    "type": t.transaction_type,
                    "amount": t.amount_paise,
                    "ref": t.reference_id
                }
                for t in transactions
            ]
        })

    def post(self, request):
        # Visit this via Postman POST request to trigger the seed command
        try:
            call_command('seed_data')
            return Response({"message": "Seed data command executed successfully"})
        except Exception as e:
            return Response({"error": str(e)}, status=500)
