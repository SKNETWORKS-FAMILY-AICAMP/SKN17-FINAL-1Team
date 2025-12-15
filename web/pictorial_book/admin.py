from django.contrib import admin
from .models import HairStyleDictionary, HairStyleImage


@admin.register(HairStyleDictionary)
class HairStyleDictionaryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'gender', 'description')
    list_filter = ('category', 'gender')
    search_fields = ('name',)


@admin.register(HairStyleImage)
class HairStyleImageAdmin(admin.ModelAdmin):
    list_display = ('dict_image_id', 'name_gender', 'length', 'image_path')
    list_filter = ('length',)
    search_fields = ('name_gender__name',)
