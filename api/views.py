from django.http import JsonResponse
from django.contrib.auth import login
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db import transaction

from .serializers import LoginSerializer, ProductSerializer, OrderSerializer
from .decorators import login_required
from .models import Product, Order, OrderItem
from .permissions import ManangerPermission, CustomerPermission
from .exceptions import OutOfStockException


@login_required
def test(request):
    return JsonResponse({'success': True})


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # login(request, user)
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key}, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [AllowAny, ]
        else:
            self.permission_classes = [IsAuthenticated, ManangerPermission]
        return super().get_permissions()

    def list(self, request):
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)
        payload = serializer.data
        return Response(payload)

    def create(self, request):
        required_fields = {'name', 'price', 'stock'}
        data = {field: request.data.get(field) for field in required_fields}
        if any(value is None for value in data.values()):
            return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

        product = Product(**data)
        product.save()

        serializer = self.get_serializer(product)
        payload = serializer.data
        return Response(payload)
    
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        fields = {'name', 'price', 'stock'}
        updated_fields = []
        for field in fields:
            val = request.data.get(field)
            if val:
                setattr(instance, field, val)
                updated_fields.append(field)
        if updated_fields:
            instance.save(update_fields=updated_fields)
        
        serializer = self.get_serializer(instance)
        payload = serializer.data
        return Response(payload)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if OrderItem.objects.filter(product=instance).exists():
            return Response({'error': 'Cannot delete product with existing orders'}, status=status.HTTP_400_BAD_REQUEST)
        instance.delete()
        return Response({})


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_class = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes.append(CustomerPermission)
        return super().get_permissions()
   
    def list(self, request):
        user = request.user
        qs = self.get_queryset()
        if user.userprofile.role == 'Customer':
            qs = qs.filter(user=user)
            
        serializer = self.get_serializer(qs, many=True)
        payload = serializer.data
        return Response(payload)

    def create(self, request):
        user = request.user

        order_items = request.data.get('order_items')
        try:
            with transaction.atomic():
                order = Order.objects.create(user_id=user.id)
                product_ids = [data['product_id'] for data in order_items]
                products = Product.objects.select_for_update().filter(id__in=product_ids)
                product_mapping = {product.id: product for product in products}

                item_data = []
                for data in order_items:
                    product_id = data['product_id']
                    quantity = data['quantity']
                    product =  product_mapping.get(product_id)

                    if not product:
                        raise Exception(f'Product not found: {product_id}')

                    if quantity > product.stock:
                        raise OutOfStockException

                    item_data.append(
                        OrderItem(
                            order=order,
                            product_id=product_id,
                            quantity=quantity,
                        )
                    )
                    product.stock -= quantity
                OrderItem.objects.bulk_create(item_data)
                Product.objects.bulk_update(products, ['stock'])

            serializer = self.get_serializer(order)
            payload = serializer.data
            return Response(payload)

        except OutOfStockException as e:
            return Response({'msg': str(e)}, status=400)

        except Exception as e:
            return Response({'msg': str(e)}, status=500)
