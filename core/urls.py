
from django.urls import path, include
from .views import (
    HomeView, CheckoutView,ItemDetailView, 
    add_to_cart,remove_from_cart,OrderSummaryView,
    remove_single_from_cart, add_to_cartt,
    remove_from_cartt, PaymentView,
    record_payment, payment_success,AddCoupon,RequestRefund,
    initiate_payment, VerifyPaymentView,search,posts_by_category,CustomerSupportView,about,policy

    )



app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='index'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('search/', search, name='search'),
    path('about/', about, name='about'),
    path('policy/', policy, name='policy'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('product/<slug>/', ItemDetailView.as_view(), name='product'),
    path('add-coupon/', AddCoupon.as_view(), name='add-coupon'),
    path('add-to-cart/<slug>/', add_to_cart, name='add-to-cart'),
    path('category/<slug:slug>/', posts_by_category, name='posts-by-category'),
    path('add-to-cartt/<slug>/', add_to_cartt, name='add-to-cartt'),
    path('remove-from-cart/<slug>/', remove_from_cart, name='remove-from-cart'),
    path('remove-from-cartt/<slug>/', remove_from_cartt, name='remove-from-cartt'),
    path('remove-item-from-cart/<slug>/', remove_single_from_cart, name='remove-single-from-cart'),
    path('initiate-payment/', initiate_payment, name='initiate-payment'),
    path('verify_payment/', VerifyPaymentView.as_view(), name='verify-payment'),
    path('payment/<payment_option>', PaymentView.as_view(), name='payment'),
    path('record-payment/',record_payment, name='record-payment'),
    path('payment-success/', payment_success, name='payment-success'),
    path('customer-support/', CustomerSupportView.as_view(), name='customer-support'),

    path('refund-request/', RequestRefund.as_view(), name='refund-request'),



]