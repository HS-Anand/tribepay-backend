# TribePay

## Your tribe. Your money. Together.

TribePay is a transaction-safe collaborative payment backend — wallet infrastructure for individuals and groups, built around financial correctness at every layer.

At its core, TribePay is powered by a money movement engine responsible for executing wallet transfers, maintaining a transaction ledger, and preserving financial consistency.

On top of this transaction layer, TribePay enables shared tribe wallets, smart expense splitting, cash invoice requests, settlements, and automated background workflows.

**Live Swagger API:**  
https://tribepay-backend.onrender.com/

---

# Why TribePay?

Most expense-splitting applications only record who owes whom after money has already moved externally.

TribePay handles the complete payment workflow:

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

The goal is not only expense tracking — but building a reliable transaction system with correctness, consistency, and auditability.

---

# Engineering Highlights

## Financial Consistency

All critical money operations execute inside database transactions using:

```python
transaction.atomic()
```

Operations:

- Wallet debit
- Wallet credit
- Transaction ledger creation

commit together as a single unit.

If any step fails:

```
Failure
   ↓
Rollback
   ↓
Original wallet state preserved
```

This prevents partial money movement and inconsistent balances.

---

## Race Condition Protection

Concurrent wallet updates are protected using PostgreSQL row-level locking:

```python
select_for_update()
```

Example:

```
Wallet Balance: ₹500

Request A → Spend ₹400
Request B → Spend ₹400
```

Only one transaction succeeds. The other request fails safely.

Prevents:

- Double spending
- Balance corruption
- Concurrent invoice payments

---

## Deadlock Prevention

Wallet locks are acquired in deterministic wallet ID order.

This prevents circular waits when multiple transactions involving the same wallets execute simultaneously.

---

## Idempotency Handling

Payment operations support idempotency keys.

Protects against:

- Network retries
- Duplicate requests
- Accidental double payments

Flow:

```
First Request
      ↓
Transaction Created


Duplicate Request
      ↓
Existing Transaction Returned
```

---

## Async Processing

Implemented using:

- Celery
- Redis
- Celery Beat

Background workflows:

- Automatic invoice expiry
- Payment reminders

Jobs are designed to be idempotent to prevent duplicate processing during retries.

---

# Core Features

## Wallet Infrastructure

Unified wallet system supporting:

- Personal wallets
- Group (Tribe) wallets
- OWNER / MEMBER roles
- Wallet membership lifecycle
- Balance tracking
- Active/inactive wallet states

---

# Transaction Engine

The transaction engine is the core layer powering TribePay.

Supported flows:

- Personal → Personal transfers
- Personal → Group contributions
- Group expenses
- Invoice payments
- Settlement payments

Transaction types:

- TRANSFER
- DEPOSIT
- GROUP_CONTRIBUTION
- GROUP_EXPENSE
- WITHDRAWAL
- SETTLEMENT

Each transaction stores:

- Sender wallet
- Receiver wallet
- Initiating user
- Amount
- Transaction type
- Status
- Reference ID
- Idempotency key
- Timestamp

The Transaction model acts as a centralized ledger and audit history for every money movement.

---

# Tribe Wallet System

Shared financial spaces for groups.

Features:

- Create tribe wallets
- Unique group invite codes
- Join request workflow
- Owner approval/rejection
- Member removal
- Leave group workflow

---

# Smart Payment Engine

Smart payments combine multiple financial workflows into one atomic operation.

Example:

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

- Transfer Service
- Split Service
- Invoice Service

---

# Cash Invoice System

Payment request infrastructure built on top of wallet transactions.

Features:

- Create payment requests
- Assign payer
- Pay invoice through wallet engine
- Reject invoice
- Invoice history
- Filtering
- Automatic expiry

Lifecycle:

```
PENDING

 ├── PAID

 ├── REJECTED

 ├── EXPIRED

 └── SETTLED
```

---

# Split Engine

Automated expense splitting system.

Supports:

- Equal splits
- Custom amount splits
- Automatic invoice generation
- Split history

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

