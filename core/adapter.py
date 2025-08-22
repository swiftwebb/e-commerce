# core/adapter.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.urls import reverse

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return

        email = (sociallogin.account.extra_data or {}).get("email")
        if not email:
            return

        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return

        # Safely connect this login with the existing user
        sociallogin.connect(request, user)

        # Redirect to the correct home/index page
        raise ImmediateHttpResponse(redirect(reverse("core:index")))
