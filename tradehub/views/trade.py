from django.db import IntegrityError
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from tradehub.models.bakugan import OwnedBakugan
from tradehub.models.offer import Offer, OfferItem
from tradehub.models.user import User
import datetime
import logging

logger = logging.getLogger('django')

class TradeMenu(View):
    def get(self, request):
        Offer.init_pending_offer(request)
        offer_id = request.session.get('offer_id') or request.GET.get("offer_id")
        request.session['offer_id'] = offer_id
        uid = request.session.get('user')
        sender = None
        receiver = None
        sender_price = None
        receiver_price = None
        sender_bakugans = []
        receiver_bakugans = []
        myoffer = None
        request.session.setdefault('editing', False)

        if not uid:
            return redirect('homepage')

        if offer_id:
            try:
                offer = Offer.get_offer_by_id(offer_id)
                previous_offer_id = request.session.get('original_offer')
                original_pending = request.session.get('pending_offer', {})
                sender = offer.sender.id
                receiver = offer.receiver.id

                has_previous = (
                    previous_offer_id == offer_id
                    and original_pending.get('sender_id') is not None
                )
                request.session.setdefault('has_previous', None)

                request.session['original_offer'] = offer_id

                if uid == sender:
                    myoffer = True

                offered = OfferItem.get_offer_items_by_offer_id(offer_id)

                if uid == sender:
                    pending = {
                        'sender_id': sender,
                        'receiver_id': receiver,
                        'sender_price': offer.sender_price,
                        'receiver_price': offer.receiver_price,
                        'sender_bakugans': [],
                        'receiver_bakugans': [],
                    }
                    db_sender = {
                        item.item_id
                        for item in offered
                        if item.direction == "giving"
                    }
                    db_receiver = {
                        item.item_id
                        for item in offered
                        if item.direction == "asking"
                    }
                else:
                    pending = {
                        'sender_id': receiver,
                        'receiver_id': sender,
                        'sender_price': offer.receiver_price,
                        'receiver_price': offer.sender_price,
                        'sender_bakugans': [],
                        'receiver_bakugans': [],
                    }
                    db_sender = {
                        item.item_id
                        for item in offered
                        if item.direction == "asking"
                    }
                    db_receiver = {
                        item.item_id
                        for item in offered
                        if item.direction == "giving"
                    }
                
                if has_previous:
                    pending_sender = {int(x) for x in original_pending['sender_bakugans']}
                    pending_receiver = {int(x) for x in original_pending['receiver_bakugans']}

                    unchanged_sender = db_sender & pending_sender
                    added_sender = pending_sender - db_sender

                    unchanged_receiver = db_receiver & pending_receiver
                    added_receiver = pending_receiver - db_receiver

                    pending['sender_bakugans'].extend(unchanged_sender)
                    pending['sender_bakugans'].extend(added_sender)
                    pending['receiver_bakugans'].extend(unchanged_receiver)
                    pending['receiver_bakugans'].extend(added_receiver)
                else:
                    pending['sender_bakugans'].extend(db_sender)
                    pending['receiver_bakugans'].extend(db_receiver)

                if receiver == uid and not offer.receiver_read:
                    offer.receiver_read = True
                    offer.save(update_fields=["receiver_read"])

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
                check = self.check_offers(request, pending, original_offer)
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
        data['editing'] = request.session['editing']
        data['sender'] = sender
        data['receiver'] = receiver
        data['sender_price'] = sender_price
        data['receiver_price'] = receiver_price
        data['sender_bakugans'] = sender_bakugans
        data['receiver_bakugans'] = receiver_bakugans
        data['my_offer'] = myoffer
        
        data['check'] = check

        return render(request, 'trade.html', data)
    
    def post(self, request):
        print("TOP OF POST")
        create = request.POST.get('create')
        print(request.POST)
        trade_result = request.POST.get('action')
        print(trade_result)
        edit_trade = request.POST.get('edit-trade')
        clear = request.POST.get('clear')
        update = request.POST.get('update')
        pending = request.session.get('pending_offer')
        uid = request.session.get('user')
        sender_id = pending['sender_id']
        receiver_id = pending['receiver_id']
        existing_offer = None
        myoffer = request.session.get('myoffer', None)
        print(f"PENDING: {pending}")
        print(myoffer)

        if not uid:
            return redirect('homepage')

        if clear:
            self.clear_session_offer(request)
            return redirect('homepage')
        
        if pending:
            try:
                print(request.session['offer_id'])
                existing_offer = Offer.get_offer_by_id(request.session['offer_id'])
            except Offer.DoesNotExist:
                pass
            print(existing_offer)

        if existing_offer:
            print(f"INSIDE IF STATEMENT")
            if update:
                print("PROBLEM HERE not updating offer when pressed")
                if uid == existing_offer.sender_id:
                    sender = User.get_user_by_id(sender_id)
                    receiver = User.get_user_by_id(receiver_id)
                    existing_offer.sender_price = pending['sender_price']
                    existing_offer.receiver_price = pending['receiver_price']
                elif uid == existing_offer.receiver_id:
                    print("I BE DA RECIEVER")
                    print(request.session['has_previous'])
                    receiver = User.get_user_by_id(sender_id)
                    sender = User.get_user_by_id(receiver_id)
                    existing_offer.sender_price = pending['receiver_price']
                    existing_offer.receiver_price = pending['sender_price']
                    temp_list = pending['sender_bakugans']
                    pending['sender_bakugans'] = pending['receiver_bakugans']
                    pending['receiver_bakugans'] = temp_list
                    temp_user = pending['sender_id']
                    pending['sender_id'] = pending['receiver_id']
                    pending['receiver_id'] = temp_user
                    temp_price = pending['sender_price']
                    pending['sender_price'] = pending['receiver_price']
                    pending['receiver_price'] = temp_price
                existing_offer.sender = sender
                existing_offer.receiver = receiver
                existing_offer.date = datetime.date.today()
                existing_offer.receiver_read = False

                existing_offer.save()
                request.session['editing'] = False
                print(request.session['editing'])

                if pending['sender_bakugans']:
                    for ob_id in pending['sender_bakugans']:
                        ob = OwnedBakugan.get_owned_bakugan_by_id(ob_id)
                        print(f"SENDER: {ob}")
                        ob.is_offered = True
                        oi = OfferItem.get_offer_items_by_owned_bakugan_id(ob_id).filter(offer_id=existing_offer.id).first()
                        
                        if oi is None:
                            print("are we here")
                            print(oi)
                            new_oi = OfferItem(
                                offer = existing_offer,
                                item = ob,
                                direction = "sending",
                            )
                            new_oi.create_offer_item()
                        else:
                            print("BEFORE SET", oi.id, oi.direction)
                            oi.direction = "giving"
                            print("AFTER SET:", oi.id, oi.direction)
                            oi.save()
                            oi.refresh_from_db
                            print("AFTER REFRESH:", oi.id, oi.direction)
                if pending['receiver_bakugans']:
                    for ob_id in pending['receiver_bakugans']:
                        ob = OwnedBakugan.get_owned_bakugan_by_id(ob_id)
                        ob.is_offered = False
                        oi = OfferItem.get_offer_items_by_owned_bakugan_id(ob_id).filter(offer_id=existing_offer.id).first()

                        if oi is None:
                            new_oi = OfferItem(
                                offer = existing_offer,
                                item = ob,
                                direction = "receiving",
                            )
                            new_oi.create_offer_item()
                        else:
                            print("BEFORE SET", oi.id, oi.direction)
                            oi.direction = "asking"
                            print("AFTER SET:", oi.id, oi.direction)
                            oi.save()
                            oi.refresh_from_db
                            print("AFTER REFRESH:", oi.id, oi.direction)

                removed_senders = OfferItem.get_offer_items_by_offer_id(existing_offer.id).filter(item__id__in=pending['sender_bakugans'])
                removed_senders = removed_senders.exclude(item_id__in=pending['sender_bakugans'])
                for removed_sender in removed_senders:
                    ob = OwnedBakugan.get_owned_bakugan_by_id(removed_sender.item.id)
                    ob.is_offered = False
                    ob.save()

                removed_ois = OfferItem.get_offer_items_by_offer_id(existing_offer.id)
                removed_ois = removed_ois.exclude(item_id__in=pending['receiver_bakugans'])
                removed_ois = removed_ois.exclude(item_id__in=pending['sender_bakugans'])
                removed_ois.delete()

            if trade_result is not None:
                if trade_result == 'accept':
                    for ob in pending['sender_bakugans']:
                        pass
                elif trade_result == 'decline':
                    removed_senders = OfferItem.get_offer_items_by_offer_id(existing_offer.id).filter(item__id__in=pending['sender_bakugans'])
                    for removed_sender in removed_senders:
                        ob = OwnedBakugan.get_owned_bakugan_by_id(removed_sender.item.id)
                        ob.is_offered = False
                        ob.save()
                    existing_offer.delete()
                    self.clear_session_offer(request);
                    return redirect('homepage')
                else:
                    logger.warning(f"Unexpected trade_result: {trade_result}")
                    return redirect('homepage')

        if edit_trade:
            return redirect('userinv', edit_trade)
        
        if create:
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
    
    def check_offers(self, request, pending, original_offer):
        if not original_offer:
            return "new trade"
        
        uid = request.session.get('user')
        
        sender_price = original_offer.sender_price
        receiver_price = original_offer.receiver_price
        if sender_price != pending['sender_price'] or receiver_price != pending['receiver_price']:
            return "edited"
        
        original_sender_bakugans = []
        original_receiver_bakugans = []
        original_bakugans = OfferItem.get_offer_items_by_offer_id(original_offer.id)
        if uid == original_offer.sender.id:
            for oi in original_bakugans:
                if oi.item.owner.id == original_offer.sender.id:
                    original_sender_bakugans.append(oi.item.id)
                elif oi.item.owner.id == original_offer.receiver.id:
                    original_receiver_bakugans.append(oi.item.id)
        else:
            for oi in original_bakugans:
                if oi.item.owner.id == original_offer.sender.id:
                    original_receiver_bakugans.append(oi.item.id)
                elif oi.item.owner.id == original_offer.receiver.id:
                    original_sender_bakugans.append(oi.item.id)
        if set(original_sender_bakugans) != set(pending['sender_bakugans']) or set(original_receiver_bakugans) != set(pending['receiver_bakugans']):
            return "edited"
        
        return "same"