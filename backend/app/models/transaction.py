from django.db import models
from django.core.validators import MinValueValidator

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
        ('HOLD', 'Hold'),
        ('RELEASE', 'Release'),
    ]
    
    merchant = models.ForeignKey('Merchant', on_delete=models.CASCADE, related_name='transactions')
    amount_paise = models.BigIntegerField(validators=[MinValueValidator(0)])
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reference_id = models.CharField(max_length=255, unique=True, db_index=True)
    metadata = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            merchant = self.merchant

            if self.transaction_type == "CREDIT":
                merchant.balance += self.amount_paise

            elif self.transaction_type == "DEBIT":
                merchant.balance -= self.amount_paise

            elif self.transaction_type == "HOLD":
                merchant.balance -= self.amount_paise

            elif self.transaction_type == "RELEASE":
                merchant.balance += self.amount_paise

            merchant.save()

    class Meta:
        indexes = [
            models.Index(fields=['merchant', 'created_at']),
            models.Index(fields=['reference_id']),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.amount_paise} paise - {self.merchant.business_name}"
