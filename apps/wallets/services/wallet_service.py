from apps.wallets.models import Wallet, WalletMembership


def create_personal_wallet(user):

    wallet = Wallet.objects.create(
        wallet_type="PRS"
    )

    WalletMembership.objects.create(
        user=user,
        wallet=wallet,
        role="OWNER"
    )

    return wallet