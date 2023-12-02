from .models import Vendor, PurchaseOrder
from django.db.models import Q


def update_on_time_delivery_rate(pk, on_time):
    purchase_order = PurchaseOrder.objects.get(pk=pk)
    vendor = purchase_order.vendor

    new_completed_order = 1 if on_time else 0
    total_completed_orders = PurchaseOrder.objects.filter(
        Q(vendor=vendor.id,status='COMPLETED')
    ).count()
    old_delivery_rate = vendor.on_time_delivery_rate

    if total_completed_orders == 0:
        return

    if old_delivery_rate is not None:
        previous_ontime_completed = (
            old_delivery_rate*(total_completed_orders-1)
        )

        new_delivery_rate = (
            (previous_ontime_completed
             + new_completed_order) / total_completed_orders
        )

        vendor.on_time_delivery_rate = new_delivery_rate
    else:
        vendor.on_time_delivery_rate = (
            new_completed_order/total_completed_orders
        )

    vendor.save()


def update_fulfillment_rate(pk):
    purchase_order = PurchaseOrder.objects.get(pk=pk)
    vendor = purchase_order.vendor

    total_orders = PurchaseOrder.objects.filter(
        Q(vendor=vendor.id)
    )
    total_orders_count = total_orders.count()
    total_completed_count = total_orders.filter(Q(status='COMPLETED')).count()

    if total_completed_count == 0:
        return

    vendor.fulfillment_rate = total_completed_count/total_orders_count
    vendor.save()


def update_average_response_time(pk):
    pass


def update_quality_rating_avg(pk):
    purchase_order = PurchaseOrder.objects.get(pk=pk)
    vendor = purchase_order.vendor

    old_quality_rate = vendor.quality_rating_avg
    new_quality_score = purchase_order.quality_rating

    if old_quality_rate is None:
        vendor.quality_rating_avg = new_quality_score
        vendor.save()
        return

    total_completed_orders = PurchaseOrder.objects.filter(
        Q(vendor=vendor.id,status='COMPLETED')
    ).count()

    previous_total_quality = old_quality_rate*(total_completed_orders - 1)

    vendor.quality_rating_avg = (
        (previous_total_quality+new_quality_score)/total_completed_orders
    )
    vendor.save()
