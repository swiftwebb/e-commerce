# core/adapter.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from django.urls import reverse

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # If already linked, do nothing
        if sociallogin.is_existing:
            return

        # Be defensive: some providers may not return email
        email = (sociallogin.account.extra_data or {}).get("email")
        if not email:
            return  # Let allauth proceed with normal flow

        try:
            user = get_user_model().objects.get(email=email)
        except get_user_model().DoesNotExist:
            return  # Let allauth create a new user

        # Link social to existing user and redirect
        sociallogin.connect(request, user)
        raise ImmediateHttpResponse(redirect(reverse("core:home")))
