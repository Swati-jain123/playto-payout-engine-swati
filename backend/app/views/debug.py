from rest_framework.views import APIView
from rest_framework.response import Response
from app.models.merchant import Merchant
from app.models.transaction import Transaction

class DebugDBView(APIView):
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
