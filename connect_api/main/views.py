from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from collections import OrderedDict
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import AllowAny
# from rest_framework.generics import ListCreateAPIView
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


# class OrderListView(ListCreateAPIView):  # работает пагинация и фильтр как сделать кастомный POST ?
#     serializer_class = OrderListSerializer
#     queryset = Order.objects.all()
#     pagination_class = OrderPagination
#     filter_backends = [SearchFilter]
#     search_fields = ["external_id", "status"]

#     def perform_create(self, serializer):
#         order = get_object_or_404(Order)
#         return serializer.save()

class OrderFilter(DjangoFilterBackend):  # фильтр на работает ?

    def filter_queryset(self, request, queryset, view):
        filter_class = self.get_filter_class(view, queryset)

        if filter_class:
            return filter_class(request.query_params, queryset=queryset, request=request).qs
        return queryset


class OrderListView(APIView):  # как сделать фильтр в APIView и частично не работает POST
    """Вывод списка заказов"""
    paginator = OrderPagination()

    # permission_classes = (AllowAny,)
    # filter_fields = ("external_id", "status")

    def get(self, request):  # работает (без фильтров), есть тесты ?
        try:
            orders = Order.objects
            # ff = OrderFilter()
            # filtered_queryset = ff.filter_queryset(request, orders, self)
            # print(filtered_queryset)

            serializer = OrderListSerializer(orders, many=True)
            page = self.paginator.paginate_queryset(serializer.data, request)
            return self.paginator.get_paginated_response(page)
        except:
            Response(status=status.HTTP_400_BAD_REQUEST)

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
        serializer = OrderListSerializer(order)
        if serializer.data["status"] == "N":
            id = None
            for i in range(len(request.data)):
                if request.data[i]['id'] == pk:
                    id = i
                    break
            if id is not None:
                serializer = OrderExternalSerializer(order, data=request.data[id])
                if serializer.is_valid():
                    serializer.save()
                    order = Order.objects.get(id=pk)
                    serializer = OrderListSerializer(order)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
