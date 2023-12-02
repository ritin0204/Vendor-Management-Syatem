from rest_framework import serializers
from .models import Vendor, PurchaseOrder, HistoricalPerformance
from django.utils import timezone


class VendorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'name', 'contact_details', 'address', 'vendor_code']


class VendorPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = ['id', 'vendor_code', 'on_time_delivery_rate', 'quality_rating_avg',
                  'average_response_time', 'fulfillment_rate']

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PurchaseOrderSerializer(serializers.ModelSerializer):
    status = serializers.CharField(default='PENDING')
    order_date = serializers.DateTimeField(default=timezone.now)
    delivery_date = serializers.DateTimeField(
        default=timezone.now() + timezone.timedelta(days=7))
    acknowledgment_date = serializers.DateTimeField(default=None)
    quality_rating = serializers.FloatField(default=0.0)

    class Meta:
        model = PurchaseOrder
        # In future remove 'issue_date' from this field
        fields = '__all__'
        read_only_fields = [
            'status', 'order_date', 'delivery_date',
            'acknowledgment_date', 'quality_rating'
        ]

    def update(self, instance, validated_data):
        if validated_data.get('status', None) == 'COMPLETED':
            validated_data['delivery_date'] = timezone.now()
        return super().update(instance, validated_data)


class HistoricalPerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistoricalPerformance
        fields = '__all__'
