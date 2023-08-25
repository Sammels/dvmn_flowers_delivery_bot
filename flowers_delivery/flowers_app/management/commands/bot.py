from django.core.management.base import BaseCommand
from django.conf import settings
from environs import Env
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, InputFile, \
    LabeledPrice
import telebot
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "flowers_delivery.settings")
django.setup()
from flowers_app.models import Categories, ColorSpectrum, Bouquets, ConsultationRequests, Orders, TelegramUser

Env().read_env()
token = Env().str('TG_TOKEN')
payment_token = Env().str('PAYMENTS_TOKEN')
bot = telebot.TeleBot(token)

chats = {}


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.message.chat.id not in chats:
        chats[call.message.chat.id] = {}
    if call.data == 'main':
        main_menu(call.message)
    if call.data == 'payment':
        bot.send_invoice(call.message.chat.id,
                         title=f'Покупка букета {chats[call.message.chat.id]["bouquet"]}',
                         description=f'Время доставки: {chats[call.message.chat.id]["delivery_time"]}',
                         provider_token=payment_token,
                         currency='rub',
                         photo_url='https://appleinsider.ru/wp-content/uploads/2023/02/telegram_premium_logo_subscription-750x464.png',
                         photo_width=416,
                         photo_height=234,
                         photo_size=416,
                         is_flexible=False,
                         prices=[LabeledPrice(label='Покупка букета',
                                              amount=chats[call.message.chat.id]['bouquet_price'] * 100)],
                         invoice_payload='test-invoice-payload',
                         )


