#!/usr/bin/env python
"""Test script to verify alerts API response"""

import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sigeti_bi.settings')
sys.path.insert(0, '/c/Users/hynco/Desktop/DWH_SIG/bi_app/backend')

django.setup()

from analytics.models import Alert
from api.serializers import AlertSerializer
import json

# Get alerts from database
print("=" * 60)
print("TESTING ALERTS API")
print("=" * 60)

alerts_count = Alert.objects.count()
print(f"\n✓ Total alerts in database: {alerts_count}")

# Get first 5 alerts
alerts = Alert.objects.all()[:5]
print(f"✓ Retrieved {alerts.count()} alerts")

# Serialize them
serializer = AlertSerializer(alerts, many=True)
data = serializer.data

print("\n" + "=" * 60)
print("SERIALIZED DATA STRUCTURE:")
print("=" * 60)
print(json.dumps(data, indent=2, default=str))

print("\n" + "=" * 60)
print("EACH ALERT HAS FIELDS:")
print("=" * 60)
if data:
    print(json.dumps(data[0], indent=2, default=str))
    print(f"\nKeys: {list(data[0].keys())}")

print("\n" + "=" * 60)
print("API RESPONSE FORMAT (what frontend receives):")
print("=" * 60)
print(f"Type: {type(data)}")
print(f"Is list: {isinstance(data, list)}")
print(f"Length: {len(data)}")