- Net balance calculation
- Bilateral debt optimization
- Optimized settlement calculation
- Settlement execution through wallet transactions
- Invoice settlement tracking

---

# Notification System

Event-based notification service.

Events:

- Money sent
- Money received
- Group transactions
- Invoice creation/payment/rejection
- Expiry reminders
- Join requests
- Member approval/rejection

---

# Architecture

TribePay follows a modular service-layer architecture.

```
API Request

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

Services contain business workflows.

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

Models:

- User
- Wallet
- WalletMembership
- GroupJoinRequest
- Transaction
- CashInvoice
- SplitPayment
- SplitMember
- Notification

Design decisions:

- UUID identifiers
- Foreign key relationships
- Custom many-to-many models
- Database constraints
- Decimal fields for money precision
- Created/updated timestamps

(Add ER diagram image here)

---

# Security

Implemented:

- JWT authentication
- Protected REST APIs
- Wallet ownership validation
- Group role-based authorization
- Owner-only permission enforcement
- Invalid transaction and invoice state prevention

---

# API Documentation

Built using Django REST Framework.

Features:

- 28 documented REST APIs
- Swagger/OpenAPI documentation
- Postman tested endpoints
- Pagination
- Database-level filtering
- Chronological ordering

**Swagger UI:**

https://tribepay-backend.onrender.com/

(Add Swagger screenshot here)

---

# Testing

Automated backend tests focus on financial correctness and reliability.

Run:

```bash
python manage.py test
```

Result:

```
Found 16 tests

Ran 16 tests in 7.805s

OK
```

(Add test screenshot here)

Coverage:

## Transactions

- Successful transfer execution
- Ledger creation
- Balance conservation
- Rollback protection
- Insufficient balance handling

## Concurrency

- Concurrent double-spend prevention
- Invoice double-payment race prevention

## Idempotency

- Duplicate payment request handling

## Authorization

- Unauthorized wallet access prevention
- Owner permission enforcement

## Workflows

- Smart payment atomic workflow
- Settlement calculation
- Settlement execution
- Group lifecycle validation

## Background Jobs

- Invoice expiry correctness
- Reminder idempotency

---

# Performance Testing

Created a custom concurrent API load tester using:

- Python
- Requests
- ThreadPoolExecutor

Measured:

- Success rate
- Throughput
- Average latency
- P95 latency
- Failure rate

---

# Deployment Benchmark

Environment:

```
API Request

 ↓

Render Django Backend

 ↓

Render PostgreSQL
```

Results:

```
1000 authenticated requests

Concurrent workers:
10

Successful requests:
1000 / 1000

Failure rate:
0%

Throughput:
~37 requests/sec

Average latency:
~267 ms

P95 latency:
~519 ms
```

(Add load test screenshot here)

Stress testing showed that transaction correctness was maintained under concurrent load, while higher traffic increased latency due to deployment and database resource limitations.

---

# Tech Stack

## Backend

- Django 5
- Django REST Framework

## Database

- PostgreSQL

## Authentication

- Simple JWT

## Async Processing

- Celery
- Redis
- Celery Beat

## Documentation

- Swagger
- OpenAPI (drf-spectacular)

## Testing

- Django Test Framework
- Postman
- Custom Load Tester

## Deployment

- Render
- Gunicorn
- WhiteNoise

## Configuration

- Environment variables
- .env.example
- requirements.txt dependency management

---

# Local Setup

Clone repository:

```bash
git clone <repo-url>

cd TribePay
```

Create virtual environment:

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

A sample environment file is provided:

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

Start development server:

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

Currently deployed using:

- Render Web Service
- Render PostgreSQL
- Gunicorn WSGI server
- Environment-based configuration

---

# Future Improvements

- User-facing web/mobile application for managing wallets, tribe payments, cash invoices, splits, and settlements

- Docker-based containerization to simplify environment setup and maintain consistent deployments across systems

- Enhanced observability with structured transaction logging to trace payment workflows across wallet, invoice, split, and settlement services

- Database performance optimization using indexing and connection pooling for higher concurrent transaction loads