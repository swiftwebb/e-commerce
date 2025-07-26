from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from .models import Item, Order, OrderItem, Address, Payment,Coupon,Refund, Cats,CustomerSupport
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from .forms import CheckoutForm,CouponForm,RefundForm,CustomerSupportForm
from django.db.models import Count, Q
from django.conf import settings
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY
import random
import string

def create_ref_code():
    return ' '.join(random.choices(string.ascii_lowercase + string.digits, k=20))
# Create your views here.




def is_valid_form(value):
    valid = True
    for field in value:
        if field == '':
            valid = False
    return valid




def  products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request,'home.html',context)



class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order':order,
                'couponform':CouponForm(),
                "DISPLAY_FORM": True
            }
            shipping_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 'S',
                default = True
            )
            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})
            
            billing_address_qs = Address.objects.filter(
                user = self.request.user,
                address_type = 'B',
                default = True
            )
            if billing_address_qs.exists():
                context.update({'default_billing_address': billing_address_qs[0]})
            
            
            return render(self.request,'checkout.html',context)
            


        except ObjectDoesNotExist:
            messages.info(self.request, "you do not have an active order")
            return redirect('core:checkout')

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get('use_default_shipping')
                if use_default_shipping:

                    address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type = 'S',
                        default = True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address =shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "no default shipping address available")
                        return redirect ("core:checkout")
                else:
                    
                


                    shipping_address1 = form.cleaned_data.get('shipping_address')
                    shipping_address2 = form.cleaned_data.get('shipping_address2')
                    shipping_country =  form.cleaned_data.get('shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')
                    if is_valid_form([shipping_address1,shipping_country,shipping_zip]):
                    
                        shipping_address = Address(
                            user = self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                            address_type = "S"
                        )
                        shipping_address.save()
                        order.shipping_address = shipping_address
                        order.save()
                        set_default_shipping =form.cleaned_data.get('set_default_shipping') 
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                    
                    else:
                        messages.info(self.request, "please fill in the shipping address")
                



                use_default_billing = form.cleaned_data.get('use_default_billing')
                same_billing_address = form.cleaned_data.get('same_billing_address')
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk =None
                    billing_address.save()
                    billing_address.address_type = "B"
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                    
                elif use_default_billing:

                    address_qs = Address.objects.filter(
                        user = self.request.user,
                        address_type = 'B',
                        default = True
                    )
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "no default billing address available")
                        return redirect ("core:checkout")
                else:
                    
                


                    billing_address1 = form.cleaned_data.get('billing_address')
                    billing_address2 = form.cleaned_data.get('billing_address2')
                    billing_country = form.cleaned_data.get('billing_country')
                    billing_zip = form.cleaned_data.get('billing_zip')
                    if is_valid_form([billing_address1,billing_country,billing_zip]):
                    
                        billing_address = Address(
                            user = self.request.user,
                            street_address=billing_address1,
                            apartment_address=billing_address2,
                            country=billing_country,
                            zip=billing_zip,
                            address_type = "B"
                        )
                        billing_address.save()
                        order.billing_address = billing_address
                        order.save()
                        set_default_billing =form.cleaned_data.get('set_default_billing') 
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                    
                    else:
                        messages.info(self.request, "please fill in the shipping address")
                



                payment_option = form.cleaned_data.get('payment_option')
                if payment_option == 'S':
                    return redirect ("core:payment", payment_option='stripe')
                if payment_option =='P':
                    return redirect ("core:payment", payment_option='paypal')
                if payment_option =='PS':
                    return redirect("core:initiate-payment")
                    # return redirect ("core:payment", payment_option='Paystack')
                return redirect ("core:checkout")
            messages.warning(self.request, "Failed checkout")
        except ObjectDoesNotExist:
            messages.warning(self.request, "you do not have an active order")
            return redirect('core:order-summary')

      

