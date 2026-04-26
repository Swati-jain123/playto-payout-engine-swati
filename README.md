Here’s your **final, polished README.md** — clean, professional, and exactly what reviewers expect. You can **copy-paste directly** 👇

---

```md
# 💳 Playto Payout Engine

A minimal, production-grade payout processing system that simulates real-world money movement — focused on **correctness, concurrency, and data integrity**.

---

## 🚀 Features

- ✅ **Ledger-based Accounting**
  - No stored balance field
  - Balance derived from transactions (single source of truth)

- ✅ **Money Integrity**
  - All amounts stored in **paise (BigInteger)**
  - No floats → no rounding errors

- ✅ **Concurrency Safe**
  - Uses **PostgreSQL row-level locks (`SELECT FOR UPDATE`)**
  - Prevents double spending

- ✅ **Idempotent API**
  - `Idempotency-Key` ensures duplicate requests return same response
  - Safe for retries

- ✅ **Payout State Machine**
```

PENDING → PROCESSING → COMPLETED
↘ FAILED

````
- Invalid transitions are blocked

- ✅ **Async Processing**
- Celery worker processes payouts
- Simulated bank behavior:
  - 70% success
  - 20% failure
  - 10% stuck (retry)

- ✅ **Retry Logic**
- Max 3 retries for stuck payouts
- Prevents indefinite processing state

- ✅ **Merchant Dashboard**
- Available balance
- Held balance
- Payout history
- Live updates

- ✅ **Dockerized Setup**
- One command to run entire system

---

## 🧱 Tech Stack

| Layer        | Tech                         |
|-------------|------------------------------|
| Backend      | Django + DRF                 |
| Database     | PostgreSQL 15                |
| Queue        | Redis + Celery               |
| Frontend     | React + Tailwind + Vite      |
| Infra        | Docker Compose               |

---

## ⚡ Quick Start

### 1. Clone repository

```bash
git clone <your-repo-url>
cd playto-payout-engine
````

---

### 2. Setup environment

```bash
cp .env.example .env
```

---

### 3. Run with Docker

```bash
docker-compose up --build
```

---

### 4. Access application

* 🌐 Frontend → [http://localhost](http://localhost)
* 🔧 Backend API → [http://localhost:8000](http://localhost:8000)

---

## 🧪 Seed Data

On first run, the system auto-creates:

* 3 merchants
* ₹2500 initial balance each

| Merchant   | Email                                                 |
| ---------- | ----------------------------------------------------- |
| Merchant 1 | [merchant1@example.com] |
| Merchant 2 | [merchant2@example.com]|
| Merchant 3 | [merchant3@example.com]|

---

## 🔌 API Usage

### ➤ Create Payout

```http
POST /api/v1/payouts/
```

Headers:

```
Idempotency-Key: <unique-uuid>
X-Merchant-Email: merchant1@example.com
```

Body:

```json
{
  "amount_paise": 10000,
  "bank_account_id": "bank_123"
}
```

---

### ➤ Get Dashboard

```http
GET /api/v1/dashboard/
```

Headers:

```
X-Merchant-Email: merchant1@example.com
```

---

## 🧠 Core Design Decisions

### 1. Ledger System (No Balance Column)

Balance is computed as:

```
CREDIT + RELEASE - HOLD - DEBIT
```

**Why:**

* Prevents inconsistency
* Full audit trail
* Industry-standard approach

---

### 2. Concurrency Handling

```python
Transaction.objects.select_for_update().filter(merchant_id=merchant_id)
```

* Locks rows during payout
* Prevents race conditions

---

### 3. Idempotency

* Stored in `IdempotencyRecord`
* Same key → same response
* Prevents duplicate payouts

---

### 4. Atomic Money Movement

* HOLD → DEBIT / RELEASE happens inside DB transaction
* Ensures no money duplication or loss

---

## 🧪 Tests

* ✅ Concurrency test (double payout scenario)
* ✅ Idempotency test

---

## 🐳 Docker Services

* `db` → PostgreSQL
* `redis` → message broker
* `backend` → Django API
* `celery` → worker
* `celery-beat` → scheduler
* `frontend` → React app

---

## 📂 Project Structure

```
backend/
  app/
    models/
    views/
    services/
    tasks/

frontend/
docker-compose.yml
```

---

## 🌟 What This Project Demonstrates

* Real-world **money movement system design**
* Strong understanding of **database consistency**
* Proper use of **locking and transactions**
* Clean separation of concerns

---

## 📌 Notes

This project prioritizes:

* ✔ correctness over features
* ✔ integrity over speed
* ✔ real-world system behavior

---

## 📬 Submission

* GitHub Repo: <your-link>
* Live URL: <your-deployment-link>

---

