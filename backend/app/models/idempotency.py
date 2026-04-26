from django.db import models

class IdempotencyRecord(models.Model):
    idempotency_key = models.CharField(max_length=255, unique=True, db_index=True)
    merchant_id = models.IntegerField(db_index=True)
    response_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        indexes = [
            models.Index(fields=['merchant_id', 'idempotency_key']),
        ]