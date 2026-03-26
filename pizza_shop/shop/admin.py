from django.contrib import admin
from .models import Pizza, Order


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'pizza', 'size', 'quantity', 'total_price', 'status')
    list_filter = ('status',)


admin.site.register(Pizza)
admin.site.register(Order, OrderAdmin)