def get_category_count():
    queryset = Item.objects \
        .values('cats__title') \
        .annotate(Count('cats__title'))
    return queryset

# class HomeView(ListView):
#     model = Item, Cats
#     paginate_by = 10
#     template_name = 'home.html'

class HomeView(ListView):
    model = Item
    template_name = 'home.html'
    context_object_name = 'object_list'
    paginate_by = 100

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cats'] = Cats.objects.all()
        return context


def search(request):
    queryset = Item.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query)|
            Q(price__icontains=query)|
            Q(discount_price__icontains=query)

        ).distinct()
    context = {
        'queryset': queryset
    }
    return render(request, 'search_result.html', context)


def posts_by_category(request, slug):
    category = get_object_or_404(Cats, slug=slug)
    items = Item.objects.filter(cats=category).order_by('-timestamp')

    context = {
        'category': category,
        'items': items,
    }
    return render(request, 'posts_by_category.html', context)











class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object':order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "you do not have an active order")
            return redirect('/')



class ItemDetailView(DetailView):
    model = Item
    template_name = 'product.html'


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    
    # Find any existing un-ordered OrderItem for this user+item
    order_item_qs = OrderItem.objects.filter(
        item=item,
        user=request.user,
        ordered=False
    )
    
    if order_item_qs.exists():
        order_item = order_item_qs.first()
    else:
        order_item = OrderItem.objects.create(
            item=item,
            user=request.user,
            ordered=False,
            quantity=1
        )

    # Get the active order
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs.first()
        # Check if this item is already in the order
        if order.items.filter(item__slug=item.slug).exists():

            # Increment quantity
            if order_item.quantity + 1 > item.quantity:
                messages.warning(request, f"We have {item.quantity} '{item.title}' in stock.")
                return redirect("core:order-summary")
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
    else:
        # No order yet: create one and add the item
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date
        )
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
    
    return redirect("core:product", slug=slug)

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Check if this order has this item
        if order.items.filter(item__slug=item.slug).exists():
            # Get the existing order item
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            ).first()
            if order_item:
                order.items.remove(order_item)
                order_item.delete()
                messages.info(request, "This item was removed from your cart.")
            else:
                messages.warning(request, "Could not find this item in your order.")
            return redirect("core:product", slug=slug)
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)










@login_required
def remove_single_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Check if this order has this item
        if order.items.filter(item__slug=item.slug).exists():
            # Get the existing order item
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            ).first()
            if order_item .quantity >1:
                order_item.quantity -= 1
                order_item.save()
                messages.info(request, "This item quantity was updated ")
            else:
                order.items.remove(order_item)
                order_item.delete()
            
            messages.info(request, "This item quantity was updated ")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product", slug=slug)






@login_required
def add_to_cartt(request, slug):
    item = get_object_or_404(Item, slug=slug)
    
    # Find any existing un-ordered OrderItem for this user+item
    order_item_qs = OrderItem.objects.filter(
        item=item,
        user=request.user,
        ordered=False
    )
    
    if order_item_qs.exists():
        order_item = order_item_qs.first()
    else:
        order_item = OrderItem.objects.create(
            item=item,
            user=request.user,
            ordered=False,
            quantity=1
        )

    # Get the active order
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs.first()
        # Check if this item is already in the order
        if order.items.filter(item__slug=item.slug).exists():
            # Increment quantity
            if order_item.quantity + 1 > item.quantity:
                messages.warning(request, f"we have{item.quantity} '{item.title}' in stock.")
                return redirect("core:order-summary")

            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        # No order yet: create one and add the item
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user,
            ordered_date=ordered_date
        )
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")
    






@login_required
def remove_from_cartt(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # Check if this order has this item
        if order.items.filter(item__slug=item.slug).exists():
            # Get the existing order item
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            ).first()
            if order_item:
                order.items.remove(order_item)
                order_item.delete()
                messages.info(request, "This item was removed from your cart.")
            else:
                messages.warning(request, "Could not find this item in your order.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:order-summary")
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:order-summary")





