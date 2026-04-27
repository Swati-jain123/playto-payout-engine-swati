```md
# 💳 Playto Payout Engine

A minimal, production-grade payout processing system that simulates real-world money movement — focused on **correctness, concurrency, and data integrity**.

---

## 🚀 Features

- ✅ **Ledger-based Accounting**
  - No stored balance field. Balance is derived from transactions (Single Source of Truth).
- ✅ **Money Integrity**
  - All amounts stored in **paise (BigInteger)**. No floats → no rounding errors.
- ✅ **Concurrency Safe**
  - Uses **PostgreSQL row-level locks (`SELECT FOR UPDATE`)** to prevent double spending.
- ✅ **Idempotent API**
  - `Idempotency-Key` ensures duplicate requests return the same response.
- ✅ **Payout State Machine**
  - `PENDING` → `PROCESSING` → `COMPLETED` or `FAILED`. Invalid transitions are blocked.
- ✅ **Async Processing**
  - Celery worker processes payouts with simulated bank behavior (70% success, 20% failure, 10% retry).
- ✅ **Merchant Dashboard**
  - Live view of Available balance, Held balance, and Payout history.

---

## 🧱 Tech Stack

| Layer       | Tech                         |
|------------|------------------------------|
| Backend     | Django + DRF                 |
| Database    | PostgreSQL 15                |
| Queue       | Redis + Celery               |
| Frontend    | React + Tailwind + Vite      |
| Infra       | Docker / Render              |

---

## ⚡ Quick Start

### 1. Clone repository

```bash
git clone [https://github.com/Swati-jain123/playto-payout-engine-swati](https://github.com/Swati-jain123/playto-payout-engine-swati)
cd playto-payout-engine-swati
```

### 2. Run with Docker

```bash
docker-compose up --build
```

### 3. Access application

* 🌐 **Live Demo:** [https://playto-payout-engine-swati-1.onrender.com/](https://playto-payout-engine-swati-1.onrender.com/)
* 🔧 **Local Backend:** http://localhost:8000

---

## 🧪 Seed Data

On first run, the system auto-creates 3 merchants with **₹2500** initial balance each.

| Merchant   | Email                     |
| ---------- | ------------------------- |
| Merchant 1 | merchant1@example.com     |
| Merchant 2 | merchant2@example.com     |
| Merchant 3 | merchant3@example.com     |

---

## 🔌 API Usage

### ➤ Create Payout

```http
POST /api/v1/payouts/
```

**Headers:**
```text
Idempotency-Key: <unique-uuid>
X-Merchant-Email: merchant1@example.com
```

**Body:**
```json
{
  "amount_paise": 10000,
  "bank_account_id": "ACC001" 
}
```
*Note: Use formats like `ACC001`, `BCC001`, or `BANK_HID_123` for the bank account ID.*

---

## 🧠 Core Design Decisions

### 1. Ledger System
Instead of a simple `balance` column, we calculate: `CREDIT + RELEASE - HOLD - DEBIT`. This ensures a full audit trail and prevents balance mismatch bugs.

### 2. Concurrency Handling
We use `Transaction.objects.select_for_update()` during the payout initiation. This locks the merchant's ledger rows, ensuring that if two payouts are requested at the exact same millisecond, the system processes them one by one to prevent overdrawing.

### 3. Idempotency
Every payout request requires an `Idempotency-Key`. If a network timeout occurs and the client retries the same key, the system recognizes it and returns the original result instead of creating a second payout.

---

## 📂 Project Structure

```text
backend/
  ├── app/
  │   ├── models/    # Ledger, Payout, Merchant models
  │   ├── services/  # Business logic (LedgerService, BankSimulator)
  │   └── tasks/     # Celery background tasks
frontend/            # React dashboard
docker-compose.yml   # Full system orchestration
```

---

## 📬 Submission Info

* **GitHub Repo:** [https://github.com/Swati-jain123/playto-payout-engine-swati](https://github.com/Swati-jain123/playto-payout-engine-swati)
* **Live Deployment:** [https://playto-payout-engine-swati-1.onrender.com/](https://playto-payout-engine-swati-1.onrender.com/)
```
