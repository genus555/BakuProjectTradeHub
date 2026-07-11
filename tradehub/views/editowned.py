from django.shortcuts import render, redirect
from django.views import View
from tradehub.models.bakugan import OwnedBakugan
import logging

logger = logging.getLogger('django')

class EditOwned(View):
    def post(self, request, ob_id):
        owned = OwnedBakugan.get_owned_bakugan_by_id(id=ob_id)

        if request.POST.get("action") == "remove":
            owned.delete()
            return redirect('homepage')
        
        edited = owned.edit(request.POST)
        if not edited:
            request.session['edited'] = edited
            return redirect('editowned', ob_id=ob_id)

        return redirect('homepage')
    
    def get(self, request, ob_id):
        owned = OwnedBakugan.get_owned_bakugan_by_id(id=ob_id)
        user = request.session.get('user')
        edited = request.session.pop('edited', None)
        print(user)
        print(owned.owner)
        if not user == owned.owner.id:
            logger.warning(f"Non-owner editing bakugan. Owner: \"{owned.owner}\" | Editor: \"{user}\"")
            return redirect('homepage')

        data = {}
        data['edited'] = edited
        data['ownedbakugan'] = owned
        data['bakugan'] = owned.bakugan
        data['power'] = owned.power
        data['trade_type'] = owned.trade_type
        data['price'] = owned.price
        return render(request, 'editowned.html', data)