def payment_success(request):
        messages.success(request, "Your payment was successful!")
        return redirect("/")

class PaymentView(LoginRequiredMixin, View):

    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            try:
                order = Order.objects.get(user=self.request.user, ordered=False)
                for order_item in order.items.all():
                    if order_item.quantity > order_item.item.quantity:
                        messages.warning(self.request, f"we have {order_item.item.quantity}  '{order_item.item.title}'  available in stock.")
                        return redirect("core:order-summary")
            except Order.DoesNotExist:
                return redirect("core:order-summary")

            amount = int(order.get_total() * 100)

            try:
                intent = stripe.PaymentIntent.create(
                    amount=amount,
                    currency='usd',
                    metadata={'user_id': self.request.user.id},
                )
            except stripe.error.CardError as e:
                body = e.json_body
                err = body.get('error', {})
                messages.warning(self.request, f"{err.get('message')}")
                return redirect("/")
            except stripe.error.RateLimitError as e:
                messages.warning(self.request, "Rate limit error")
                return redirect("/")
            except stripe.error.InvalidRequestError as e:
                messages.warning(self.request, "Invalid parameters")
                return redirect("/")
            except stripe.error.AuthenticationError as e:
                messages.warning(self.request, "Not authenticated")
                return redirect("/")
            except stripe.error.APIConnectionError as e:
                messages.warning(self.request, "Network error")
                return redirect("/")
            except stripe.error.StripeError as e:
                messages.warning(
                    self.request, "Something went wrong. You were not charged. Please try again."
                )
                return redirect("/")
            except Exception as e:
                messages.warning(
                    self.request, "A serious error occurred. We have been notified."
                )
                return redirect("/")

            context = {
                'order': order,
                "client_secret": intent.client_secret,
                "STRIPE_PUBLISHABLE_KEY": settings.STRIPE_PUBLISHABLE_KEY,
                "DISPLAY_FORM": False
            }
            return render(self.request, "payment2.html", context)
        else:
            messages.warning(self.request,"you have not added a billing address")
            return redirect("core:checkout")
    

    


from django.http import JsonResponse
import json
from django.http import JsonResponse
import json
from .models import Payment, Order

