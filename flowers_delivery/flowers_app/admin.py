from django.contrib import admin

# Register your models here.

from .models import (
    TelegramUser,
    Bouquets,
    Images,
    Orders,
    Categories,
    ColorSpectrum,
    ConsultationRequests,
    ProductInOrder,
    Products,
    ProductsBouquets
)


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'name', 'phone']

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ['category_name']


@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = ['title', 'description', 'price']


class ProductsBouquetsInlines(admin.TabularInline):
    model = ProductsBouquets
    extra = 0


# @admin.register(ProductsBouquets)
# class ProductsBouquetsAdmin(admin.ModelAdmin):
#     list_display = ['products', 'bouquets']


@admin.register(Bouquets)
class BouquetsAdmin(admin.ModelAdmin):
    list_display = ['short_title', 'price']
    inlines = [ProductsBouquetsInlines]

    def price(self, bouquets):
        price_bouqets = 0
        bouquets_products = ProductsBouquets.objects.filter(bouquets=bouquets.id)
        for product in bouquets_products:
            price_bouqets += product.products.price

        return price_bouqets


@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['alt', 'path']


class ProductInOrderInlines(admin.TabularInline):
    model = ProductInOrder
    extra = 0


# @admin.register(ProductInOrder)
# class ProductInOrderAdmin(admin.ModelAdmin):
#     list_display = ['order', 'product', 'price']

#     def price(self, product):
#         price = 0
#         if product.product:
#             price += product.product.price
#         elif product.bouquets:
#             bouquets_products = ProductsBouquets.objects.filter(bouquets=product.bouquets.id)
#             for product in bouquets_products:
#                 price += product.products.price
        
#         return price


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ['client_id', 'execution_date', 'status', 'comment', 'delivery_address', 'all_price']
    inlines = [ProductInOrderInlines]

    def price_order(self, order):
        price = 0
        all_position = ProductInOrder.objects.filter(order=order.id)
        for position in all_position:
            if position.product:
                price += position.product.price
            elif position.bouquets:
                bouquets_products = ProductsBouquets.objects.filter(bouquets=position.bouquets.id)
                for position in bouquets_products:
                    price += position.products.price
        return price




@admin.register(ColorSpectrum)
class ColorSpectrumAdmin(admin.ModelAdmin):
    list_display = ['color_spectrum']


@admin.register(ConsultationRequests)
class ConsultationRequestsAdmin(admin.ModelAdmin):
    list_display = ['phone', 'status']






