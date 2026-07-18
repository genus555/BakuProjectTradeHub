from django.db import IntegrityError, transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from tradehub.models.bakugan import OwnedBakugan
from tradehub.models.offer import CompletedOffer, Offer, OfferItem
from tradehub.models.user import User
import datetime
import logging
logger = logging.getLogger('django')

class TradeMenu(View):
    def get(self, request):
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
        empty_pending = {
                        'sender_id': None,
                        'receiver_id': None,
                        'sender_price': 0,
                        'receiver_price': 0,
                        'sender_bakugans': [],
                        'receiver_bakugans': [],
                    }

        if not uid:
            return redirect('homepage')

        if offer_id:
            try:
                original_pending = request.session.get('pending_offer', {})
                offer = Offer.get_offer_by_id(offer_id)
                if not original_pending:
                    Offer.init_pending_offer(request)
                    original_pending = {
                        'sender_id': offer.sender.id,
                        'receiver_id': offer.receiver.id,
                        'sender_price': offer.sender_price,
                        'receiver_price': offer.receiver_price,
                        'sender_bakugans': [],
                        'receiver_bakugans': [],
                    }
                previous_offer_id = request.session.get('original_offer')
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

                if uid == sender and request.session['pending_offer'] == empty_pending:
                    pending = {
                        'sender_id': sender,
                        'receiver_id': receiver,
                        'sender_price': original_pending['sender_price'],
                        'receiver_price': original_pending['receiver_price'],
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
                elif request.session['pending_offer'] == empty_pending and uid == receiver:
                    pending = {
                        'sender_id': receiver,
                        'receiver_id': sender,
                        'sender_price': original_pending['receiver_price'],
                        'receiver_price': original_pending['sender_price'],
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
                
                if has_previous and request.session['pending_offer'] == empty_pending:
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
                elif not has_previous and request.session['pending_offer'] == empty_pending:
                    pending['sender_bakugans'].extend(db_sender)
                    pending['receiver_bakugans'].extend(db_receiver)

                if receiver == uid and not offer.receiver_read:
                    offer.receiver_read = True
                    offer.save(update_fields=["receiver_read"])

                if request.session['pending_offer'] == empty_pending:
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
                try:
                    original_offer = Offer.get_offer_by_id(original_offer_id)
                except Exception:
                    logger.exception(f"Failed to get original_offer from offer_id: {original_offer_id}")
                    self.clear_session_offer(request)
                    return redirect('homepage')
                check = self.check_offers(request, pending, original_offer)
                if check == "edited":
                    request.session['editing'] = True
                elif check == "same":
                    request.session['editing'] = False
                elif check == "new trade":
                    self.clear_session_offer(request)
                    return redirect('seek_users')
                else:
                    logger.warning(f"something went wrong with check: {check}")
                    return redirect('homepage')
            sender = User.get_user_by_id(pending['sender_id'])
            receiver = User.get_user_by_id(pending['receiver_id'])
            sender_price = pending['sender_price']
            receiver_price = pending['receiver_price']
            sender_bakugans = []
            receiver_bakugans = []
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
        create = request.POST.get('create')
        trade_result = request.POST.get('action')
        edit_trade = request.POST.get('edit-trade')
        clear = request.POST.get('clear')
        update = request.POST.get('update')
        pending = request.session.get('pending_offer')
        uid = request.session.get('user')
        existing_offer = None
        original_offer = request.session.get('original_offer')

        if not uid:
            return redirect('homepage')

        if clear:
            self.clear_session_offer(request)
            return redirect('homepage')
        
        if pending:
            try:
                existing_offer = Offer.get_offer_by_id(request.session['offer_id'])
            except Offer.DoesNotExist:
                pass

        if existing_offer:
            if update:
                if pending['sender_price'] is None:
                    pending['sender_price'] = 0
                if pending['receiver_price'] is None:
                    pending['receiver_price'] = 0
                sender = User.get_user_by_id(pending['sender_id'])
                receiver = User.get_user_by_id(pending['receiver_id'])
                existing_offer.sender = sender
                existing_offer.receiver = receiver
                existing_offer.sender_price = pending['sender_price']
                existing_offer.receiver_price = pending['receiver_price']
                existing_offer.date = datetime.date.today()
                existing_offer.receiver_read = False

                existing_offer.save()
                request.session['editing'] = False

                if pending['sender_bakugans']:
                    for ob_id in pending['sender_bakugans']:
                        ob = OwnedBakugan.get_owned_bakugan_by_id(ob_id)
                        ob.is_offered = True
                        ob.save()
                        oi = OfferItem.get_offer_items_by_owned_bakugan_id(ob_id).filter(offer_id=existing_offer.id).first()

                        if oi is None:
                            new_oi = OfferItem(
                                offer = existing_offer,
                                item = ob,
                                direction = "giving",
                            )
                            new_oi.create_offer_item()
                        else:
                            oi.direction = "giving"
                            oi.save()
                            oi.refresh_from_db
                if pending['receiver_bakugans']:
                    for ob_id in pending['receiver_bakugans']:
                        ob = OwnedBakugan.get_owned_bakugan_by_id(ob_id)
                        ob.is_offered = False
                        ob.save()
                        oi = OfferItem.get_offer_items_by_owned_bakugan_id(ob_id).filter(offer_id=existing_offer.id).first()

                        if oi is None:
                            new_oi = OfferItem(
                                offer = existing_offer,
                                item = ob,
                                direction = "asking",
                            )
                            new_oi.create_offer_item()
                        else:
                            oi.direction = "asking"
                            oi.save()
                            oi.refresh_from_db

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
                self.clear_session_offer(request)

            if trade_result is not None:
                if trade_result == 'accept':
                    offer = Offer.get_offer_by_id(request.session['original_offer'])
                    sender_discord_name = offer.sender.discord_name
                    receiver_discord_name = offer.receiver.discord_name
                    sender_bakugans = []
                    receiver_bakugans = []
                    all_involved_bakugans = []
                    if uid == offer.receiver.id and uid == pending['sender_id']:
                        try:
                            with transaction.atomic():
                                for ob_id in pending['receiver_bakugans']:
                                    all_involved_bakugans.append(ob_id)
                                    sender_ob = OwnedBakugan.get_owned_bakugan_by_id(ob_id)
                                    sender_bakugans.append(f"{sender_ob.owner.discord_name}'s {sender_ob.power} {sender_ob.bakugan.attribute} {sender_ob.bakugan.name}")
                                    sender_ob.owner = offer.receiver
                                    sender_ob.is_offered = False
                                    sender_ob.save()
                                for ob_id in pending['sender_bakugans']:
                                    all_involved_bakugans.append(ob_id)
                                    receiver_ob = OwnedBakugan.get_owned_bakugan_by_id(ob_id)
                                    receiver_bakugans.append(f"{receiver_ob.owner.discord_name}'s {receiver_ob.power} {receiver_ob.bakugan.attribute} {receiver_ob.bakugan.name}")
                                    receiver_ob.owner = offer.sender
                                    receiver_ob.is_offered = False
                                    receiver_ob.save()
                                completed_offer = CompletedOffer(
                                    sender_discord_name = sender_discord_name,
                                    receiver_discord_name = receiver_discord_name,
                                    sender_price = pending['receiver_price'],
                                    receiver_price = pending['sender_price'],
                                    sender_bakugans = sender_bakugans,
                                    receiver_bakugans = receiver_bakugans,
                                )
                                completed_offer.full_clean()
                                completed_offer.save()

                                all_tied_offer_ids = []
                                for ob_id in all_involved_bakugans:
                                    ois = OfferItem.get_offer_items_by_owned_bakugan_id(ob_id)
                                    if ois:
                                        for oi in ois:
                                            all_tied_offer_ids.append(oi.offer.id)
                                for offer_id in all_tied_offer_ids:
                                    Offer.objects.filter(id=offer_id).delete()
                                self.clear_session_offer(request)
                        except Exception as e:
                            logger.warning(f"Something went wrong with changing ownership and making compelted offer. Exception: {e}")
                            self.clear_session_offer(request)
                            return redirect('homepage')
                    else:
                        logger.warning(f"Something went wrong with accept. UID: {uid} | Offer: {offer} | Session pending: {pending}")
                        self.clear_session_offer(request)
                        return redirect('homepage')
                elif trade_result == 'decline':
                    removed_senders = OfferItem.get_offer_items_by_offer_id(original_offer)
                    for removed_sender in removed_senders:
                        if removed_sender.direction == "giving":
                            ob = removed_sender.item
                            ob.is_offered = False
                            ob.save()
                    existing_offer.delete()
                    self.clear_session_offer(request)
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
        original_sender_bakugans = []
        original_receiver_bakugans = []
        original_bakugans = OfferItem.get_offer_items_by_offer_id(original_offer.id)
        check_offer = {
                        'sender_id': None,
                        'receiver_id': None,
                        'sender_price': 0,
                        'receiver_price': 0,
                        'sender_bakugans': [],
                        'receiver_bakugans': [],
                    }

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

        if uid == original_offer.sender_id:
            check_offer['sender_id'] = pending['sender_id']
            check_offer['receiver_id'] = pending['receiver_id']
            check_offer['sender_price'] = pending['sender_price']
            check_offer['receiver_price'] = pending['receiver_price']
        elif uid == original_offer.receiver_id:
            check_offer['sender_id'] = pending['receiver_id']
            check_offer['receiver_id'] = pending['sender_id']
            check_offer['sender_price'] = pending['receiver_price']
            check_offer['receiver_price'] = pending['sender_price']

        check_offer['sender_bakugans'] = pending['sender_bakugans']
        check_offer['receiver_bakugans'] = pending['receiver_bakugans']
        
        if sender_price != check_offer['sender_price'] or receiver_price != check_offer['receiver_price']:
            return "edited"
        if set(original_sender_bakugans) != set(check_offer['sender_bakugans']) or set(original_receiver_bakugans) != set(check_offer['receiver_bakugans']):
            return "edited"
        
        return "same"