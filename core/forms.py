from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget


PAYMENT_CHOICES = (
   ('S','stripe'),
   ('PS','paystack'),

)
class CheckoutForm(forms.Form):
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False,)
    shipping_country = CountryField(blank_label = '(select country)').formfield(required = False,widet=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100',
    
})
)
    shipping_zip = forms.CharField(required=False)



    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False,)
    billing_country = CountryField(blank_label = '(select country)').formfield(required = False,widet=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100',
    
})
)
    billing_zip = forms.CharField(required=False)
    same_billing_address= forms.BooleanField(required=False)
    set_default_shipping = forms.BooleanField(required=False)

    use_default_shipping = forms.BooleanField(required=False)
    set_default_billing = forms.BooleanField(required=False)

    use_default_billing = forms.BooleanField(required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect,choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':"Promo code",
        'aria-label' :"Promo code",
        'aria-describedby':"button-addon2"

    }))


class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4,
    }))
    email = forms.EmailField()


class CustomerSupportForm(forms.Form):
    first_name = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4,'class' :"col-lg-4 col-md-12 mb-4",
        'placeholder':'First name'
    }))
    last_name = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4,'class' :"col-lg-4 col-md-12 mb-4",'placeholder':'Last name'
    }))
    subject = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs={
        'rows': 4, 
    }))
    email = forms.EmailField()



# # forms.py
# from django import forms

# class PaystackForm(forms.Form):
#     email = forms.EmailField()
#     amount = forms.FloatField()
