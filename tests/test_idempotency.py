import requests
import uuid
import time

def test_idempotency():
    """Test that same idempotency key returns same response"""
    
    print("Testing idempotency...")
    
    idempotency_key = str(uuid.uuid4())
    headers = {'Idempotency-Key': idempotency_key}
    data = {
        'amount_paise': 5000,
        'bank_account_id': 'ACC001'
    }
    
    print(f"First request with key: {idempotency_key}")
    response1 = requests.post(
        'http://localhost:8000/api/v1/payouts/',
        headers=headers,
        json=data
    )
    
    print(f"Response 1: Status {response1.status_code}")
    response1_data = response1.json()
    
    print(f"\nSecond request with same key")
    response2 = requests.post(
        'http://localhost:8000/api/v1/payouts/',
        headers=headers,
        json=data
    )
    
    print(f"Response 2: Status {response2.status_code}")
    response2_data = response2.json()
    
    # Both should return same payout_id and status
    assert response1_data['payout_id'] == response2_data['payout_id']
    assert response1_data['status'] == response2_data['status']
    
    print("\n✅ Idempotency test passed!\n")
    
    # Test that only one payout was created
    response = requests.get('http://localhost:8000/api/v1/dashboard/')
    payouts = response.json().get('recent_payouts', [])
    
    matching_payouts = [p for p in payouts if p['id'] == response1_data['payout_id']]
    assert len(matching_payouts) == 1
    
    print("✅ Verified only one payout record exists!\n")

if __name__ == '__main__':
    time.sleep(2)  # Wait for services to be ready
    test_idempotency()