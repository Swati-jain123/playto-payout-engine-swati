# 📄 EXPLAINER.md

## 1. The Ledger

### ✅ Balance Calculation Query

```python
result = Transaction.objects.filter(
    merchant_id=merchant_id
).aggregate(
    total=Sum(
        Case(
            When(transaction_type='CREDIT', then=F('amount_paise')),
            When(transaction_type='RELEASE', then=F('amount_paise')),
            When(transaction_type='HOLD', then=-F('amount_paise')),
            When(transaction_type='DEBIT', then=-F('amount_paise')),
            default=0,
            output_field=BigIntegerField()
        )
    )
)
```

### 💡 Why this model?

I used a **ledger-based system** instead of storing balance directly.

* `CREDIT` → money coming in
* `HOLD` → temporarily reserved for payout
* `DEBIT` → successful payout
* `RELEASE` → failed payout refund

### ✅ Key Benefits

* **Single source of truth** → Transaction table
* **No race conditions** on balance updates
* **Auditability** → every money movement is recorded
* **Mathematically consistent** →

  ```
  Balance = CREDIT + RELEASE - HOLD - DEBIT
  ```

---

## 2. The Lock (Concurrency Control)

### ✅ Critical Code

```python
Transaction.objects.select_for_update().filter(
    merchant_id=merchant_id
)
```

Used inside:

```python
with transaction.atomic():
```

### 💡 What this does

* Locks all transaction rows for the merchant
* Prevents **parallel payout requests** from reading stale balance

### 🧠 Why this works

This relies on:

👉 **PostgreSQL row-level locking (`SELECT ... FOR UPDATE`)**

### 🚨 Problem solved

Scenario:

* Balance = ₹100
* Two requests of ₹60 come simultaneously

Without lock:

* Both see ₹100 → both succeed ❌

With lock:

* First request locks rows → processes
* Second request waits → sees updated balance → fails ✅

---

## 3. The Idempotency

### ✅ How system detects duplicate requests

```python
existing = IdempotencyRecord.objects.filter(
    idempotency_key=idempotency_key,
    merchant_id=merchant.id
).first()

if existing:
    return Response(existing.response_data, status=200)
```

### ✅ Storage

```python
IdempotencyRecord.objects.create(
    idempotency_key=idempotency_key,
    merchant_id=merchant.id,
    response_data=response_data,
    expires_at=timezone.now() + timedelta(hours=24)
)
```

### 💡 Behavior

* Same key → same response returned
* No duplicate payout created

### 🧠 Edge case handled

👉 If second request comes while first is in-flight:

* First transaction creates record inside DB transaction
* Second request either:

  * waits OR
  * finds record → returns cached response

---

## 4. The State Machine

### ✅ Allowed transitions

```
PENDING → PROCESSING → COMPLETED
PENDING → PROCESSING → FAILED
```

### ✅ Enforcement

```python
if payout.status != "PENDING":
    return
```

Inside worker:

```python
payout = Payout.objects.select_for_update().get(id=payout_id)
```

### ❌ Prevented transitions

* COMPLETED → anything ❌
* FAILED → COMPLETED ❌

### 💡 Atomic guarantee

```python
with transaction.atomic():
```

Used while:

* updating payout status
* releasing/debiting funds

So:

👉 **State change + ledger update happen together**

---

## 5. The Retry Logic

```python
@shared_task(bind=True, max_retries=3)
```

```python
raise self.retry(countdown=10)
```

### 💡 Behavior

* If bank response = "processing" → retry
* Max 3 retries
* After that → FAILED

---

## 6. The AI Audit (Important Section)

### ❌ Problem AI introduced

AI initially suggested:

```python
merchant.balance -= amount
merchant.save()
```

### 🚨 Why this is wrong

* Not atomic
* Race conditions
* Breaks ledger consistency

---

### ❌ Another issue

AI missed:

```python
expires_at
```

in IdempotencyRecord → caused:

```
IntegrityError: null value in column "expires_at"
```

---

### ✅ What I fixed

1. Replaced direct balance updates with **ledger system**
2. Added:

```python
expires_at = timezone.now() + timedelta(hours=24)
```

3. Implemented:

```python
select_for_update()
```

for concurrency safety

---

## 7. Architecture Decisions

### Backend

* Django + DRF
* PostgreSQL (strong consistency)
* Celery + Redis for async payouts

### Frontend

* React + Tailwind
* Real-time dashboard refresh

### Infra

* Docker Compose:

  * Postgres
  * Redis
  * Backend (Gunicorn)
  * Celery Worker
  * Celery Beat
  * Frontend

---

## 8. What I am most proud of

* Correct **ledger-based accounting system**
* Proper **database-level locking**
* Real **idempotent API design**
* Clean separation of:

  * API
  * Ledger
  * Worker

---

## 9. Future Improvements

* Webhooks for payout updates
* Better retry strategy (exponential backoff)
* Event sourcing for full audit logs
* Merchant authentication system

---

# ✅ Final Note

This system prioritizes:

* **Correctness over features**
* **Data integrity over speed**
* **Real-world payment system constraints**
