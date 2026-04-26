from django.db import models
from django.contrib.auth.models import User

class Merchant(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='merchant')
    business_name = models.CharField(max_length=255)
    bank_account_id = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.business_name} - {self.user.email}"

    @property
    def balance(self):
        from app.services.ledger import LedgerService
        return LedgerService.get_merchant_balance(self.id)
    
    @property
    def held_balance(self):
        from app.services.ledger import LedgerService
        return LedgerService.get_held_balance(self.id)