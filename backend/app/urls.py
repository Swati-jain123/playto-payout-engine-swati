from django.contrib import admin
from django.urls import path
from app.views.payout import PayoutRequestView, PayoutStatusView, MerchantBalanceView
from app.views.dashboard import DashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/payouts/', PayoutRequestView.as_view(), name='payout-create'),
    path('api/v1/payouts/<int:payout_id>/', PayoutStatusView.as_view(), name='payout-status'),
    path('api/v1/balance/', MerchantBalanceView.as_view(), name='merchant-balance'),
    path('api/v1/dashboard/', DashboardView.as_view(), name='dashboard'),
]