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

# Set new password for admin
admin_user = User.objects.get(username='admin')
new_password = 'Admin@2025'
admin_user.set_password(new_password)
admin_user.save()

print(f"✓ Mot de passe réinitialisé pour l'utilisateur 'admin'")
print(f"✓ Nouveau mot de passe: {new_password}")
print(f"✓ Veuillez vous connecter avec:")
print(f"  - Email/Username: admin")
print(f"  - Mot de passe: {new_password}")
