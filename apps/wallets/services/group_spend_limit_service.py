from apps.notifications.services import create_notification
from apps.wallets.models import Wallet, WalletMembership

from rest_framework.exceptions import ValidationError

from django.db import transaction


@transaction.atomic
def set_spending_limit(user, group_code, spending_limit):
    
    try:
        wallet = Wallet.objects.get(
            wallet_type = "GRP",
            group_code = group_code
        )
    except Wallet.DoesNotExist:
        raise ValidationError("Group not found.")
    
    membership = WalletMembership.objects.filter(
        user = user,
        wallet = wallet,
        role = "OWNER"
    ).first()

    if not membership:
        raise ValidationError("Only group owners can set the spending limit.")
    
    wallet.spending_limit = spending_limit
    wallet.save(update_fields=["spending_limit"])

    members = (
        WalletMembership.objects
        .select_related("user")
        .filter(wallet=wallet)
    )

    for member in members:
        create_notification(
            user=member.user,
            message=(f"{user.username} set the spending limit for {wallet.group_name} to ₹{spending_limit}.")
        )

    return wallet.group_name
