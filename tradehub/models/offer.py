from django.db import models
from django.db.models import Q
from .bakugan import OwnedBakugan
from .user import User
import datetime

class Offer(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_offers")
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_offers")
    sender_price = models.IntegerField(default=0)
    receiver_price = models.IntegerField(default=0)
    receiver_read = models.BooleanField(default=False)
    date = models.DateField(default=datetime.date.today)
    complete = models.BooleanField(default=False)

    def placeOffer(self):
        self.save()

    @staticmethod
    def init_pending_offer(request):
        if 'pending_offer' not in request.session:
            request.session['pending_offer'] = {}
        request.session['pending_offer'].setdefault('sender_id', None)
        request.session['pending_offer'].setdefault('receiver_id', None)
        request.session['pending_offer'].setdefault('sender_price', None)
        request.session['pending_offer'].setdefault('receiver_price', None)
        request.session['pending_offer'].setdefault('sender_bakugans', [])
        request.session['pending_offer'].setdefault('receiver_bakugans', [])

    @staticmethod
    def get_user_offers(user_id, direction):
        if direction == "sending":
            return Offer.objects.filter(sender=user_id).order_by('-date')
        elif direction == "receiving":
            return Offer.objects.filter(receiver=user_id).order_by('-date')
        return Offer.objects.filter(Q(sender=user_id) | Q(receiver=user_id)).order_by('-date')
    
    @staticmethod
    def get_offer_min_price(owned_ids):
        price = 0
        for id in owned_ids:
            owned_bakugan = OwnedBakugan.get_owned_bakugan_by_id(id)
            if owned_bakugan.trade_type == 'selling':
                price += owned_bakugan.price
        return price
    
    @staticmethod
    def get_offer_by_id(offer_id):
        return Offer.objects.get(id=offer_id)
    
    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"
    
    def __str__(self):
        return f"\"{self.sender.discord_name}\" traded with \"{self.receiver.discord_name}\""

class OfferItem(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(OwnedBakugan, on_delete=models.CASCADE)
    direction = models.CharField(max_length=10, choices=[("giving", "Giving"), ("asking", "Asking")])

    def create_offer_item(self):
        self.save()
        
    @staticmethod
    def get_offer_items_by_offer_id(offer_id):
        return OfferItem.objects.filter(offer__id=offer_id)
    
    @staticmethod
    def get_offer_items_by_owned_bakugan_id(ob_id):
        return OfferItem.objects.filter(item_id=ob_id)

    class Meta:
        verbose_name = "OfferItem"
        verbose_name_plural = "OfferItems"

    def __str__(self):
        return f"{self.direction} {self.item} | {self.id}"