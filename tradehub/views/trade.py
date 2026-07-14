from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.views import View
from tradehub.models.bakugan import OwnedBakugan
from tradehub.models.offer import Offer, OfferItem
from tradehub.models.user import User
import logging

logger = logging.getLogger('django')

class TradeMenu(View):
    def get(self, request):
        Offer.init_pending_offer(request)
        offer_id = request.session.get('offer_id')
        uid = request.session.get('user')
        sender = None
        receiver = None
        sender_price = None
        receiver_price = None
        sender_bakugans = []
        receiver_bakugans = []
        request.session.setdefault('editing', False)

        if not uid:
            return redirect('homepage')

        if not offer_id:
            offer_id = request.GET.get("offer_id")
            request.session['offer_id'] = offer_id

        if offer_id:
            try:
                offer = Offer.get_offer_by_id(offer_id)
                request.session['original_offer'] = offer_id
                pending = {
                    'sender_id': offer.sender.id,
                    'receiver_id': offer.receiver.id,
                    'sender_price': offer.sender_price,
                    'receiver_price': offer.receiver_price,
                    'sender_bakugans': [],
                    'receiver_bakugans': [],
                }
                offered = OfferItem.get_offer_items_by_offer_id(offer_id)

                if offer.receiver_id == uid and not offer.receiver_read:
                    offer.receiver_read = True
                    offer.save(update_fields=["receiver_read"])

                for oi in offered:
                    if oi.item.owner.id == offer.sender.id:
                        pending['sender_bakugans'].append(oi.item.id)
                    elif oi.item.owner.id == offer.receiver.id:
                        pending['receiver_bakugans'].append(oi.item.id)
                request.session['pending_offer'] = pending
                request.session.modified = True
            except Offer.DoesNotExist:
                request.session.pop('offer_id', None)
                return redirect('seek_users')
            
        pending = request.session.get('pending_offer')
        if pending and pending['sender_id'] and pending['receiver_id']:
            original_offer_id = request.session.get('original_offer')
            check = None
            if original_offer_id:
                original_offer = Offer.get_offer_by_id(original_offer_id)
                check = self.check_offers(pending, original_offer)
                if check == "edited":
                    request.session['editing'] = True
                if check == "same":
                    request.session['editing'] = False
                if check == "new trade":
                    self.clear_session_offer(request)
                    return redirect('seek_users')
            sender = User.get_user_by_id(pending['sender_id'])
            receiver = User.get_user_by_id(pending['receiver_id'])
            sender_price = pending['sender_price']
            receiver_price = pending['receiver_price']
            for ob_id in pending['sender_bakugans']:
                try:
                    ob = OwnedBakugan.get_owned_bakugan_by_id(ob_id)
                    sender_bakugans.append(ob)
                except OwnedBakugan.DoesNotExist:
                    pass
            for ob_id in pending['receiver_bakugans']:
                try:
                    ob = OwnedBakugan.get_owned_bakugan_by_id(ob_id)
                    receiver_bakugans.append(ob)
                except OwnedBakugan.DoesNotExist:
                    pass
        else:
            self.clear_session_offer(request)
            return redirect('seek_users')

        data = {}
        data['original_offer_id'] = original_offer_id
        request.session.pop("offer_id", None)
        data['editing'] = request.session['editing']
        data['sender'] = sender
        data['receiver'] = receiver
        data['sender_price'] = sender_price
        data['receiver_price'] = receiver_price
        data['sender_bakugans'] = sender_bakugans
        data['receiver_bakugans'] = receiver_bakugans
        
        data['check'] = check

        return render(request, 'trade.html', data)
    
    def post(self, request):
        create = request.POST.get('create')
        trade_result = request.POST.get('action')
        edit_trade = request.POST.get('edit-trade')
        clear = request.POST.get('clear')

        if clear:
            self.clear_session_offer(request)
            return redirect('homepage')

        if trade_result is not None:
            if trade_result == 'accept':
                pass
            elif trade_result == 'decline':
                pass
            else:
                logger.warning(f"Unexpected trade_result: {trade_result}")
                return redirect('homepage')

        if edit_trade:
            return redirect('userinv', edit_trade)
        
        if create:
            pending = request.session['pending_offer']
            try:
                new_offer = Offer(
                sender = User.get_user_by_id(pending['sender_id']),
                receiver = User.get_user_by_id(pending['receiver_id']),
                sender_price = int(pending['sender_price']),
                receiver_price = int(pending['receiver_price']),
                )
                new_offer.placeOffer()

                for ob_id in request.POST.getlist('sender_bakugans'):
                    new_offeritem = OfferItem(
                        offer=new_offer,
                        item_id=ob_id,
                        direction="giving",
                    )
                    new_offeritem.create_offer_item()
                    ob = OwnedBakugan.get_owned_bakugan_by_id(ob_id)
                    ob.is_offered = True
                    ob.save()
                for ob_id in request.POST.getlist('receiver_bakugans'):
                    new_offeritem = OfferItem(
                        offer=new_offer,
                        item_id=ob_id,
                        direction="asking",
                    )
                    new_offeritem.create_offer_item()

                request.session.pop('pending_offer', None)
                return redirect('homepage')
            except IntegrityError:
                request.session.pop('pending_offer', None)
                return redirect('seek_users')
        
        return redirect('homepage')
    
    def clear_session_offer(self, request):
        request.session.pop("pending_offer", None)
        request.session.pop("original_offer", None)
        request.session.pop("editing", None)
        return
    
    def check_offers(self, pending, original_offer):
        sender_id = original_offer.sender.id
        receiver_id = original_offer.receiver.id
        if sender_id != pending['sender_id'] or receiver_id != pending['receiver_id']:
            return "new trade"
        
        sender_price = original_offer.sender_price
        receiver_price = original_offer.receiver_price
        if sender_price != pending['sender_price'] or receiver_price != pending['receiver_price']:
            return "edited"
        
        original_sender_bakugans = []
        original_receiver_bakugans = []
        original_bakugans = OfferItem.get_offer_items_by_offer_id(original_offer.id)
        for oi in original_bakugans:
            if oi.item.owner.id == original_offer.sender.id:
                original_sender_bakugans.append(oi.item.id)
            elif oi.item.owner.id == original_offer.receiver.id:
                original_receiver_bakugans.append(oi.item.id)
        if set(original_sender_bakugans) != set(pending['sender_bakugans']) or set(original_receiver_bakugans) != set(pending['receiver_bakugans']):
            return "edited"
        
        return "same"