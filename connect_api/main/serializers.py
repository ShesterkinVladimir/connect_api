from rest_framework import serializers

from .models import Order, Product, OrderDetail


# сериализаторы для вывода
class ProductListSerializer(serializers.ModelSerializer):
    """Список продуктов"""

    class Meta:
        model = Product
        fields = ("id", "name")


class OrderDetailListSerializer(serializers.ModelSerializer):
    """Список детализаций заказа"""

    product = ProductListSerializer()

    class Meta:
        model = OrderDetail
        fields = ("id", "product", "amount", "price")


class OrderListSerializer(serializers.ModelSerializer):
    """Список заказов"""

    details = OrderDetailListSerializer(many=True)

    class Meta:
        model = Order
        fields = ("id", "status", "created_at", "external_id", "details")


# сериализаторы для создания нового заказа
class ProductListCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ("id", )


class OrderDetailCreateSerializer(serializers.ModelSerializer):

    product = ProductListCreateSerializer()
    # order = super().create(validated_data)

    class Meta:
        model = OrderDetail
        fields = ("order", "product", "amount", "price")

    # def create(self, validated_data):
    #     theorderid = validated_data.pop('order_id', None)
    #     theorder = Order.objects.get(pk=theorderid)
    #
    #     return OrderDetail.objects.create(order=theorder, **validated_data)


class OrderCreateSerializer(serializers.ModelSerializer):
    """Новый заказ"""

    details = OrderDetailCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ("external_id", "details",)

    def create(self, validated_data):
        # order = super().create(validated_data)

        details_data = validated_data.pop('details')
        details_model = OrderDetail.objects.create(**details_data)
        order = OrderDetail.objects.create(order=details_model, **validated_data)

        return order


# сериализатор для изменения статуса заказа
class OrderAcceptOrFailedSerializer(serializers.ModelSerializer):
    """ Обновление статуса на 'ACCEPT' или 'FAILED' """

    class Meta:
        model = Order
        fields = ("status", )

    def create(self, validated_data):
        status = Order.objects.update(
            status=validated_data.get("status")
        )
        return status


# сериализатор для изменения внешнего id
class OrderExternalSerializer(serializers.ModelSerializer):
    """ Обновление статуса на 'ACCEPT' или 'FAILED' """

    class Meta:
        model = Order
        fields = ("external_id", )

    def create(self, validated_data):
        status = Order.objects.update(
            external_id=validated_data.get("external_id")
        )
        return status