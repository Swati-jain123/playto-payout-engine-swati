from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny  # 👈 Add this import
from app.models.merchant import Merchant
from app.models.transaction import Transaction
from django.core.management import call_command

class DebugDBView(APIView):
    # This allows you to visit the URL without being logged in
    permission_classes = [AllowAny] 

    def get(self, request):
        merchants = Merchant.objects.all()
        transactions = Transaction.objects.all().order_by('-id')[:10]
        
        return Response({
            "status": "connected",
            "merchant_count": merchants.count(),
            "merchants": [
                {"id": m.id, "email": m.user.email, "business": m.business_name} 
                for m in merchants
            ],
            "recent_transactions": [
                {"type": t.transaction_type, "amount": t.amount_paise, "ref": t.reference_id}
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
