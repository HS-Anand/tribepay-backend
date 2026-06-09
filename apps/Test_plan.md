Test cases:

1. test_successful_transfer_updates_balance
   Print: TEST: SUCCESSFUL TRANSFER & LEDGER CREATION
   Does: Verifies sender debit, receiver credit, transaction ledger creation
   App: transactions


2. test_idempotency_key_prevents_duplicate_transfer
   Print: TEST: IDEMPOTENCY PROTECTION
   Does: Prevents duplicate money movement from repeated payment requests
   App: transactions


3. test_transfer_rollback_on_failure
   Print: TEST: ATOMIC ROLLBACK PROTECTION
   Does: Ensures failed transactions rollback all wallet changes
   App: transactions


4. test_user_cannot_spend_wallet_they_do_not_own
   Print: TEST: UNAUTHORIZED WALLET ACCESS PREVENTION
   Does: Blocks users from spending another user's wallet
   App: transactions


5. test_insufficient_balance_transfer_blocked
   Print: TEST: INSUFFICIENT BALANCE PROTECTION
   Does: Prevents transfers exceeding available wallet balance
   App: transactions


6. test_total_balance_remains_constant_after_transfer
   Print: TEST: BALANCE CONSERVATION INVARIANT
   Does: Ensures money is never created or lost during transfers
   App: transactions


7. test_concurrent_double_spend_prevention
   Print: TEST: CONCURRENT DOUBLE SPEND PREVENTION
   Does: Simulates parallel payments and validates database row locking
   App: transactions


8. test_invoice_double_payment_race
   Print: TEST: INVOICE DOUBLE PAYMENT RACE PREVENTION
   Does: Prevents same invoice from being paid twice concurrently
   App: invoices


9. test_invalid_invoice_state_transition
   Print: TEST: INVALID INVOICE STATE TRANSITION
   Does: Blocks invalid invoice lifecycle changes (rejected/paid reuse)
   App: invoices


10. test_settlement_net_calculation
    Print: TEST: SETTLEMENT NET CALCULATION
    Does: Verifies multiple expenses are reduced into correct net amount
    App: settlements


11. test_execute_settlement_updates_expense_invoices_only
    Print: TEST: SETTLEMENT EXECUTION CONSISTENCY + REQUESTS UNTOUCHED
    Does: Settles expenses while keeping normal payment requests unchanged
    App: settlements


12. test_user_can_rejoin_after_leaving_group
    Print: TEST: GROUP REJOIN LIFECYCLE VALIDATION
    Does: Allows users to rejoin after leaving/rejection without duplicate requests
    App: wallets


13. test_only_owner_can_approve_join_requests
    Print: TEST: GROUP OWNER PERMISSION ENFORCEMENT
    Does: Ensures only group owners can approve join requests
    App: wallets


14. test_expired_invoices_are_marked_expired
    Print: TEST: CELERY INVOICE EXPIRY CORRECTNESS
    Does: Verifies background task expires old pending invoices correctly
    App: invoices (Celery)


15. test_invoice_reminder_idempotency
    Print: TEST: CELERY REMINDER IDEMPOTENCY
    Does: Ensures repeated Celery runs do not send duplicate reminders
    App: invoices (Celery)

