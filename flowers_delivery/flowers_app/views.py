from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Orders
from datetime import datetime

# Create your views here.

def index(request):
    today_date = datetime.now()
    orders = Orders.objects.filter(created__lte=today_date)
    template = 'flowers_app/index.html'
    split_date = str(today_date).split()[0]

    all_summ = 0
    for order in orders:
        all_summ += order.all_price


    context = {
        "orders": orders,
        "date": datetime.strptime(split_date, '%Y-%m-%d').date(),
        "all_summ": all_summ
    }
    return render(request, template, context)
