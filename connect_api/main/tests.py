from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Order, Product, OrderDetail


class OrderTests(APITestCase):

    def setUp(self):

        self.order1 = Order.objects.create(
            external_id="PR-123-321-123",
        )

        product1 = Product.objects.create(name="Dropbox")
        detail1 = OrderDetail.objects.create(order=self.order1, product=product1, amount=10, price="12.00")


        self.order2 = Order.objects.create(
            external_id="PR-333-111-222"
        )
        detail2 = OrderDetail.objects.create(order=self.order2, product=product1, amount=10, price="12.00")

        self.order3 = Order.objects.create(
            external_id="PR-000-111",
            status="A"
        )
        detail3 = OrderDetail.objects.create(order=self.order3, product=product1, amount=10, price="12.00")

        self.p1 = Product.objects.create(
            name="book"
        )

    # тесты для post
    def test_new_order(self):
        response = self.client.post(
            reverse("orders"), {"external_id": "qqq", "details": [{
                            "product": {"id": self.p1.id},
                            "amount": 10,
                            "price": "12.00"
                                }]
                               }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get("external_id"), "qqq")
        self.assertEqual(response.json().get('details')[0]['product']["name"], "book")

    def test_new_order_plus_field(self):
        response = self.client.post(
            reverse("orders"), {"external_id": "qqq", "new_field": "qqq", "details": [{
                            "product": {"id": self.p1.id},
                            "amount": 10,
                            "price": "12.00"
                                }]
                               }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get("new_field"), None)

    def test_new_order_not_details(self):
        response = self.client.post(
            reverse("orders"), {"external_id": "qqq", "details": []}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json().get("external_id"), "qqq")

    def test_new_order_not_external_id(self):
        response = self.client.post(
            reverse("orders"), {"details": [{
                "product": {"id": self.p1.id},
                "amount": 10,
                "price": "12.00"
            }]
                                }, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # тесты для get all
    def test_order_list(self):
        response = self.client.get(reverse("orders"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    # тесты для get id
    def test_not_exist_order(self):
        response = self.client.get(reverse("order_pk", kwargs={'pk': 100}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_exist_order(self):
        response = self.client.get(reverse("order_pk", kwargs={'pk': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("external_id"), "PR-123-321-123")

    # тесты для delete
    def test_order_delete(self):
        response = self.client.delete(reverse("order_pk", kwargs={'pk': self.order1.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_not_exist_order_delete(self):
        response = self.client.delete(reverse("order_pk", kwargs={'pk': 100}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_order_delete_accepted(self):
        response = self.client.delete(reverse("order_pk", kwargs={'pk': self.order3.id}))
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    # тесты для put external_id
    def test_new_external_id(self):
        response = self.client.put(
            reverse("order_pk", kwargs={'pk': self.order1.id}),
            {"id": self.order1.id, "external_id": "10101"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get("external_id"), "10101")

    def test_new_status(self):
        response = self.client.put(
            reverse("order_pk", kwargs={'pk': self.order1.id}),
            {"id": self.order1.id, "status": "A"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_external_id_not_N(self):
        response = self.client.put(
            reverse("order_pk", kwargs={'pk': self.order3.id}),
            {"id": self.order3.id, "external_id": "10101"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_new_external_id_not_data_id(self):
        response = self.client.put(
            reverse("order_pk", kwargs={'pk': self.order1.id}),
            {"id": 100, "external_id": "10101"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_new_external_id_not_db_id(self):
        response = self.client.put(
            reverse("order_pk", kwargs={'pk': 100}),
            {"id": self.order1.id, "external_id": "10101"}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # тесты для accept
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

    # тесты для fail
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








