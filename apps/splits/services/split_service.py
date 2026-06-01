from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError

from django.contrib.auth import get_user_model


from apps.splits.models import (
    SplitPayment,
    SplitMember
)


from apps.invoices.services.invoice_service import (
    create_invoice
)



User = get_user_model()




@transaction.atomic
def create_split(
    created_by,
    total_amount,
    title,
    split_type,
    members
):


    if total_amount <= 0:

        raise ValidationError(
            "Amount must be greater than zero."
        )


    if not members:

        raise ValidationError(
            "Add at least one member."
        )


    # -------------------------
    # Fetch users in one query
    # -------------------------


    usernames = [

        member["username"]

        for member in members
    ]


    if created_by.username in usernames:

        raise ValidationError(
            "Cannot split with yourself."
        )


    users = User.objects.filter(

        username__in=usernames
    )


    user_map = {

        user.username: user

        for user in users
    }


    for username in usernames:

        if username not in user_map:

            raise ValidationError(
                "User not found."
            )



    # -------------------------
    # Create Split
    # -------------------------


    split = SplitPayment.objects.create(

        created_by=created_by,

        total_amount=total_amount,

        title=title
    )



    # -------------------------
    # EQUAL SPLIT
    # -------------------------


    if split_type == "EQUAL":


        total_people = len(members) + 1


        base_share = (

            total_amount / total_people

        ).quantize(
            Decimal("0.01")
        )


        creator_share = (

            total_amount
            -
            (
                base_share
                *
                len(members)
            )
        )


        SplitMember.objects.create(

            split=split,

            user=created_by,

            share_amount=creator_share,

            is_payer=True
        )



        for member_data in members:


            user = user_map[
                member_data["username"]
            ]


            invoice = create_invoice(

                created_by=created_by,

                payer=user,

                amount=base_share,

                description=title
            )


            SplitMember.objects.create(

                split=split,

                user=user,

                share_amount=base_share,

                invoice=invoice
            )



    # -------------------------
    # CUSTOM SPLIT
    # -------------------------


    elif split_type == "CUSTOM":


        others_total = Decimal("0")


        for member_data in members:


            if "amount" not in member_data:

                raise ValidationError(
                    "Amount required for custom split."
                )


            amount = member_data[
                "amount"
            ]


            if amount <= 0:

                raise ValidationError(
                    "Split amount must be positive."
                )


            others_total += amount



        creator_share = (

            total_amount
            -
            others_total
        )


        if creator_share < 0:

            raise ValidationError(
                "Split amount exceeds total."
            )



        SplitMember.objects.create(

            split=split,

            user=created_by,

            share_amount=creator_share,

            is_payer=True
        )



        for member_data in members:


            user = user_map[
                member_data["username"]
            ]


            amount = member_data[
                "amount"
            ]


            invoice = create_invoice(

                created_by=created_by,

                payer=user,

                amount=amount,

                description=title
            )


            SplitMember.objects.create(

                split=split,

                user=user,

                share_amount=amount,

                invoice=invoice
            )



    else:

        raise ValidationError(
            "Invalid split type."
        )



    return split