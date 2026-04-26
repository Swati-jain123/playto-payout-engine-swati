from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin
from app.models.merchant import Merchant


class TestAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):

        merchant_email = request.headers.get('X-Merchant-Email')

        # ❌ DO NOT fallback silently
        if not merchant_email:
            print("❌ Missing X-Merchant-Email header")
            request.user = None
            request.merchant = None
            return None

        print("MW HIT:", merchant_email)

        user, _ = User.objects.get_or_create(
            username=merchant_email,
            defaults={"email": merchant_email}
        )

        merchant = Merchant.objects.filter(user=user).first()

        if not merchant:
            merchant = Merchant.objects.create(
                user=user,
                business_name=f"Business for {merchant_email}",
                bank_account_id="ACC001"
            )
            print(f"Created new merchant for {merchant_email}")

        request.user = user
        request.merchant = merchant