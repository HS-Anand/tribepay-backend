from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

from apps.wallets.models import (
    WalletMembership,
    GroupJoinRequest
)

from apps.wallets.services.group_wallet_service import (
    create_group_wallet,
    request_join_group,
    approve_join_request,
    leave_group
)


User = get_user_model()


class GroupLifecycleTest(TestCase):

    def setUp(self):

        self.owner = User.objects.create_user(
            username="owner",
            phone_number="1111111111",
            password="1234"
        )

        self.member = User.objects.create_user(
            username="member",
            phone_number="2222222222",
            password="1234"
        )

        self.group = create_group_wallet(
            user=self.owner,
            group_name="Trip"
        )

    def test_user_can_rejoin_after_leaving_group(self):

        print(
            "\n\n===== TEST: GROUP REJOIN LIFECYCLE VALIDATION ====="
        )

        first_request = request_join_group(
            user=self.member,
            group_code=self.group.group_code
        )

        approve_join_request(
            owner_user=self.owner,
            request_id=first_request.rid
        )

        self.assertTrue(
            WalletMembership.objects.filter(
                user=self.member,
                wallet=self.group
            ).exists()
        )

        leave_group(
            user=self.member,
            group_id=self.group.wid
        )

        self.assertFalse(
            WalletMembership.objects.filter(
                user=self.member,
                wallet=self.group
            ).exists()
        )

        second_request = request_join_group(
            user=self.member,
            group_code=self.group.group_code
        )

        self.assertEqual(second_request.status, "PENDING")

        self.assertEqual(first_request.rid, second_request.rid)

        self.assertEqual(
            GroupJoinRequest.objects.filter(
                requested_user=self.member,
                wallet=self.group
            ).count(),
            1
        )

    def test_only_owner_can_approve_join_requests(self):

        print(
            "\n\n===== TEST: GROUP OWNER PERMISSION ENFORCEMENT ====="
        )

        user3 = User.objects.create_user(
            username="user3",
            phone_number="3333333333",
            password="1234"
        )

        first_request = request_join_group(
            user=self.member,
            group_code=self.group.group_code
        )

        approve_join_request(
            owner_user=self.owner,
            request_id=first_request.rid
        )

        second_request = request_join_group(
            user=user3,
            group_code=self.group.group_code
        )

        with self.assertRaises(ValidationError):

            approve_join_request(
                owner_user=self.member,
                request_id=second_request.rid
            )

        self.assertFalse(
            WalletMembership.objects.filter(
                user=user3,
                wallet=self.group
            ).exists()
        )

        second_request.refresh_from_db()

        self.assertEqual(second_request.status, "PENDING")