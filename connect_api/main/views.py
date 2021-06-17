from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.pagination import LimitOffsetPagination
from collections import OrderedDict
# from rest_framework.generics import ListAPIView
# from rest_framework.filters import SearchFilter


from .models import Order
from .serializers import OrderListSerializer, OrderCreateSerializer, \
    OrderAcceptOrFailedSerializer, OrderExternalSerializer


class OrderPagination(LimitOffsetPagination):
    default_limit = 3
    # limit_query_param = 'l'
    # offset_query_param = 'o'
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


# class OrderListView(ListAPIView):
#     serializer_class = OrderListSerializer
#     queryset = Order.objects.all()
#     pagination_class = OrderPagination
#     filter_backends = [SearchFilter]
#     search_fields = ["external_id", "status"]


class OrderListView(APIView):
    """Вывод списка заказов"""
    paginator = OrderPagination()
    # filter_backends = [SearchFilter]
    # search_fields = ["external_id", "status"]

    # def get(self, request):  # работает
    #     try:
    #         orders = Order.objects
    #         serializer = OrderListSerializer(orders, many=True)
    #
    #         page = self.paginator.paginate_queryset(serializer.data, request)
    #         return self.paginator.get_paginated_response(page)
    #     except:
    #         Response(status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):  # не получилоссь заполнить все таблицы, как создавать FK?
        serializer = OrderCreateSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()

            order = Order.objects.get(id=serializer.data[0])
            serializer = OrderListSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class OrderSpecificView(APIView):
    """Вывод конкретного заказа """

    def get(self, request, pk):  # работает
        try:
            order = Order.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = OrderListSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):  # работает
        try:
            Order.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

        id = None
        for i in range(len(request.data)):
            if request.data[i]['id'] == pk:
                id = i
                break
        if id is not None:
            serializer = OrderExternalSerializer(data=request.data[id])
            if serializer.is_valid():
                serializer.save()
                order = Order.objects.get(id=pk)
                serializer = OrderListSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):  # работает
        try:
            Order.objects.get(id=pk)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = OrderListSerializer(order)
        if serializer.data["status"] != "A":
            order.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class OrderAccept(APIView):  # работает

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


class OrderFail(APIView):  # работает

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
