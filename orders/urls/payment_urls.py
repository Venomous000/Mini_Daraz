from django.urls import path
from orders.views.payment_views import start_payment, fake_stripe_checkout

urlpatterns = [
    path("start-payment/", start_payment, name="start_payment"),
    path("fake-stripe/<str:mode>/", fake_stripe_checkout, name="fake_stripe_checkout"),
]   