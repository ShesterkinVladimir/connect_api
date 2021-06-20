from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Order, Product, OrderDetail


class OrderTests(APITestCase):

    def setUp(self):
        # product1 = Product.objects.create(name="Dropbox")
        # detail1 = OrderDetail.objects.create(order=, product=product1, amount=10, price="12.00")

        # Order.objects.create(external_id="PR-123-321-123")
        # Order.objects.create(external_id="PR-100-111-232")

        self.order1 = Order.objects.create(
            external_id="PR-123-321-123",
            # detail=detail1
        )

        self.order2 = Order.objects.create(
            external_id="PR-333-111-222"
        )

        self.order3 = Order.objects.create(
            external_id="PR-000-111",
            status="A"
        )

    def test_order_list(self):
        response = self.client.get(reverse("orders"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_not_exist_order(self):
        response = self.client.get(reverse("order_pk", kwargs={'pk': 100}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_exist_order(self):
        response = self.client.get(reverse("order_pk", kwargs={'pk': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("external_id"), "PR-123-321-123")

    def test_order_delete(self):
        response = self.client.delete(reverse("order_pk", kwargs={'pk': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_not_exist_order_delete(self):
        response = self.client.delete(reverse("order_pk", kwargs={'pk': 100}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_delete_accepted(self):
        response = self.client.delete(reverse("order_pk", kwargs={'pk': self.order3.id}))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_new_external_id(self):
        response = self.client.put(
            reverse("order_pk", kwargs={'pk': self.order1.id}),
            [{"id": self.order1.id, "external_id": "10101"}], format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("external_id"), "10101")

    def test_new_status(self):
        response = self.client.put(
            reverse("order_pk", kwargs={'pk': self.order1.id}),
            [{"id": self.order1.id, "status": "A"}], format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_external_id_not_N(self):
        response = self.client.put(
            reverse("order_pk", kwargs={'pk': self.order3.id}),
            [{"id": self.order3.id, "external_id": "10101"}], format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_new_external_id_not_data_id(self):
        response = self.client.put(
            reverse("order_pk", kwargs={'pk': self.order1.id}),
            [{"id": 100, "external_id": "10101"}], format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_external_id_not_db_id(self):
        response = self.client.put(
            reverse("order_pk", kwargs={'pk': 100}),
            [{"id": self.order1.id, "external_id": "10101"}], format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_accept(self):
        response = self.client.post(reverse("accept", kwargs={'pk': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("status"), "A")

    def test_order_accept_not_N(self):
        response = self.client.post(reverse("accept", kwargs={'pk': self.order3.id}))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_order_accept_not_id(self):
        response = self.client.post(reverse("accept", kwargs={'pk': 100}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_fail(self):
        response = self.client.post(reverse("fail", kwargs={'pk': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("status"), "F")

    def test_order_fail_not_N(self):
        response = self.client.post(reverse("fail", kwargs={'pk': self.order3.id}))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_order_fail_not_id(self):
        response = self.client.post(reverse("fail", kwargs={'pk': 100}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)








