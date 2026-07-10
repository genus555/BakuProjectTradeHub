import pyotp
from django.shortcuts import render, redirect
from django.views import View
from tradehub.models.user import User
import logging

logger = logging.getLogger('django')

class Login(View):
    def get(self, request):
        return render(request, 'login.html')
    
    def post(self, request):
        discord_name = request.POST.get('discord_name')
        otp_code = request.POST.get('otp_code')
        user = User.get_user_by_discord_name(discord_name)
        error_message = None
        if user:
            totp = pyotp.TOTP(user.otp_secret)
            if totp.verify(otp_code):
                request.session['user'] = user.id
                logger.info(f"Login sucessful: Discord Name: \"{discord_name}\" | OTP: \"{otp_code}\"")
                return redirect('homepage')
            else:
                error_message = 'Password incorrect.'
                logger.warning(f"Incorrect OTP code. Attempted Values: Discord Name: \"{discord_name}\" | OTP: \"{otp_code}\"")
        else:
            error_message = 'Discord name is incorrect.'
            logger.warning(f"Incorrect Discord Name. Attempted Value: Discord Name: \"{discord_name}\" | OTP: \"{otp_code}\"")
        
        value = {
            'discord_name': discord_name,
        }
        return render(request, 'login.html', {
            'error': error_message,
            'values': value
            })

def logout(request):
    request.session.clear()
    return redirect('homepage')