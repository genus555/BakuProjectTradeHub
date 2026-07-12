from django.shortcuts import render, redirect
from django.views import View
from tradehub.models.bakugan import Attribute
from tradehub.models.bakugan import OwnedBakugan
from tradehub.models.user import User

class UserInv(View):
    def post(self, request, owner_id):
        offered_ids = request.POST.getlist("offered_bakugan")
        uid = request.session.get('user')
        price = int(request.POST.get('offered_price') or 0)

        if not uid:
            return redirect('homepage')
        if not offered_ids:
            return redirect('userinv', owner_id)
        
        offer = {}
        offer['sender_id'] = uid
        offer['receiver_id'] = owner_id
        offer['receiver_price'] = price
        offer['offered_ids'] = offered_ids

        request.session['pending_offer'] = offer

        return redirect('homepage')
    
    def get(self, request, owner_id):
        owner = User.get_user_by_id(owner_id)
        owner_bakugans = OwnedBakugan.get_owned_bakugans_by_owner(owner_id)
        current_attribute = request.GET.get('attribute')
        search_query = request.GET.get('search')
        pending_offer = request.session.get('pending_offer')
        price = 0
        pending_bakugans = []

        if pending_offer and pending_offer['receiver_id'] == owner_id:
            pending_bakugans = OwnedBakugan.objects.filter(id__in=pending_offer['offered_ids'])
            price = pending_offer['receiver_price']

        if current_attribute:
            owner_bakugans = owner_bakugans.filter(bakugan__attribute=current_attribute)
        if search_query:
            owner_bakugans = owner_bakugans.filter(bakugan__name__icontains=search_query)

        data = {}
        data['attributes'] = Attribute.get_all_attributes()
        data['owner'] = owner
        data['owner_id'] = owner_id
        data['owner_bakugans'] = owner_bakugans
        data['pending_bakugans'] = pending_bakugans
        data['pending_price'] = price

        return render(request, 'user_inv.html', data)