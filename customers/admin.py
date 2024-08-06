from django.contrib import admin
from .models import Customer
# Register your models here.


class CustomerAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'email', 'phone'
    )
    search_fields = ('name', 'email')


admin.site.register(Customer, CustomerAdmin)
