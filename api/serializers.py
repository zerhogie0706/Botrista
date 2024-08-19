from django.contrib.auth import authenticate
from rest_framework import serializers
from .models import Product, Order, OrderItem


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data.get("username")
        password = data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must include both username and password.")
        data['user'] = user
        return data
    

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items_info = serializers.SerializerMethodField()

    def get_items_info(self, obj):
        items = obj.order_items.all()
        return OrderItemSerializer(items, many=True).data

    class Meta:
        model = Order
        fields = ['items_info']


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['product', 'quantity']
