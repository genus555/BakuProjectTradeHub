from django.contrib import admin
from .models.attribute import Attribute
from .models.bakugan import Bakugan

admin.site.register(Attribute)
admin.site.register(Bakugan)