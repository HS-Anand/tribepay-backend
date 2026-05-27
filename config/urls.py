
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/transactions/", include("apps.transactions.urls")),
    path("api/auth/", include("apps.authentication.urls")),
    path("wallets/", include("apps.wallets.urls")),
]
