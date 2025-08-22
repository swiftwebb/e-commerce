# core/adapter.py
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model
from allauth.exceptions import ImmediateHttpResponse
from django.shortcuts import redirect
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse

class MySocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Check if the social account email exists
        if sociallogin.is_existing:
            return

        try:
            # Get the email from the social account
            email = sociallogin.account.extra_data.get('email')

            # Find a user with a matching email
            user = get_user_model().objects.get(email=email)

            # If a user is found, connect the social account to the existing user
            sociallogin.connect(request, user)

            # Redirect to the home page or a success URL
            raise ImmediateHttpResponse(redirect(reverse('core:home')))

        except get_user_model().DoesNotExist:
            # If no user with that email is found, proceed with standard signup flow
            pass
        except Exception as e:
            # Handle other potential errors gracefully
            print(f"Error in social login adapter: {e}")
            raise