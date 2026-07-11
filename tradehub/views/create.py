from django.shortcuts import render, redirect, HttpResponseRedirect
from django.views import View
from tradehub.models.attribute import Attribute
from tradehub.models.bakugan import Bakugan, OwnedBakugan
from tradehub.models.user import User
    
class Create(View):
    def post(self, request):
        bakugan_id = request.POST.get('bakugan')
        power = request.POST.get('power')
        owner_id = request.session.get('user')
        trade_type = request.POST.get('trade_type')
        price = request.POST.get('price')
        if not price:
            price = 0

        bakugan = Bakugan.get_bakugan_by_id(bakugan_id)
        owner = User.get_user_by_id(owner_id)

        registered_bakugan = OwnedBakugan(
            bakugan = bakugan,
            power = power,
            owner = owner,
            trade_type = trade_type,
            is_offered = False,
            price = price
        )
        registered_bakugan.create()

        return_url = request.GET.get('return_url')
        if return_url:
            return redirect(return_url)
        return redirect('create')

    def get(self, request):
        bakugans = None
        attributes = Attribute.get_all_attributes()
        attributeID = request.GET.get('attribute')
        search_query = request.GET.get('search')
        user = request.GET.get('user')

        if attributeID:
            bakugans = Bakugan.get_all_bakugan_by_attributeid(attributeID)
        else:
            bakugans = Bakugan.get_all_bakugan()
        
        if search_query:
            bakugans = bakugans.filter(name__icontains=search_query)

        data = {}
        data['bakugans'] = bakugans
        data['attributes'] = attributes
        data['user'] = user

        return render(request, 'create.html', data)