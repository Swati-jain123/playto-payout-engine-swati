from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models.merchant import Merchant
from app.models.transaction import Transaction
import random

class Command(BaseCommand):
    help = 'Seed database with test merchants and transactions'
    
    def handle(self, *args, **options):
        # Create merchants
        merchants_data = [
            {'email': 'merchant1@example.com', 'business': 'Tech Solutions India', 'bank_account': 'ACC001'},
            {'email': 'merchant2@example.com', 'business': 'Digital Agency Mumbai', 'bank_account': 'ACC002'},
            {'email': 'merchant3@example.com', 'business': 'Freelance Designer', 'bank_account': 'ACC003'},
        ]
        
        for data in merchants_data:
            user, created = User.objects.get_or_create(
                username=data['email'],
                defaults={
                    'email': data['email'],
                    'password': 'testpass123'
                }
            )
            
            merchant, created = Merchant.objects.get_or_create(
                user=user,
                defaults={
                    'business_name': data['business'],
                    'bank_account_id': data['bank_account']
                }
            )
            
            if created:
                # Seed with credit history
                credits = [50000, 25000, 100000, 75000]  # amounts in paise (500, 250, 1000, 750 INR)
                for amount in credits:
                    Transaction.objects.create(
                        merchant=merchant,
                        amount_paise=amount,
                        transaction_type='CREDIT',
                        reference_id=f"seed_credit_{amount}_{merchant.id}",
                        metadata={'source': 'seed_data'}
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Created merchant: {merchant.business_name} with balance {merchant.balance/100:.2f} INR'))
            else:
                self.stdout.write(f'Merchant already exists: {merchant.business_name}')