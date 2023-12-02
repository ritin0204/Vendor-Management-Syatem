from rest_framework.test import APITestCase
from rest_framework import status
from .models import Vendor, PurchaseOrder
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


class AdminAccessToken():
    def __init__(self) -> None:
        self.admin_user = User.objects.create_superuser(username='adminuser', password='adminpassword')

        # Obtain a JWT for the admin user
        refresh = RefreshToken.for_user(self.admin_user)
        self.admin_access_token = str(refresh.access_token)


class AdminOnlyViewTests(APITestCase):
    def setUp(self):
        self.url = reverse('create-vendor')
        # Create a regular user for testing
        self.user = User.objects.create_user(username='testuser', password='testpassword')

        # Create an admin user for testing
        self.admin_user = User.objects.create_superuser(username='adminuser', password='adminpassword')

        # Obtain a JWT for the admin user
        refresh = RefreshToken.for_user(self.admin_user)
        self.admin_access_token = str(refresh.access_token)

        # Obtain a JWT for the regular user (for comparison)
        refresh = RefreshToken.for_user(self.user)
        self.user_access_token = str(refresh.access_token)

    def test_admin_access(self):
        # Set the Authorization header with the admin JWT token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_access_token}')

        # Make a GET request to the admin-only API view
        response = self.client.get(self.url)

        # Assert that the response status code is 200 (OK)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_regular_user_access(self):
        # Set the Authorization header with the regular user JWT token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user_access_token}')

        # Make a GET request to the admin-only API view with a regular user token
        response = self.client.get(self.url)

        # Assert that the response status code is 403 (Forbidden) or another appropriate code
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class VendorAPITestCase(APITestCase):
    def setUp(self):
        # Creating Acccess Token
        self.access_token = AdminAccessToken().admin_access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.vendor_data = {
            'name': 'Test Vendor',
            'contact_details': 'Vendor Contact',
            'address': 'Vendor Address',
            'vendor_code': 'V003'
        }
        self.vendor = Vendor.objects.create(**self.vendor_data)
        self.vendor_detail_url = reverse('vendor-detail',
                                         args=[self.vendor.id])

    def test_create_vendor(self):
        vendor_data = {
            'name': 'Test Vendor',
            'contact_details': 'Vendor Contact',
            'address': 'Vendor Address',
            'vendor_code': 'V004'
        }
        response = self.client.post(
            reverse('create-vendor'), data=vendor_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Assuming you have one vendor created in the setUp
        self.assertEqual(Vendor.objects.count(), 2)

    def test_retrieve_vendor(self):
        response = self.client.get(self.vendor_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.vendor_data['name'])

    def test_update_vendor(self):
        updated_data = {'name': 'Updated Vendor Name'}
        response = self.client.patch(
            self.vendor_detail_url, data=updated_data, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            Vendor.objects.get(id=self.vendor.id).name, updated_data['name']
        )

    def test_delete_vendor(self):
        response = self.client.delete(self.vendor_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Vendor.objects.count(), 0)

    def test_vendor_performance_api(self):
        response = self.client.get(
            reverse('vendor-performance',
                    args=[self.vendor.pk]),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class PurchaseOrderAPITestCase(APITestCase):
    def setUp(self):
        # Creating Acccess Token
        self.access_token = AdminAccessToken().admin_access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.POData = {
            "po_number": "P003",
            "items": [
                "item1",
                "item2",
                "item3",
            ],
            "quantity": 12,
            "issue_date": "2023-11-29T17:58:00Z",
            "vendor": 1
        }
        self.vendor = Vendor.objects.create(
            name='Test Vendor',
            contact_details='Vendor Contact',
            address='Vendor Address',
            vendor_code='V002',
        )
        self.purchase_order = PurchaseOrder.objects.create(
            po_number='PO001',
            vendor=self.vendor,
            items={'item1': 5, 'item2': 10},
            quantity=15,
            issue_date=timezone.now(),
        )
        self.purchase_details_url = reverse('purchase-order-detail',
                                            args=[self.purchase_order.pk])

    def test_create_purchase_order_api(self):
        response = self.client.post(
            reverse('create-purchase-order'), data=self.POData, format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Assuming you have one vendor created in the setUp
        self.assertEqual(PurchaseOrder.objects.count(), 2)
        self.assertEqual(
            PurchaseOrder.objects.get(po_number='P003').vendor.id, 1
        )

    def test_update_purchase_order_api(self):
        response = self.client.patch(
            self.purchase_details_url,
            data={
                'quantity': 14,
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            PurchaseOrder.objects.get(po_number='PO001').quantity, 14
        )
        self.assertEqual(
            response.data['quantity'], 14
        )

    def test_vendor_acknowledge_api(self):
        self.assertEqual(self.purchase_order.acknowledgment_date, None)
        response = self.client.post(
            reverse('acknowledge_purchase_order',
                    args=[self.purchase_order.id])
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_status_update_purchase_order_api(self):
        response = self.client.patch(
            self.purchase_details_url,
            data={
                'status': "COMPLETED"
            },
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            PurchaseOrder.objects.get(po_number='PO001').status, 'COMPLETED'
        )
        self.assertEqual(
            response.data['status'], 'COMPLETED'
        )

    def test_retrieve_purchase_order_api(self):
        response = self.client.get(self.purchase_details_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(
            response.data['id'], 1
        )

    def test_delete_purchase_order_api(self):
        response = self.client.delete(self.purchase_details_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PurchaseOrder.objects.count(), 0)


class VendorPerformanceAPIs(APITestCase):
    def setUp(self) -> None:
        self.vendor_data = {
            'name': 'Test Vendor',
            'contact_details': 'Vendor Contact',
            'address': 'Vendor Address',
            'vendor_code': 'V001'
        }
        self.vendor = Vendor.objects.create(**self.vendor_data)
        self.purchase_orders_numbers = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10
        ]
        self.ids = []
        for po_number in self.purchase_orders_numbers:
            po_data = {
                "po_number": f"P00{po_number}",
                "items": [
                    "item1",
                    "item2",
                    "item3",
                ],
                "quantity": 12,
                "issue_date": timezone.now(),
                "vendor": self.vendor
            }
            po_obj = PurchaseOrder.objects.create(**po_data)
            self.ids.append(po_obj.pk)

    def test_performance_api(self):
        for pk in self.ids:
            if pk > 8:
                self.client.put(
                    reverse('purchase-order-detail', args=[pk]),
                    data = {
                        'status':'COMPLETED',
                        'quality_rating': 0.2+(pk/10)}
                )
            else:
                self.client.put(
                    reverse('purchase-order-detail', args=[pk]),
                    data = {'status':'CONCELLED'}
                )
        response = self.client.get(
            reverse('vendor-performance',
                    args=[self.vendor.pk])
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