@bot.message_handler(commands=['start'])
def start(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Я хочу букет', callback_data='main'))
    bot.send_message(message.chat.id, 'Кто хочет букет?', reply_markup=markup)


def main_menu(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    for category in Categories.objects.all().iterator():
        markup.add(KeyboardButton(category.category_name))
    bot.send_photo(message.chat.id,
                   r'https://www.ribbonflowers.com/vitrin_resimler/727_500.jpg',
                   'К какому событию готовимся?', reply_markup=markup)

    return bot.register_next_step_handler(message, choose_price)


def choose_price(message):
    if message.text == 'Другой повод':
        message = bot.send_message(message.chat.id, 'Напишите какой повод?')
        return bot.register_next_step_handler(message, choose_price)
    chat_id = message.chat.id
    if chat_id not in chats:
        chats[chat_id] = {}
    user = chats[message.chat.id]
    user['category'] = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    markup.add(KeyboardButton('~500'))
    markup.add(KeyboardButton('~1000'))
    markup.add(KeyboardButton('~2000'))
    markup.add(KeyboardButton('Больше'))
    markup.add(KeyboardButton('Не важно'))
    bot.send_message(message.chat.id, 'На какую сумму рассчитываете?', reply_markup=markup)

    return bot.register_next_step_handler(message, choose_color_spectrum)


def choose_color_spectrum(message):
    user = chats[message.chat.id]
    user['price'] = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    for color in ColorSpectrum.objects.all().iterator():
        markup.add(KeyboardButton(color.color_spectrum))
    bot.send_message(message.chat.id, 'Предпочтение цветовой гаммы', reply_markup=markup)

    return bot.register_next_step_handler(message, choose_bouquet, -1)


def choose_bouquet(message, page=1):
    user = chats[message.chat.id]
    if page == -1:
        user['color'] = message.text
        return choose_bouquet(message, 1)
    # TODO Доделать категорию 'Другой повод' с ценой
    if user['price'] == '~500' and user['category'] != 'Другой повод':
        bouquets = Bouquets.objects.filter(category=Categories.objects.get(category_name=user['category']),
                                           color_spectrum=ColorSpectrum.objects.get(color_spectrum=user['color']),
                                           price__lte=500 + 500 * 0.2,
                                           price__gte=500 - 500 * 0.2)
    elif user['price'] == '~1000' and user['category'] != 'Другой повод':
        bouquets = Bouquets.objects.filter(category=Categories.objects.get(category_name=user['category']),
                                           color_spectrum=ColorSpectrum.objects.get(color_spectrum=user['color']),
                                           price__lte=1000 + 1000 * 0.5,
                                           price__gte=1000 - 1000 * 0.5)
    elif user['price'] == '~2000' and user['category'] != 'Другой повод':
        bouquets = Bouquets.objects.filter(category=Categories.objects.get(category_name=user['category']),
                                           color_spectrum=ColorSpectrum.objects.get(color_spectrum=user['color']),
                                           price__lte=2000 + 2000 * 0.5,
                                           price__gte=2000 - 2000 * 0.5)
    elif user['price'] == 'Больше' and user['category'] != 'Другой повод':
        bouquets = Bouquets.objects.filter(category=Categories.objects.get(category_name=user['category']),
                                           color_spectrum=ColorSpectrum.objects.get(color_spectrum=user['color']),
                                           price__gte=2500)
    elif user['price'] == 'Не важно' and user['category'] != 'Другой повод':
        bouquets = Bouquets.objects.filter(category=Categories.objects.get(category_name=user['category']),
                                           color_spectrum=ColorSpectrum.objects.get(color_spectrum=user['color']))
    elif user['category'] == 'Другой повод':
        bouquets = Bouquets.objects.filter(color_spectrum=ColorSpectrum.objects.get(color_spectrum=user['color']))

    if message.text == 'Вперёд --->':
        if page < bouquets.count():
            page += 1
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            markup.add(KeyboardButton('Заказать букет'))
            markup.add(KeyboardButton('Заказать консультацию'))
            markup.add(KeyboardButton('Весь каталог'))
            markup.add(KeyboardButton('<--- Назад'),
                       KeyboardButton(f'{page}/{bouquets.count()}'),
                       KeyboardButton('Вперёд --->'))
            photo = os.path.join('media', f'{bouquets[page - 1].image_id.path}')
            bot.send_photo(message.chat.id,
                           InputFile(photo),
                           f'Букет "{bouquets[page - 1].short_title}"\n\n{bouquets[page - 1].description}'
                           f'\n\nЦена: {bouquets[page - 1].price} рублей',
                           reply_markup=markup)
            return bot.register_next_step_handler(message, choose_bouquet, page)
        else:
            return choose_bouquet(message, bouquets.count() - 1)

    elif message.text == '<--- Назад':
        if page > 1:
            page -= 1
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            markup.add(KeyboardButton('Заказать букет'))
            markup.add(KeyboardButton('Заказать консультацию'))
            markup.add(KeyboardButton('Весь каталог'))
            markup.add(KeyboardButton('<--- Назад'),
                       KeyboardButton(f'{page}/{bouquets.count()}'),
                       KeyboardButton(f'Вперёд --->'))
            photo = os.path.join('media', f'{bouquets[page - 1].image_id.path}')
            bot.send_photo(message.chat.id,
                           InputFile(photo),
                           f'Букет "{bouquets[page - 1].short_title}"\n\n{bouquets[page - 1].description}\n\n'
                           f'Цена: {bouquets[page - 1].price} рублей',
                           reply_markup=markup)

            return bot.register_next_step_handler(message, choose_bouquet, page)
        else:
            message.text = ''
            return choose_bouquet(message)

    elif message.text == 'Заказать букет':
        chats[message.chat.id]['bouquet_price'] = bouquets[page - 1].price
        get_bouquet(message, 1, bouquets[page - 1].short_title)

    elif message.text == 'Заказать консультацию':
        get_consultation(message)

    elif message.text == 'Весь каталог':
        get_catalog(message)

    else:
        try:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            markup.add(KeyboardButton('Заказать букет'))
            markup.add(KeyboardButton('Заказать консультацию'))
            markup.add(KeyboardButton('Весь каталог'))
            markup.add(KeyboardButton('<--- Назад'),
                       KeyboardButton(f'1/{bouquets.count()}'),
                       KeyboardButton('Вперёд --->'))

            photo = os.path.join('media', f'{bouquets[page - 1].image_id.path}')
            bot.send_photo(message.chat.id,
                           InputFile(photo),
                           f'Букет "{bouquets[page - 1].short_title}"\n\n{bouquets[page - 1].description}'
                           f'\n\nЦена: {bouquets[page - 1].price} рублей',
                           reply_markup=markup)
            return bot.register_next_step_handler(message, choose_bouquet, page)
        except IndexError:
            bot.send_message(message.chat.id, 'Выберите другую категорию')
            main_menu(message)


def get_catalog(message, page=1):
    bouquets = Bouquets.objects.all()

    if message.text == 'Вперёд --->':
        if page < bouquets.count():
            page += 1
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            markup.add(KeyboardButton('Заказать букет'))
            markup.add(KeyboardButton('Заказать консультацию'))
            markup.add(KeyboardButton('<--- Назад'),
                       KeyboardButton(f'{page}/{bouquets.count()}'),
                       KeyboardButton('Вперёд --->'))
            photo = os.path.join('media', f'{bouquets[page - 1].image_id.path}')
            bot.send_photo(message.chat.id,
                           InputFile(photo),
                           f'Букет "{bouquets[page - 1].short_title}"\n\n{bouquets[page - 1].description}'
                           f'\n\nЦена: {bouquets[page - 1].price} рублей',
                           reply_markup=markup)
            return bot.register_next_step_handler(message, get_catalog, page)
        else:
            return get_catalog(message, bouquets.count() - 1)

    elif message.text == '<--- Назад':
        if page > 1:
            page -= 1
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            markup.add(KeyboardButton('Заказать букет'))
            markup.add(KeyboardButton('Заказать консультацию'))
            markup.add(KeyboardButton('<--- Назад'),
                       KeyboardButton(f'{page}/{bouquets.count()}'),
                       KeyboardButton(f'Вперёд --->'))
            photo = os.path.join('media', f'{bouquets[page - 1].image_id.path}')
            bot.send_photo(message.chat.id,
                           InputFile(photo),
                           f'Букет "{bouquets[page - 1].short_title}"\n\n{bouquets[page - 1].description}'
                           f'\n\nЦена: {bouquets[page - 1].price} рублей',
                           reply_markup=markup)

            return bot.register_next_step_handler(message, get_catalog, page)
        else:
            message.text = ''
            return get_catalog(message)

    elif message.text == 'Заказать букет':
        chats[message.chat.id]['bouquet_price'] = bouquets[page - 1].price
        get_bouquet(message, 1, bouquets[page - 1].short_title)

    elif message.text == 'Заказать консультацию':
        get_consultation(message)

    else:
        try:
            markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

            markup.add(KeyboardButton('Заказать букет'))
            markup.add(KeyboardButton('Заказать консультацию'))
            markup.add(KeyboardButton('<--- Назад'),
                       KeyboardButton(f'1/{bouquets.count()}'),
                       KeyboardButton('Вперёд --->'))
            photo = os.path.join('media', f'{bouquets[page - 1].image_id.path}')
            bot.send_photo(message.chat.id,
                           InputFile(photo),
                           f'Букет "{bouquets[page - 1].short_title}"\n\n{bouquets[page - 1].description}'
                           f'\n\nЦена: {bouquets[page - 1].price} рублей',
                           reply_markup=markup)
            return bot.register_next_step_handler(message, get_catalog, page)
        except IndexError:
            bot.send_message(message.chat.id, 'Выберите другую категорию')
            main_menu(message)


def get_consultation(message, step=1):
    user = chats[message.chat.id]
    if step == 1:
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        bot.send_message(message.chat.id, 'Укажите номер телефона, и наш флорист перезвонит вам в течение 20 минут',
                         reply_markup=markup)
        return bot.register_next_step_handler(message, get_consultation, 2)
    if step == 2:
        user['phone'] = message.text
        bot.send_message(message.chat.id,
                         'Флорист скоро свяжется с вами. А пока можете присмотреть что-нибудь из готовой коллекции')
        ConsultationRequests.objects.create(phone=user['phone'], status=1)
        get_catalog(message)


def get_bouquet(message, step, bouquets=0):
    user = chats[message.chat.id]
    if step == 1:
        user['bouquet'] = bouquets
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        bot.send_message(message.chat.id, 'Введите имя', reply_markup=markup)
        return bot.register_next_step_handler(message, get_bouquet, 2)
    elif step == 2:
        user['name'] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        bot.send_message(message.chat.id, 'Введите ваш номер телефона', reply_markup=markup)
        return bot.register_next_step_handler(message, get_bouquet, 3)
    elif step == 3:
        user['phone'] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        bot.send_message(message.chat.id, 'Введите адрес', reply_markup=markup)
        return bot.register_next_step_handler(message, get_bouquet, 4)
    elif step == 4:
        user['address'] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('10:00 - 12:00'))
        markup.add(KeyboardButton('14:00 - 16:00'))
        markup.add(KeyboardButton('18:00 - 20:00'))
        bot.send_message(message.chat.id, 'Выберите время доставки', reply_markup=markup)
        return bot.register_next_step_handler(message, get_bouquet, 5)
    elif step == 5:
        user['delivery_time'] = message.text
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(KeyboardButton('Нет'))
        bot.send_message(message.chat.id, 'Желаете оставить комментарий к заказу', reply_markup=markup)
        return bot.register_next_step_handler(message, get_bouquet, 6)
    elif step == 6:
        user['comment'] = message.text
        tg_user, _ = TelegramUser.objects.get_or_create(chat_id=message.chat.id,
                                                        name=user['name'],
                                                        phone=user['phone'],
                                                        address=user['address'])
        order = Orders.objects.create(client_id=tg_user,
                                      status=1,
                                      execution_date=user['delivery_time'],
                                      delivery_address=user['address'],
                                      comment=user['comment'],
                                      all_price=Bouquets.objects.get(short_title=user['bouquet']).price)
        order.bouquet_id.add(Bouquets.objects.get(short_title=user['bouquet']).id)
        user['order_id'] = order.id
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('Да', callback_data='payment'))
        markup.add(InlineKeyboardButton('На главную', callback_data='main'))
        bot.send_message(message.chat.id, 'Ваш заказ оформлен.Желаете оплатить сразу?', reply_markup=markup)


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                  error_message="Aliens tried to steal your card's CVV, but we successfully protected your credentials,"
                                                " try to pay again in a few minutes, we need a small rest.")


@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
    Orders.objects.filter(id=chats[message.chat.id]["order_id"]).update(payment=True)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton('Перейти на главное меню', callback_data='main'))
    bot.send_message(message.chat.id,
                     'Спасибо за оплату! Ваш букет будет доставлен во время! Хорошего Вам дня!',
                     parse_mode='Markdown', reply_markup=markup)


# def run_bot():
#     bot.polling(none_stop=True)


class Command(BaseCommand):
  	# Используется как описание команды обычно
    help = 'Implemented to Django application telegram bot setup command'

    def handle(self, *args, **kwargs):
        bot.enable_save_next_step_handlers(delay=2) # Сохранение обработчиков
        bot.load_next_step_handlers()								# Загрузка обработчиков
        bot.infinity_polling()	

# if __name__ == '__main__':
#     run_bot()
