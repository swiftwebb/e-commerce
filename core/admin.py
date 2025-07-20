from django.contrib import admin
from .models import Item, Order, OrderItem,Payment,Coupon,Refund,Address,Cats

def make_refund_accepted(ModelAdmin, request, queryset):
    queryset.update(refund_requested=False, refund_granted=True)
make_refund_accepted.short_dscription = "Update order to refund grant"

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user','ordered',
                    'being_delivered',
                    'recieved',
                    'refund_requested',
                    'refund_granted','billing_address','shipping_address',  'payment','coupon'
                    ]
    list_display_links = ['user','shipping_address', 'billing_address', 'payment','coupon']
    list_filter = ['ordered',
                    'being_delivered',
                    'recieved',
                    'refund_requested',
                    'refund_granted']
    search_fields = ['user__username', 'ref_code']
    actions = [make_refund_accepted]

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['user','ordered']


class AddressAdmin(admin.ModelAdmin):
    list_display = [
         'user','street_address', 'apartment_address', 'country', 'zip','address_type' ,'default'
    ]
    list_filter= ['user', 'default','country']
    search_fields = ['user', 'street_address', 'apartment_address', 'zip']


# Register your models here.
admin.site.register(Item)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(Cats)

