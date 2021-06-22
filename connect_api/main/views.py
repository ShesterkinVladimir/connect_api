from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from collections import OrderedDict
from rest_framework.generics import ListCreateAPIView
from rest_framework.filters import SearchFilter

from .models import Order
from .serializers import OrderListSerializer, OrderAcceptOrFailedSerializer, OrderExternalSerializer


class OrderPagination(LimitOffsetPagination):
    default_limit = 3
    max_limit = 100

    def get_paginated_response(self, data):
        return Response(OrderedDict({
            'Content - Range': {
                'limit - ' + str(self.limit),
                'offset - ' + str(self.offset),
            },
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.count,
            'results': data
        }))


class OrderListView(ListCreateAPIView):  # работает и есть тесты

    serializer_class = OrderListSerializer
    queryset = Order.objects.all()
    pagination_class = OrderPagination
    filter_backends = [SearchFilter]
    search_fields = ["external_id", "status"]



class OrderSpecificView(APIView):
    """Вывод конкретного заказа """

    def get(self, request, pk):  # работает, есть тесты
        try:
            order = Order.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = OrderListSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):  # работает, есть тесты
        try:
            order = Order.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if request.data['id'] == pk:
            serializer = OrderListSerializer(order)
            if serializer.data["status"] == "N":
                serializer = OrderExternalSerializer(order, data=request.data)
                if serializer.is_valid():
                    serializer.save()
                    order = Order.objects.get(id=pk)
                    serializer = OrderListSerializer(order)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):  # работает, есть тесты
        try:
            order = Order.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = OrderListSerializer(order)
        if serializer.data["status"] != "A":
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class OrderAccept(APIView):  # работает, есть тесты

    def post(self, request, pk):
        try:
            Order.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if OrderListSerializer(Order.objects.get(id=pk))['status'].value == "N":
            serializer = OrderAcceptOrFailedSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(id=pk, status="A")
                order = Order.objects.get(id=pk)
                serializer = OrderListSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class OrderFail(APIView):  # работает, есть тесты

    def post(self, request, pk):
        try:
            Order.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = OrderAcceptOrFailedSerializer(data=request.data)
        if OrderListSerializer(Order.objects.get(id=pk))['status'].value == "N":
            if serializer.is_valid():
                serializer.save(id=pk, status="F")
                order = Order.objects.get(id=pk)
                serializer = OrderListSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
