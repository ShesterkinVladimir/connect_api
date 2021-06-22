from rest_framework import serializers

from .models import Order, Product, OrderDetail


# сериализаторы для добавления и вывода
class ProductListSerializer(serializers.ModelSerializer):
    """Список продуктов"""

    id = serializers.IntegerField()
    name = serializers.CharField(max_length=64, read_only=True)

    class Meta:
        model = Product
        fields = ("id", "name")


class OrderDetailListSerializer(serializers.ModelSerializer):
    """Список детализаций заказа"""

    product = ProductListSerializer()

    class Meta:
        model = OrderDetail
        fields = ("id", "product", "amount", "price")

    def create(self, validated_data):
        product_data = validated_data.pop('product', None)
        if product_data:
            product = Product.objects.get(**product_data)
            validated_data['product'] = product
        return OrderDetail.objects.create(**validated_data)


class OrderListSerializer(serializers.ModelSerializer):
    """Список заказов"""

    details = OrderDetailListSerializer(many=True)

    class Meta:
        model = Order
        fields = ("id", "status", "created_at", "external_id", "details")

    def create(self, validated_data):
        details = validated_data.pop('details', [])
        order = Order.objects.create(**validated_data)
        for detail_dict in details:
            detail_dict['order'] = order
            OrderDetailListSerializer().create(detail_dict)
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