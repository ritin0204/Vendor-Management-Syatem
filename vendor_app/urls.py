from django.urls import path
from .views import (
    index,
    acknowledge_purchase_order,
    VendorListCreateView,
    VendorRetrieveUpdateDestroyView,
    PurchaseOrderListCreateView,
    PurchaseOrderView,
    VendorPerformanceView,
)

urlpatterns = [
    path('', index, name='index'),

    # Vendor Profile Management
    path('api/vendors/', VendorListCreateView.as_view(), name='create-vendor'),
    path('api/vendors/<int:pk>/',
         VendorRetrieveUpdateDestroyView.as_view(),
         name='vendor-detail'),

    # Vendor Performance Evaluation
    path('api/vendors/<int:vendor>/performance/',
         VendorPerformanceView.as_view(),
         name='vendor-performance'),

    # Purchase Order Tracking
    path('api/purchase_orders/',
         PurchaseOrderListCreateView.as_view(),
         name='create-purchase-order'),
    path('api/purchase_orders/<int:pk>/',
         PurchaseOrderView.as_view(),
         name='purchase-order-detail'),
    path('api/purchase_orders/<int:pk>/acknowledge',
         view=acknowledge_purchase_order,
         name='acknowledge_purchase_order'),
]
