from apps.invoices.services.invoice_service import create_invoice
from apps.wallets.models import Wallet, WalletMembership

from rest_framework.exceptions import ValidationError

from django.db import transaction

@transaction.atomic
def group_cash_request(user, group_code, cash_request, description):

    try:
        wallet = Wallet.objects.get(
            group_code = group_code,
            wallet_type = "GRP"
        )
    except Wallet.DoesNotExist:
        raise ValidationError("Group not found.")


    owner_membership = WalletMembership.objects.filter(
        user = user,
        wallet = wallet,
        role="OWNER"
    ).first()

    if not owner_membership:
        raise ValidationError(
            "Only group owner can raise cash-invoice requests."
        )
    
    members = WalletMembership.objects.select_related("user").filter(wallet=wallet)

    count=0
    for member in members:
        create_invoice(
            created_by = user,
            payer = member.user,
            amount = cash_request,
            description = description,
            invoice_type = "REQUEST",
            target_wallet = wallet
        )
        count+=1

    return count

    
