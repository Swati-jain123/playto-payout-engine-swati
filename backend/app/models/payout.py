from django.db import models
from django.core.validators import MinValueValidator

class Payout(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    merchant = models.ForeignKey('Merchant', on_delete=models.CASCADE, related_name='payouts')
    amount_paise = models.BigIntegerField(validators=[MinValueValidator(1)])
    bank_account_id = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING', db_index=True)
    idempotency_key = models.CharField(max_length=255, unique=True, db_index=True)
    failure_reason = models.TextField(null=True, blank=True)
    retry_count = models.IntegerField(default=0)
    processing_started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['merchant', 'status']),
            models.Index(fields=['status', 'created_at']),
        ]
    
    def __str__(self):
        return f"Payout {self.id} - {self.amount_paise} paise - {self.status}"
    
    def can_transition_to(self, new_status):
        allowed_transitions = {
            'PENDING': ['PROCESSING'],
            'PROCESSING': ['COMPLETED', 'FAILED'],
            'COMPLETED': [],
            'FAILED': [],
        }
        return new_status in allowed_transitions.get(self.status, [])