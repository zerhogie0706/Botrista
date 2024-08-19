from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .serializers import LoginSerializer, ProductSerializer
from .decorators import login_required
from .models import Product, Order
from .permissions import ManangerPermission


@login_required
def test(request):
    return JsonResponse({'success': True})


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, _ = Token.objects.get_or_create(user=user)
            return JsonResponse({'token': token.key}, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    permission_classes = [ManangerPermission]
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action == 'list':
            self.permission_classes = [AllowAny, ]
        return super().get_permissions()

    def list(self, request):
        qs = self.get_queryset()
        print(qs)
        serializer = self.get_serializer(qs, many=True)
        payload = serializer.data
        print(payload)
        return Response(payload)

    def create(self, request):
        required_fields = {'name', 'price', 'stock'}
        data = {field: request.data.get(field) for field in required_fields}
        if any(value is None for value in data.values()):
            raise

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


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    pass
