from django.shortcuts import render, redirect
from django.views import View
from tradehub.models.attribute import Attribute
from tradehub.models.bakugan import OwnedBakugan
from tradehub.models.user import User
import logging

logger = logging.getLogger('django')

class Home(View):
    def post(self, request):
        user_id = request.session.get('user')
        if not user_id:
            logger.warning(f"Something went wrong. Non-user entered bakulist. Session User: {user}")
            redirect('homepage')
        
        return_url = request.Get.get('return_url')
        if return_url:
            return redirect(return_url)
        return render(request, 'home.html')
    
    def get(self, request):
        user_id = request.session.get('user')
        if not user_id:
            return render(request, 'home.html')
        user = User.get_user_by_id(user_id)
        user_bakugans = None
        current_attribute = request.GET.get('attribute')
        search_query = None

        if current_attribute:
            user_bakugans = OwnedBakugan.get_owned_bakugans_by_attribute(current_attribute)
        else:
            user_bakugans = OwnedBakugan.get_owned_bakugans_by_owner(user)
        
        if search_query:
            user_bakugans = user_bakugans.filter(name__icontains=search_query)

        data = {}
        data['user'] = user
        data['owned_bakugans'] = user_bakugans
        data['attributes'] = Attribute.get_all_attributes()

        return render(request, 'home.html', data)