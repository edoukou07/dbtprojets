#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.chdir('bi_app/backend')
sys.path.insert(0, os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
django.setup()

from django.contrib.auth.models import User

print("\n=== USERS IN DATABASE ===")
users = User.objects.all()
for u in users:
    print(f"{u.username:20} | {u.email:30} | Active: {u.is_active} | Staff: {u.is_staff}")

if not users.exists():
    print("No users found!")
