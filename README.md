# TribePay

## Your tribe. Your money. Together.

TribePay is a transaction-safe collaborative payment backend that provides wallet infrastructure for individuals and groups.

At its core, TribePay is built around a **money movement engine** responsible for executing wallet transfers, maintaining transaction history, and ensuring financial correctness.

On top of this transaction layer, TribePay enables shared wallets, automatic expense splitting, cash invoice requests, and optimized settlements.

---

## Why TribePay?

Traditional expense trackers mainly record who owes whom after payments happen externally.

TribePay focuses on the complete payment workflow:

```
Payment Initiated
        ↓
Wallet Transaction
        ↓
Ledger Entry Created
        ↓
Automatic Split Calculation
        ↓
Cash Invoice Generation
        ↓
Repayment / Settlement
```

The goal is to handle collaborative money movement while maintaining reliability, consistency, and correctness.

---

# Core Features

## Wallet Infrastructure

Unified wallet system supporting multiple wallet types.

Features:

* Personal wallets
* Group (Tribe) wallets
* Wallet membership system
* OWNER / MEMBER roles
* Balance tracking
* Active/inactive wallet lifecycle
* User-wallet relationship management

---

# Transaction Engine

The transaction engine is the core layer powering TribePay.

Supported transaction flows:

* Personal → Personal transfers
* Personal → Group contributions
* Group spending
* Invoice payments
* Settlement payments

Transaction types:

* TRANSFER
* DEPOSIT
* GROUP_CONTRIBUTION
* GROUP_EXPENSE
* WITHDRAWAL
* SETTLEMENT

Each transaction stores:

* Sender wallet
* Receiver wallet
* Initiating user
* Amount
* Transaction type
* Status
* Reference ID
* Idempotency key
* Timestamp

The transaction model acts as a centralized ledger and audit history for all money movement.

---

## Transaction Lifecycle

```
API Request

    ↓

Validate User Access

    ↓

Acquire Wallet Locks

    ↓

Validate Balance

    ↓

Update Wallet Balances

    ↓

Create Transaction Record

    ↓

Commit Transaction
```

---

# Tribe Wallet System

Shared financial spaces for groups.

Features:

* Create tribe wallets
* Unique group codes
* Join requests
* Owner approval/rejection
* Member removal
* Leave group workflow
* Membership tracking

---

# Smart Payment Engine

Smart payments combine transactions, splitting, and invoices into a single workflow.

Example:

A user pays a group bill.

```
Payment
   |
   ├── Execute wallet transaction
   |
   ├── Calculate member shares
   |
   ├── Generate cash invoices
   |
   └── Track repayments
```

Implemented through:

* Transfer service
* Split service
* Invoice service

---

# Cash Invoice System

Payment request infrastructure built on top of wallet transactions.

Features:

* Create payment requests
* Assign payer
* Pay invoice through wallet
* Reject invoice
* Invoice history
* Invoice filtering
* Automatic expiry

Invoice lifecycle:

```
PENDING

   ├── PAID

   ├── REJECTED

   ├── EXPIRED

   └── SETTLED
```

Invoices are linked with transactions after payment execution.

---

# Split Engine

Automated expense splitting system.

Supports:

* Equal splits
* Custom amount splits
* Split history
* Automatic invoice generation

Flow:

```
SplitPayment

      ↓

SplitMember

      ↓

CashInvoice
```

---

# Settlement Engine

Optimizes repayments between group members.

Features:

* Net balance calculation
* Bilateral debt optimization
* Settlement suggestions
* Settlement execution through wallet transactions
* Invoice settlement tracking

---

# Notification System

Event-based notification system.

Events:

* Money sent
* Money received
* Group contributions
* Group spending
* Invoice creation
* Invoice payment
* Invoice rejection
* Expiry reminders
* Join requests
* Member approval/rejection

---

# System Architecture

TribePay follows a modular service-layer architecture.

```
Client

  ↓

Django REST Framework Views

  ↓

Serializers

  ↓

Service Layer

  ↓

Django ORM

  ↓

PostgreSQL
```

Views handle HTTP logic.

Services handle business workflows.

---

## Service Structure

```
wallets/

    wallet_service

    transfer_service

    add_money_service

    group_wallet_service

    smart_payment_service


invoices/

    invoice_service


splits/

    split_service


settlements/

    settlement_service


notifications/

    notification_service
```

---

# Database Design

Core models:

* User
* Wallet
* WalletMembership
* GroupJoinRequest
* Transaction
* CashInvoice
* SplitPayment
* SplitMember
* Notification

Database concepts used:

* UUID identifiers
* Foreign key relationships
* Many-to-many relationships using custom models
* Database constraints
* Decimal fields for money storage
* Created/updated timestamps

(Add ER diagram here)

---

# Financial Reliability Engineering

