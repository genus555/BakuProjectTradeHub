from django.shortcuts import render, redirect
from django.db.models import Q
from django.views import View
from tradehub.models.attribute import Attribute
from tradehub.models.bakugan import OwnedBakugan
from tradehub.models.user import User
import logging

logger = logging.getLogger('django')

class SeekUsers(View):
    def post(self, request):
        change_filter = request.POST.get('change_filter')
        if change_filter:
            request.session['seek_type'] = 'bakugans'
            return redirect('seek_owned')

        logger.warning(f"Unintented Post Request: {request.POST.dict()}")
        return redirect('homepage')
    
    def get(self, request):
        seek_type = request.session.get('seek_type')
        uid = request.session.get('user')
        user = User.get_user_by_id(uid)
        all_users = User.objects.exclude(id=uid)
        search_query = request.GET.get('search')

        if not user:
            return redirect('homepage')
        if not seek_type:
            request.session['seek_type'] = 'users'
            seek_type = 'users'
        if seek_type == 'bakugans':
            return redirect('seek_owned')
        elif seek_type != 'users':
            logger.warning(f"Unrecognized seek type. Session seek_type: {seek_type}")
            return redirect('homepage')

        if search_query:
            all_users = all_users.filter(
                Q(discord_name__icontains=search_query) |
                Q(ign__icontains=search_query)
            )
        
        data = {}
        data['all_users'] = all_users

        return render(request, 'seek_users.html', data)
    
class SeekOwned(View):
    def post(self, request):
        change_filter = request.POST.get('change_filter')
        if change_filter:
            request.session['seek_type'] = 'users'
            return redirect('seek_users')

        logger.warning(f"Unintented Post Request: {request.POST.dict()}")
        return redirect('homepage')
    
    def get(self, request):
        seek_type = request.session.get('seek_type')
        uid = request.session.get('user')
        user = User.get_user_by_id(uid)
        all_owned = OwnedBakugan.get_all_owned_bakugan().exclude(owner=user)
        search_query = request.GET.get('search')

        if not user:
            return redirect('homepage')
        if not seek_type:
            request.session['seek_type'] = 'bakugans'
            seek_type = 'bakugans'
        if seek_type == 'users':
            return redirect('seek_users')
        elif seek_type != 'bakugans':
            logger.warning(f"Unrecognized seek type. Session seek_type: {seek_type}")
            return redirect('homepage')
        
        if search_query:
            search_params = search_query.lower().split()
            attributes = [
                attribute.name.lower()
                for attribute in Attribute.get_all_attributes()
            ]

            filter_query = Q()
            digits = []
            attrs = []
            texts = []

            for param in search_params:
                if param.isdigit():
                    digits.append(int(param))
                elif param in attributes:
                    attrs.append(param)
                else:
                    texts.append(param)
            
            if digits:
                filter_query &= Q(power__gte=max(digits))
            if attrs:
                attrs_query = Q()
                for attr in attrs:
                    attrs_query |= Q(bakugan__attribute__name__iexact=attr)
                filter_query &= attrs_query
            for text in texts:
                filter_query &= Q(bakugan__name__icontains=text)
            
            all_owned = all_owned.filter(filter_query)

        data = {}
        data['all_owned'] = all_owned

        return render(request, 'seek_owned.html', data)