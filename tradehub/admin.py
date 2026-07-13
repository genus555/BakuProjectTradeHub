from django.contrib import admin
from .models.attribute import Attribute
from .models.bakugan import Bakugan, OwnedBakugan
from .models.offer import Offer, OfferItem
from . models.user import User

admin.site.register(Attribute)
admin.site.register(Bakugan)
admin.site.register(User)
admin.site.register(Offer)
admin.site.register(OfferItem)
admin.site.register(OwnedBakugan)