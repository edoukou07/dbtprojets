#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys, django
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'bi_app', 'backend'))
os.environ['DJANGO_SETTINGS_MODULE'] = 'sigeti_bi.settings'
django.setup()

from django.core.cache import cache
from django.db import connection

print("=== Clearing all caches ===")
cache.clear()
print("✓ Django cache cleared")

# Test the API response manually
print("\n=== Testing by_zone endpoint response ===")
from api.views import OccupationViewSet
from django.test import RequestFactory
from rest_framework.request import Request

factory = RequestFactory()
django_request = factory.get('/api/occupation/by_zone/')
request = Request(django_request)

viewset = OccupationViewSet()
viewset.request = request
response = viewset.by_zone(request)

print(f"Response status: {response.status_code}")
print(f"Response data (first zone): {response.data[0] if response.data else 'No data'}")
print(f"\nFields in response: {list(response.data[0].keys()) if response.data else 'None'}")

# Verify lots_reserves is included
if response.data and 'lots_reserves' in response.data[0]:
    print("\n✓ lots_reserves field is now in the API response!")
    for zone in response.data[:3]:
        print(f"  {zone['nom_zone']}: reserves={zone.get('lots_reserves')}")
else:
    print("\n✗ lots_reserves NOT found in response!")
