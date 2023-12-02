from django.contrib import admin
from .models import PurchaseOrder, Vendor, HistoricalPerformance


admin.site.register(Vendor)
admin.site.register(PurchaseOrder)