## Atomic Transactions

Critical money operations use:

```python
transaction.atomic()
```

Guarantees:

* Wallet debit
* Wallet credit
* Transaction creation

execute together.

If any step fails:

```
Error

 ↓

Rollback

 ↓

Original balances preserved
```

---

## Race Condition Protection

Problem:

```
Wallet Balance = ₹500


Request A spends ₹400

Request B spends ₹400
```

Both arrive together.

Solution:

PostgreSQL row-level locking:

```python
select_for_update()
```

Prevents:

* Double spending
* Balance corruption
* Concurrent invoice payments

---

# Deadlock Prevention

Wallet locks are acquired in a deterministic order using wallet IDs.

This avoids circular waits during simultaneous transfers.

---

# Idempotency Handling

Payments support idempotency keys.

Protects against:

* Network retries
* Duplicate requests
* Double payment attempts

Flow:

```
First request

      ↓

Transaction created


Duplicate request

      ↓

Existing transaction returned
```

---

# Async Processing

Implemented using:

* Celery
* Redis
* Celery Beat

Background workflows:

* Automatic invoice expiry
* Payment reminders

Reliability:

* Persistent reminder state
* Duplicate reminder prevention
* Idempotent scheduled jobs

---

# Security

Implemented:

* JWT authentication
* Protected APIs
* Wallet ownership checks
* Group role validation
* Owner-only permissions
* Invalid state transition prevention
* Request throttling

---

# API Documentation

Built using Django REST Framework.

Features:

* 28 documented REST APIs
* Swagger/OpenAPI documentation
* Postman tested endpoints
* Pagination
* Database-level filtering
* Chronological ordering

Swagger UI:

```
https://tribepay-backend.onrender.com/
```

(Add Swagger screenshot)

---

# Testing

Automated backend tests focus on financial correctness.

Run tests:

```bash
python manage.py test
```

Result:

```
Found 16 tests

Ran 16 tests in 7.805s

OK
```

Coverage:

### Transactions

* Successful transfer
* Ledger creation
* Balance conservation
* Rollback protection
* Insufficient balance handling

### Concurrency

* Concurrent double spend prevention
* Invoice double payment prevention

### Idempotency

* Duplicate payment prevention

### Authorization

* Unauthorized wallet access prevention
* Owner permission enforcement

### Workflows

* Smart payment atomic workflow
* Settlement calculation
* Settlement execution
* Group lifecycle handling

### Background Jobs

* Invoice expiry
* Reminder idempotency

---

# Performance Testing

Built a custom concurrent API load tester using:

* Python
* Requests
* ThreadPoolExecutor

Measured:

* Success rate
* Throughput
* Average latency
* P95 latency

---

## Deployment Benchmark

Environment:

```
Client

 ↓

Render Django Backend

 ↓

Render PostgreSQL
```

Result:

```
1000 authenticated requests

10 concurrent workers


Success:

1000/1000


Failure Rate:

0%


Throughput:

~37 requests/sec


Average Latency:

~267 ms


P95 Latency:

~519 ms
```

Stress testing identified deployment resource limits as the scaling bottleneck.

Future scaling:

* Connection pooling
* Worker tuning
* Horizontal scaling
* Caching

---

# Tech Stack

Backend:

* Django 5
* Django REST Framework

Database:

* PostgreSQL

Authentication:

* Simple JWT

Async:

* Celery
* Redis
* Celery Beat

Documentation:

* Swagger
* OpenAPI (drf-spectacular)

Testing:

* Django Test Framework
* Postman
* Custom Load Tester

Deployment:

* Render
* Gunicorn
* WhiteNoise

---

# Local Setup

Clone repository:

```bash
git clone <repo-url>

cd TribePay
```

Create environment:

```bash
python -m venv venv

source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Environment Setup

A sample environment file is provided.

```bash
cp .env.example .env
```

Example:

```env
SECRET_KEY=your_secret_key

DEBUG=True

ALLOWED_HOSTS=localhost,127.0.0.1

POSTGRES_DB=your_database

POSTGRES_USER=your_user

POSTGRES_PASSWORD=your_password

POSTGRES_HOST=localhost

POSTGRES_PORT=5432

REDIS_URL=redis://localhost:6379/0
```

---

# Run Project

Apply migrations:

```bash
python manage.py migrate
```

Start server:

```bash
python manage.py runserver
```

---

# Run Background Workers

Start Celery worker:

```bash
celery -A TribePay worker -l info
```

Start scheduler:

```bash
celery -A TribePay beat -l info
```

---

# Deployment

Current deployment:

* Render Web Service
* Render PostgreSQL
* Gunicorn server
* Environment variable configuration

---

# Future Improvements

* Frontend client
* Docker containerization
* Structured logging
* Monitoring
* Advanced caching
