from django.urls import path
from . import views

urlpatterns = [
    path('initiate_payment/', views.initiate_payment, name='initiate_payment'), 
    path('payment_success/', views.payment_success, name='payment_success'),  
    path('payment_fail/', views.payment_fail, name='payment_fail'), 
    path('payment_cancel/', views.payment_cancel, name='payment_cancel'), 
    # path('payment_error/', views.payment_error, name='payment_error'),  
]
