from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
]

router = DefaultRouter()
router.register(r'product', views.ProductViewSet)
router.register(r'order', views.OrderViewSet)

urlpatterns += router.urls
