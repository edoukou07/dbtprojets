#!/usr/bin/env python3
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
sys.path.insert(0, r'c:\Users\hynco\Desktop\DWH_SIG\bi_app\backend')
django.setup()

from django.contrib.auth.models import User

# Get or create and update admin user
user, created = User.objects.get_or_create(username='admin')
user.set_password('admin')
user.is_superuser = True
user.is_staff = True
user.save()

print(f"✅ Admin user configured: {user.username} (password: admin)")
