import random
import string

from django.db import transaction
from rest_framework.exceptions import ValidationError

from apps.wallets.models import (
    Wallet,
    WalletMembership,
    GroupJoinRequest
)

from apps.notifications.services import create_notification


def generate_group_code():

    while True:

        code = "".join(
            random.choices(
                string.ascii_uppercase + string.digits,
                k=6
            )
        )

        exists = Wallet.objects.filter(
            group_code=code
        ).exists()

        if not exists:
            return code


@transaction.atomic
def create_group_wallet(user, group_name):

    wallet = Wallet.objects.create(
        wallet_type="GRP",
        group_name=group_name,
        group_code=generate_group_code(),
        created_by=user
    )

    WalletMembership.objects.create(
        user=user,
        wallet=wallet,
        role="OWNER"
    )

    return wallet


@transaction.atomic
def request_join_group(user, group_code):

    try:

        wallet = Wallet.objects.get(
            group_code=group_code,
            wallet_type="GRP"
        )

    except Wallet.DoesNotExist:

        raise ValidationError(
            "Invalid group code."
        )

    already_member = (
        WalletMembership.objects.filter(
            user=user,
            wallet=wallet
        ).exists()
    )

    if already_member:

        raise ValidationError(
            "You are already a member."
        )

    existing_request = (
        GroupJoinRequest.objects.filter(
            wallet=wallet,
            requested_user=user
        ).first()
    )

    if existing_request:

        if existing_request.status == "PENDING":

            raise ValidationError(
                "Join request already pending."
            )

        existing_request.status = "PENDING"
        existing_request.save()

        join_request = existing_request

    else:

        join_request = GroupJoinRequest.objects.create(
            wallet=wallet,
            requested_user=user
        )

    owners = (
        wallet
        .memberships
        .filter(role="OWNER")
    )

    for owner in owners:

        create_notification(
            user=owner.user,
            message=f"{user.username} requested to join {wallet.group_name}."
        )

    return join_request


@transaction.atomic
def approve_join_request(owner_user, request_id):

    try:

        join_request = (
            GroupJoinRequest.objects
            .select_related(
                "wallet",
                "requested_user"
            )
            .get(
                rid=request_id,
                status="PENDING"
            )
        )

    except GroupJoinRequest.DoesNotExist:

        raise ValidationError(
            "Join request not found."
        )

    is_owner = (
        WalletMembership.objects.filter(
            user=owner_user,
            wallet=join_request.wallet,
            role="OWNER"
        ).exists()
    )

    if not is_owner:

        raise ValidationError(
            "Only owner can approve requests."
        )

    WalletMembership.objects.create(
        user=join_request.requested_user,
        wallet=join_request.wallet,
        role="MEMBER"
    )

    join_request.status = "APPROVED"
    join_request.save()

    create_notification(
        user=join_request.requested_user,
        message=f"Your request to join {join_request.wallet.group_name} was approved."
    )

    return join_request

@transaction.atomic
def reject_join_request(request_id, owner_user):

    join_request = (
        GroupJoinRequest.objects
        .select_for_update()
        .select_related(
            "wallet",
            "requested_user"
        )
        .get(rid=request_id)
    )

    is_owner = (
        WalletMembership.objects.filter(
            wallet=join_request.wallet,
            user=owner_user,
            role="OWNER"
        ).exists()
    )

    if not is_owner:

        raise ValidationError(
            "Only owner can reject requests."
        )

    if join_request.status != "PENDING":

        raise ValidationError(
            "Request already processed."
        )

    join_request.status = "REJECTED"
    join_request.save()

    create_notification(
        user=join_request.requested_user,
        message=f"Your request to join {join_request.wallet.group_name} was rejected."
    )

    return join_request


@transaction.atomic
def leave_group(user, group_id):

    try:

        membership = (
            WalletMembership.objects
            .select_related("wallet")
            .get(
                user=user,
                wallet__wid=group_id
            )
        )

    except WalletMembership.DoesNotExist:

        raise ValidationError(
            "You are not a member."
        )

    wallet = membership.wallet

    if membership.role == "OWNER":

        member_count = (
            WalletMembership.objects.filter(
                wallet=wallet
            ).count()
        )

        if member_count > 1:

            raise ValidationError(
                "Owner cannot leave while members remain."
            )

        membership.delete()

        wallet.is_active = False
        wallet.save()

        return "GROUP_CLOSED"

    membership.delete()

    return "LEFT_GROUP"


@transaction.atomic
def remove_member(
    owner_user,
    group_id,
    username
):

    try:

        wallet = Wallet.objects.get(
            wid=group_id,
            wallet_type="GRP"
        )

    except Wallet.DoesNotExist:

        raise ValidationError(
            "Group not found."
        )

    is_owner = (
        WalletMembership.objects.filter(
            user=owner_user,
            wallet=wallet,
            role="OWNER"
        ).exists()
    )

    if not is_owner:

        raise ValidationError(
            "Only owner can remove members."
        )

    if owner_user.username == username:

        raise ValidationError(
            "Use leave group instead."
        )

    try:

        membership = (
            WalletMembership.objects
            .select_related("user")
            .get(
                wallet=wallet,
                user__username=username
            )
        )

    except WalletMembership.DoesNotExist:

        raise ValidationError(
            "Member not found."
        )

    if membership.role == "OWNER":

        raise ValidationError(
            "Owner cannot be removed."
        )

    removed_user = membership.user

    membership.delete()

    create_notification(
        user=removed_user,
        message=f"You were removed from {wallet.group_name}."
    )

    return True