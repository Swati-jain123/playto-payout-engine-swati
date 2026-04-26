from django.contrib.auth.models import User
from django.utils.deprecation import MiddlewareMixin
from app.models.merchant import Merchant


class TestAuthMiddleware(MiddlewareMixin):
    def process_request(self, request):

        merchant_email = request.headers.get('X-Merchant-Email')

        # ❌ No header → reject request
        if not merchant_email:
            print("❌ Missing X-Merchant-Email header")
            request.user = None
            request.merchant = None
            return None

        merchant_email = merchant_email.strip().lower()
        print("MW HIT:", merchant_email)

        # ✅ ALWAYS use email-based lookup (NOT get_or_create on username)
        user = User.objects.filter(email=merchant_email).first()

        if not user:
            user = User.objects.create(
                username=merchant_email,
                email=merchant_email
            )
            print(f"Created new user for {merchant_email}")

        # ✅ Merchant must NOT be auto-created in middleware in production
        merchant = Merchant.objects.filter(user=user).first()

        if not merchant:
            print(f"❌ Merchant missing for {merchant_email}")
            request.user = user
            request.merchant = None
            return None

        request.user = user
        request.merchant = merchant
