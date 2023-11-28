from django.urls import path
from .views import (
    index,
    VendorListCreateView,
    VendorRetrieveUpdateDestroyView,
    PurchaseOrderListCreateView,
    PurchaseOrderRetrieveUpdateDestroyView,
    VendorPerformanceView,
)

urlpatterns = [
    path('', index, name='index'),

    # Vendor Profile Management
    path('api/vendors/', VendorListCreateView.as_view(), name='create-vendor'),
    path('api/vendors/<int:pk>/', VendorRetrieveUpdateDestroyView.as_view(), name='vendor-detail'),

    # Purchase Order Tracking
    path('api/purchase_orders/', PurchaseOrderListCreateView.as_view(), name='create-purchase-order'),
    path('api/purchase_orders/<int:pk>/', PurchaseOrderRetrieveUpdateDestroyView.as_view(), name='purchase-order-detail'),

    # Vendor Performance Evaluation
    path('api/vendors/<int:pk>/performance/', VendorPerformanceView.as_view(), name='vendor-performance'),
]
