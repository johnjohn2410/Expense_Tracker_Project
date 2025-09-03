from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.routers import DefaultRouter

from .views import (
    AccountViewSet,
    AttachmentViewSet,
    BudgetPeriodViewSet,
    BudgetViewSet,
    CategoryViewSet,
    DashboardViewSet,
    ImportViewSet,
    RuleViewSet,
    TransactionViewSet,
    UserProfileViewSet,
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"accounts", AccountViewSet, basename="account")
router.register(r"transactions", TransactionViewSet, basename="transaction")
router.register(r"budgets", BudgetViewSet, basename="budget")
router.register(r"budget-periods", BudgetPeriodViewSet, basename="budgetperiod")
router.register(r"rules", RuleViewSet, basename="rule")
router.register(r"attachments", AttachmentViewSet, basename="attachment")
router.register(r"imports", ImportViewSet, basename="import")
router.register(r"user-profiles", UserProfileViewSet, basename="userprofile")
router.register(r"dashboard", DashboardViewSet, basename="dashboard")

# API URL patterns
urlpatterns = [
    # Router URLs
    path("", include(router.urls)),
    # Authentication
    path("auth/", include("rest_framework.urls")),
    # API Schema and Documentation
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
