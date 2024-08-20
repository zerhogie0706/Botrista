from django.contrib import admin
from .models import *
# Register your models here.

Models = [UserProfile, Product]
admin.site.register(Models)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1  # Number of extra empty fields to display


class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
