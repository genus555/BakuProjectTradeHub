from django.db.models import Q
from django.shortcuts import render, redirect
from django.views import View
from tradehub.models.offer import Offer
import logging

logger = logging.getLogger('django')

class ViewOffers(View):
    def get(self, request):
        uid = request.session.get('user')
        if not uid:
            return redirect('homepage')
        
        direction = request.session.setdefault("direction", "sending")
        offers = Offer.get_user_offers(uid, direction)
        search_query = request.GET.get('search')

        if search_query:
            search_params = search_query.lower().split()

            filter_query = Q()
            digits = []
            texts = []
            
            for param in search_params:
                if param.isdigit():
                    digits.append(int(param))
                else:
                    texts.append(param)
            
            if digits:
                filter_query &= (
                    Q(sender_price__gte=max(digits)) |
                    Q(receiver_price__gte=max(digits))
                )
            for text in texts:
                filter_query &= (
                    Q(sender__discord_name__icontains=text) |
                    Q(sender__ign__icontains=text) |
                    Q(receiver__discord_name__icontains=text) |
                    Q(receiver__ign__icontains=text)
                )
            
            offers = offers.filter(filter_query)

        data = {}
        data['direction'] = direction
        data['offers'] = offers

        return render(request, 'seek_offers.html', data)
    
    def post(self, request):
        direction = request.session.get('direction')
        change_filter = request.POST.get('change_filter')
        if change_filter:
            if direction == "sending":
                request.session['direction'] = "receiving"
            elif direction == "receiving":
                request.session['direction'] = "sending"
            else:
                return redirect('homepage')
            return redirect('viewoffers')
        return redirect('homepage')