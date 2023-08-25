from datetime import date
from django.db import models


class TelegramUser(models.Model):
    chat_id = models.CharField(
        max_length=20,
        verbose_name="Телеграмм id"
    )

    name = models.CharField(
        max_length=30,
        default="",
        verbose_name="Имя клиента"
    )
    phone = models.CharField(
        max_length=30,
        default="",
        verbose_name="Номер клиента"
    )
    address = models.CharField(
        max_length=300,
        default="",
        verbose_name="Адрес клиента"
    )

    def __str__(self) -> str:
        return f'{self.name}. {self.chat_id}'

    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенты"


class Categories(models.Model):
    category_name = models.CharField(max_length=50, default="", verbose_name="Название категории")

    def __str__(self):
        return f'{self.category_name}'

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"


class ColorSpectrum(models.Model):
    color_spectrum = models.CharField(
        max_length=50,
        default="Какой-то цвет",
        verbose_name="Цветовая гамма")

    def __str__(self):
        return f'{self.color_spectrum}'

    class Meta:
        verbose_name = "Цветовая гамма"
        verbose_name_plural = "Цветовые гаммы"


class Images(models.Model):
    alt = models.CharField(max_length=50)
    path = models.ImageField(upload_to="images/")

    def __str__(self):
        return f'{self.alt}'

    class Meta:
        verbose_name = "Картинка"
        verbose_name_plural = "Картинки"


class Bouquets(models.Model):
    short_title = models.CharField(max_length=30, verbose_name="Название букета")
    description = models.TextField(verbose_name="Подробное описание")
    category = models.ManyToManyField(Categories, verbose_name="Категория")
    color_spectrum = models.ForeignKey(
        ColorSpectrum,
        on_delete=models.CASCADE,
        verbose_name="Цветовая гамма")
    image_id = models.ForeignKey(Images, on_delete=models.CASCADE, verbose_name="Картинка")
    

    def __str__(self):
        return f'{self.short_title} {self.price}'


    class Meta:
        verbose_name = "Букет"
        verbose_name_plural = "Список букетов"


class Products(models.Model):
    title = models.CharField(max_length=50,blank=True, null=True, default=None, verbose_name="Наименование")
    price = models.IntegerField(default=0, blank=True, null=True, verbose_name="Цена")
    description = models.TextField(blank=True, default=None, null=True, verbose_name="Описание")
    image_id = models.ForeignKey(
        Images,
        blank=True, 
        null=True, 
        on_delete=models.CASCADE, 
        verbose_name="Картинка")
    

    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name = "Позиция для букета"
        verbose_name_plural = "Позиции для букета"


class ProductsBouquets(models.Model):
    products = models.ForeignKey(Products, on_delete=models.CASCADE, verbose_name="Позиция")
    bouquets = models.ForeignKey(Bouquets, on_delete=models.CASCADE, verbose_name="Букет")

    def __str__(self):
        return f"{self.products.title} {self.bouquets.short_title}"
    
    class Meta:
        verbose_name = "Позиция - букет"
        verbose_name_plural = "Позиции - букет"


class ConsultationRequests(models.Model):
    ONE = 1
    TWO = 2
    THREE = 3

    STATUS_CHOICES = [
        (ONE, "В ожидании"),
        (TWO, "Принято"),
        (THREE, "Исполнено")
    ]
    phone = models.CharField(max_length=30, default="", verbose_name="Телефон клиента")
    status = models.IntegerField(
        choices=STATUS_CHOICES,
        verbose_name="Статус заявки",
    )

    def __str__(self):
        return f"{self.phone} - {self.status}"

    class Meta:
        verbose_name = "Заявка на консультацию"
        verbose_name_plural = "Заявки на консультацию"


class Orders(models.Model):
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5

    STATUS_CHOICES = [
        (ONE, "Принят"),
        (TWO, "Готовиться"),
        (THREE, "Доставка"),
        (FOUR, "Выполнен"),
        (FIVE, "Отменен"),
    ]

    client_id = models.ForeignKey(
        TelegramUser,
        on_delete=models.CASCADE,
        verbose_name="Клиент"
    )
    execution_date = models.CharField(
        max_length=30,
        default=date.today,
        verbose_name="Дата исполнения",

        )

    bouquet_id = models.ManyToManyField(
        Bouquets,
        verbose_name="Готовые букеты", blank=True)


    status = models.IntegerField(
        choices=STATUS_CHOICES,
        verbose_name="Статус заказа",
    )
    comment = models.TextField(
        max_length=300,
        default="",
        verbose_name="Комментарий к заказу"
    )
    created = models.DateTimeField(auto_now_add=True, auto_now=False)
    updated = models.DateTimeField(auto_now_add=False, auto_now=True)

    delivery_address = models.CharField(
        max_length=250,
        blank=False,
        default="",
        verbose_name="Адрес доставки"

        )
    

    all_price = models.IntegerField(
        default=0,
        verbose_name="Общая стоимость"
    )

    def __str__(self):
        return f'{self.client_id.name}, {self.delivery_address}'

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"


class ProductInOrder(models.Model):
    order = models.ForeignKey(Orders, blank=True, null=True, default=None, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, blank=True, null=True, default=None, on_delete=models.CASCADE)
    bouquets = models.ForeignKey(Bouquets, blank=True, null=True, default=None, on_delete=models.CASCADE)

    def __str__(self):
        if self.product and self.bouquets:
            return f"{self.product} {self.bouquets}"
        elif self.product:
            return f"{self.product}"
        elif self.bouquets:
            return f"{self.bouquets}"
    
    class Meta:
        verbose_name = "Товар - заказ"
        verbose_name_plural = "Товары - заказы"
