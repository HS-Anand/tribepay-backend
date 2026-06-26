from django.urls import path
from .views import (
    AddMoneyView,
    LeaveGroupView, 
    MyWalletsView, 
    CreateGroupWalletView, 
    JoinGroupView, 
    ApproveJoinRequestView, 
    MyGroupsView,
    GroupMembersView,
    GroupTransactionsView,
    PendingJoinRequestsView,
    RejectJoinRequestView,
    RemoveMemberView,
    GroupCashRequestView,
    GroupLimitView,
    SmartPaymentView
)


urlpatterns = [
    path("me/", MyWalletsView.as_view()),
    path("add-money/", AddMoneyView.as_view()),

    path("group/create/",CreateGroupWalletView.as_view()),
    path("group/join/",JoinGroupView.as_view()),
    path("group/approve/",ApproveJoinRequestView.as_view()),
    path("groups/", MyGroupsView.as_view()),
    path("group/<uuid:wid>/members/", GroupMembersView.as_view()),
    path("group/<uuid:wid>/transactions/",GroupTransactionsView.as_view()),
    path("group/<uuid:wid>/requests/", PendingJoinRequestsView.as_view()),
    path("group/reject/", RejectJoinRequestView.as_view()),
    path("group/leave/",LeaveGroupView.as_view()),
    path("group/remove-member/",RemoveMemberView.as_view()),
    path("group/cash-invoice-raise/",GroupCashRequestView.as_view()),
    path("group/set-spending-limit/",GroupLimitView.as_view()),
    
    path("smart-payment/", SmartPaymentView.as_view(), name="smart-payment"),
]