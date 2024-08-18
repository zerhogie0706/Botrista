from django.db import models
from django.contrib.auth.models import User


class Timestamp(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class UserProfile(Timestamp):
    ROLE_CHOICES = [
        ('Manager', 'Manager'),
        ('Customer', 'Editor'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)


class Product(Timestamp):
    name = models.CharField(max_length=255, db_index=True)
    price = models.FloatField(db_index=True)
    stock = models.IntegerField()

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'


class Order(Timestamp):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')

    def __str__(self):
        return f'Order {self.id} by {self.user.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.product.name} - {self.quantity} pcs'
