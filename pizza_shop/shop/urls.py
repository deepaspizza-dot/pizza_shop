from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('menu/', views.menu, name='menu'),
    path('contact/', views.contact, name='contact'),
    path('order/<int:pizza_id>/', views.order_pizza, name='order_pizza'),

     # 🛒 Cart system
    path('add/<int:pizza_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('remove/<str:key>/', views.remove_from_cart, name='remove_from_cart'),
    path('update/<str:key>/<str:action>/', views.update_cart, name='update_cart'),
    path('payment/', views.payment, name='payment'),
    path('success/', views.order_success, name='success'),
    path('invoice/', views.download_invoice, name='invoice'),
    
]

    