@login_required
def record_payment(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            payment_intent_id = data.get("payment_intent_id")
            amount = data.get("amount")
            user = request.user if request.user.is_authenticated else None

            # Create Payment
            payment = Payment.objects.create(
                stripe_charge_id=payment_intent_id,
                user=user,
                amount=amount
            )
           

            # Mark the user's active order as completed
            order = Order.objects.get(user=user, ordered=False)
            order.ordered = True
            order.payment = payment  # Link the payment
            order.ref_code = create_ref_code()
            order.ordered_date = timezone.now()  # optional
            order.save()


            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()
                item.item.quantity -= item.quantity
                item.item.save()

            return JsonResponse({"status": "success"})

        except Order.DoesNotExist:
            return JsonResponse({"error": "No active order found."}, status=404)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request"}, status=400)

def get_coupon(request,code):
    try:
        coupon = Coupon.objects.get(code=code)
        return coupon


    except ObjectDoesNotExist:
        messages.info(request, "this coupon does not exist")
        return redirect('core:checkout')


class AddCoupon(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user= self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "successfully added coupon")
                return redirect('core:checkout')


            except ObjectDoesNotExist:
                messages.info(self.request, "you do not have an active order")
                return redirect('core:checkout')






class RequestRefund(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form':form
        }
        return render (self.request, "refund_request.html", context)
    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()

                refund =Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.info(self.request, 'your request was recieved')
                return redirect("core:refund-request")
            except ObjectDoesNotExist:
                messages.info(self.request,'this order does not exist')
                return redirect("core:refund-request")


def about(request):
    return render(request, "about.html",{})

def policy(request):
    return render(request, "policy.html",{})
          
class CustomerSupportView(View):
    def get(self, *args, **kwargs):
        form = CustomerSupportForm()
        context = {
            'form':form
        }
        return render (self.request, "customer_support.html", context)
    def post(self, *args, **kwargs):
        form = CustomerSupportForm(self.request.POST)
        if form.is_valid():
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            subject = form.cleaned_data.get('subject')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            try:
                customer =CustomerSupport()
                customer.first_name = first_name
                customer.last_name = last_name
                customer.subject = subject
                customer.message = message
                customer.email = email
                customer.save()
                messages.info(self.request, 'your message was recieved')
                return redirect("core:index")
            except ObjectDoesNotExist:
                messages.info(self.request,'not a valid message please fill the form well')
                return redirect("core:index")
  
            










from django.utils.crypto import get_random_string
from .utils import verify_payment
from .models import Payment


@login_required
def initiate_payment(request):

    order = Order.objects.get(user=request.user, ordered=False)
    amount = order.get_total()
    if order.items.exists():
        

        amount = int(order.get_total())
        for order_item in order.items.all():
            if order_item.quantity > order_item.item.quantity:
                messages.warning(request, f"We have {order_item.item.quantity} '{order_item.item.title}' available in stock.")
                return redirect("core:order-summary")

        ref = get_random_string(length=12).upper()

        # Create a Payment record
        Payment.objects.create(user=request.user, amount=amount, ref=ref)

        context = {
            "paystack_pub_key": settings.PAYSTACK_PUBLIC_KEY,
            "amount": int(amount * 100), 
            "ref": ref,
            "email": request.user.email,
            'order': order,
        }
        return render(request, "payment1.html", context)
    else:
        messages.warning(request,"no active order")
        return redirect("core:order-summary")



# class VerifyPaymentView(View):
#     def get(self, request, *args, **kwargs):
#         ref = request.GET.get("reference")

#         try:
#             payment = Payment.objects.filter(ref=ref).order_by('-timestamp').first()

#         except Payment.DoesNotExist:
#             messages.error(request, "Invalid transaction reference.")
#             return redirect("core:checkout")

#         if verify_payment(ref, payment.amount):
#             payment.verified = True
#             payment.email = self.request.user.email
#             payment.save()

#             order = Order.objects.get(user=request.user, ordered=False)
#             order.ordered = True
#             order.ref_code = create_ref_code()
#             order.ordered_date = timezone.now()
#             order.save()

#             order_items = order.items.all()
#             order_items.update(ordered = True)
#             for item in order_items:
#                 item.save()


#                 item.item.quantity -= item.quantity
#                 item.item.save()


#             messages.success(request, "Payment verified successfully!")
#             return redirect("core:index")
#         else:
#             messages.warning(request, "Payment verification failed.")
#             return redirect("core:checkout")


from django.http import HttpResponseServerError
import logging

logger = logging.getLogger(__name__)

class VerifyPaymentView(View):
    def get(self, request, *args, **kwargs):
        try:
            ref = request.GET.get("reference")
            user = request.user

            order = Order.objects.get(user=user, ordered=False)

            payment = Payment.objects.get(ref=ref, user=user)

            if verify_payment(ref, payment.amount):
                payment.verified = True
                payment.email = user.email
                payment.save()

                order.payment = payment
                order.ordered = True
                order.ref_code = create_ref_code()
                order.ordered_date = timezone.now()
                order.save()

                order_items = order.items.all()
                order_items.update(ordered=True)
                for item in order_items:
                    item.save()
                    item.item.quantity -= item.quantity
                    item.item.save()

                messages.success(request, "Payment verified and order completed!")
                return redirect("core:index")
            else:
                messages.warning(request, "Payment verification failed.")
                return redirect("core:checkout")

        except Exception as e:
            logger.exception("Error verifying payment")  # Logs full traceback
            return HttpResponseServerError(f"Server Error: {str(e)}")


