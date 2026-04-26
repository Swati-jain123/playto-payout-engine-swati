# app/auth.py
from django.contrib.auth.models import User
from rest_framework.authentication import BaseAuthentication
from app.models.merchant import Merchant

class MerchantHeaderAuth(BaseAuthentication):
    def authenticate(self, request):
        email = request.headers.get("X-Merchant-Email")

        if not email:
            return None

        user, _ = User.objects.get_or_create(username=email)

        merchant, _ = Merchant.objects.get_or_create(
            user=user,
            defaults={"business_name": f"Business {email}"}
        )

        return (user, merchant)