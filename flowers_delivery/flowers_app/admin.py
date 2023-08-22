from django.contrib import admin

# Register your models here.

from .models import (
    TelegramUser,
    Bouquets,
    Images,
    Orders,
    Categories,
    ColorSpectrum,
    ConsultationRequests
)


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['chat_id', 'name', 'phone']

@admin.register(Categories)
class CategoriesAdmin(admin.ModelAdmin):
    list_display = ['category_name']

@admin.register(Bouquets)
class BouquetsAdmin(admin.ModelAdmin):
    list_display = ['short_title', 'price']


@admin.register(Images)
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['alt', 'path']


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = ['client_id', 'execution_date', 'status', 'comment', 'delivery_address', 'all_price']


@admin.register(ColorSpectrum)
class ColorSpectrumAdmin(admin.ModelAdmin):
    list_display = ['color_spectrum']


@admin.register(ConsultationRequests)
class ConsultationRequestsAdmin(admin.ModelAdmin):
    list_display = ['phone', 'status']

