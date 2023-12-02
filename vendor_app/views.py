from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, views, response, decorators, status, permissions
from .models import Vendor, PurchaseOrder
from .serializers import (
    VendorSerializer,
    VendorPerformanceSerializer,
    PurchaseOrderSerializer,
)
from . import utils


# Create your views here.
def index(request):
    return HttpResponse("I am The Home Page :)")


class VendorListCreateView(generics.ListCreateAPIView):
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser
    ]


class VendorPerformanceView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser
    ]
    # Helper Method to getOBject
    def get_object(self, pk):
        try:
            vender = Vendor.objects.get(pk)
            return vender
        except Vendor.DoesNotExist:
            return None

    def get(self, request, vendor, *args, **kwargs):
        vendor = self.get_object(vendor)
        serializer = VendorPerformanceSerializer(vendor)
        return response.Response(serializer.data, status=200)


class VendorRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser
    ]
    queryset = Vendor.objects.all()
    serializer_class = VendorSerializer


class PurchaseOrderListCreateView(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser
    ]

    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PurchaseOrderView(generics.RetrieveUpdateDestroyAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        permissions.IsAdminUser
    ]

    def perform_update(self, serializer) -> None:
        before_update_po = self.get_object()

        # Update the purchase order object
        super().perform_update(serializer)

        after_update_po = self.get_object()

        # Calculate Vendor Metrics
        if before_update_po.status != after_update_po.status:

            delivered_on_time = (
                before_update_po.delivery_date >= after_update_po.delivery_date
            )

            if after_update_po.status == 'COMPLETED':
                utils.update_on_time_delivery_rate(
                    pk=self.get_object().id, on_time=delivered_on_time)

            utils.update_fulfillment_rate(pk=self.get_object().id)

    def update(self, request, *args, **kwargs):
        '''
        This update function take update values through the api
        and updates the values as provided.

        for example: if request is to update the status,
        then also provide the updated delivery date.
        '''
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


@decorators.api_view(['POST', 'GET'])
@decorators.permission_classes([permissions.IsAuthenticated, permissions.IsAdminUser])
def acknowledge_purchase_order(request, pk):
    if request.method == 'POST':
        try:
            purchase_order = PurchaseOrder.objects.get(pk=pk)
            purchase_order.acknowledgment_date = timezone.now()
            utils.update_average_response_time(pk=purchase_order.id)
            purchase_order.save()

            return response.Response(
                {"message": "Acknowledgment successful"},
                status=status.HTTP_200_OK
            )
        except PurchaseOrder.DoesNotExist:
            return response.Response(
                {"message": "Purchase Order not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return response.Response(
                {"message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    if request.method == 'GET':
        return response.Response({'messege': 'Hi you can access me!'})
