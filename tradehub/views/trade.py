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
        sender = None
        receiver = None
        sender_price = None
        receiver_price = None
        sender_bakugans = []
        receiver_bakugans = []

        if offer_id:
            try:
                offer = Offer.get_offer_by_id(offer_id)
                pending = {
                    'sender_id': offer.sender.id,
                    'receiver_id': offer.receiver.id,
                    'sender_price': offer.sender_price,
                    'receiver_price': offer.receiver_price,
                    'sender_bakugans': [],
                    'receiver_bakugans': [],
                }
                offered = OfferItem.get_offer_items_by_offer_id(offer_id)

                for oi in offered:
                    if oi.items.owner.id == offer.sender.id:
                        pending['sender_bakugans'].append(oi.items.id)
                    elif oi.items.owner.id == offer.receiver.id:
                        pending['receiver_bakugans'].append(oi.items.id)
                request.session['pending_offer'] = pending
                request.session.modified = True
            except Offer.DoesNotExist:
                request.session.pop('offer_id', None)
                return redirect('seek_users')
            
        pending = request.session.get('pending_offer')
        if pending and pending['sender_id'] and pending['receiver_id']:
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
            return redirect('seek_users')

        data = {}
        data['offer_id'] = offer_id
        data['sender'] = sender
        data['receiver'] = receiver
        data['sender_price'] = sender_price
        data['receiver_price'] = receiver_price
        data['sender_bakugans'] = sender_bakugans
        data['receiver_bakugans'] = receiver_bakugans

        request.session.pop('offer_id', None)

        return render(request, 'trade.html', data)
    
    def post(self, request):
        create = request.POST.get('create')
        trade_result = request.POST.get('action')
        edit_trade = request.POST.get('edit-trade')

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