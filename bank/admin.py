from django.contrib import admin

from bank.models import Customer, Transaction, Account


admin.site.register([Customer, Transaction, Account])
