from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator 
# Create your models here.
from django.urls import reverse

from django_countries.fields import CountryField
from django.db.models.signals import post_save 


CATEGORY_CHOICES= (
    ('S','SHIRT'),
    ('SW','SportWear'),
    ('OW','OutWear')
)


LABEL_CHOICES= (
    ('P','primary'),
    ('S','secondary'),
    ('D','danger')
)

ADDRESS_CHOICES= (
    ('B','Billing'),
    ('S','Shipping'),
)
TYPE_CHOICES =(
    ('BN','BRAND NEW'),
    ('U','LOCAL USED' ),
    ('UK', 'UK USED'),
)
# class UserProfile(models.Model):
#     user = models.OneToOneField(
#         settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#     stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
#     one_click_purchasing = models.BooleanField(default=False)

#     def __str__(self):
#         return self.user.username
from django.utils.text import slugify 
class Cats(models.Model):
    title = models.CharField(max_length=30)
    slug = models.SlugField(unique=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)





class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    cats = models.ManyToManyField('Cats',blank=True)

    discount_price = models.FloatField(blank=True,null=True)
    category = models.CharField(choices= CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices= LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description =models.TextField()
    quantity = models.IntegerField(default=1,validators=[MinValueValidator(0)])
    image = models.ImageField()
    timestamp = models.DateTimeField(auto_now_add=True)
    type_phone = models.CharField(choices= TYPE_CHOICES, max_length=19)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse("core:product", kwargs={
            'slug':self.slug
        })
    def get_add_to_cart_url(self):
        return reverse("core:add-to-cart", kwargs={
            'slug':self.slug
        })

    def get_remove_from_cart_url(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug':self.slug
        })
    




class OrderItem(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    item = models.ForeignKey(Item, on_delete= models.CASCADE)
    quantity = models.IntegerField(default=1,validators=[MinValueValidator(0)])
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    def get_total_item_price(self):
        return self.quantity * self.item.price
    
    def get_total_discount_item_price(self):
        return self.quantity * self.item.discount_price
    def get_amount_saved(self):
        return self.get_total_item_price() - self.get_total_discount_item_price()
    
    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_item_price()
        return self.get_total_item_price()
    

   

    

class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    ref_code = models.CharField(max_length=20)
    items = models.ManyToManyField(OrderItem)
    Start_date= models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null=True, blank=True)
    ordered = models.BooleanField(default=False)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete = models.SET_NULL, blank = True, null = True)
    billing_address = models.ForeignKey('Address',  related_name='billing_address', on_delete = models.SET_NULL, blank = True, null = True)
    payment = models.ForeignKey('Payment', on_delete = models.SET_NULL, blank = True, null = True)
    coupon = models.ForeignKey('Coupon', on_delete = models.SET_NULL, blank = True, null = True)
    being_delivered  = models.BooleanField(default=False)
    recieved  = models.BooleanField(default=False)
    refund_requested  = models.BooleanField(default=False)
    refund_granted  = models.BooleanField(default=False)
    

    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount

        return total
    

class BillingAddress (models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete= models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False)

    zip = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.user.username
    






# class Payment(models.Model):
#     stripe_charge_id = models.CharField(max_length=50)
#     user = models.ForeignKey(settings.AUTH_USER_MODEL,
#                              on_delete=models.SET_NULL, blank=True, null=True)
#     amount = models.FloatField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.user.username
    

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50, blank=True, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.SET_NULL, blank=True, null=True)
    amount = models.FloatField()
    email = models.EmailField(blank=True, null=True)  # ✅ Add this line
    ref = models.CharField(max_length=100, blank=True, null=True)  # For Paystack
    verified = models.BooleanField(default=False)  # For Paystack
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
    

    def __str__(self):
        return self.user.username if self.user else "Anonymous Payment"










class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount= models.FloatField()
    def __str__(self):
        return self.code


class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete =models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"
    

class CustomerSupport(models.Model):
    first_name =models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    message = models.CharField(max_length=300)
    email = models.EmailField()



class Address(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple= False)
    zip = models.CharField(max_length=100)
    state = models.CharField(max_length=100, blank=True, null=True)
    address_type = models.CharField(max_length=1, choices = ADDRESS_CHOICES)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username
    

    class Meta:
        verbose_name_plural ='Addresses'
    

    



# def userprofile_receiver(sender, instance, created, *args, **kwargs):
#     if created:
#         userprofile = UserProfile.objects.create(user=instance)


# post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL)




# models.py
# class Payment(models.Model):
#     user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
#     amount = models.FloatField()
#     ref = models.CharField(max_length=100)
#     verified = models.BooleanField(default=False)
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.user.username} - {self.amount} - {self.ref}"
