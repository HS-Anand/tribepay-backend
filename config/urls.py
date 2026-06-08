
from django.contrib import admin
from django.urls import path, include

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView
)

urlpatterns = [
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    path("admin/", admin.site.urls),
    path("api/transactions/", include("apps.transactions.urls")),
    path("api/auth/", include("apps.authentication.urls")),
    path("wallets/", include("apps.wallets.urls")),
    path("invoices/", include("apps.invoices.urls")),
    path("splits/",include("apps.splits.urls")),
    path("settlements/", include("apps.settlements.urls")),
    path("api/notifications/",include("apps.notifications.urls")),
]
