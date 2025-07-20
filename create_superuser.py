# create_superuser.py
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "blog.settings")  # update this
django.setup()

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if username and email and password:
    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser {username}...")
        User.objects.create_superuser(username=username, email=email, password=password)
    else:
        print(f"Superuser {username} already exists.")
else:
    print("Missing superuser environment variables. Skipping...")
