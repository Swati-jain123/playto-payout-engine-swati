import random
import time

class BankSimulator:

    @staticmethod
    def process_payout(amount_paise, bank_account_id):

        time.sleep(random.uniform(0.5, 1.5))

        # basic validation simulation
        if not bank_account_id or len(bank_account_id) < 4:
            return {
                "success": False,
                "status": "FAILED",
                "failure_reason": "Invalid bank account details"
            }

        # deterministic failure case
        if amount_paise > 10_00_000:  # 10k INR limit example
            return {
                "success": False,
                "status": "FAILED",
                "failure_reason": "Daily limit exceeded"
            }

        rand = random.random()

        if rand < 0.7:
            return {
                "success": True,
                "status": "COMPLETED",
                "transaction_id": f"txn_{random.randint(100000, 999999)}"
            }

        elif rand < 0.9:
            return {
                "success": False,
                "status": "FAILED",
                "failure_reason": random.choice([
                    "Insufficient funds in bank account",
                    "Bank account not verified"
                ])
            }

        else:
            return {
                "success": None,
                "status": "PROCESSING"
            }