from django.shortcuts import render, redirect
from django.views import View
from tradehub.models.user import User

import io
import base64
import pyotp
import qrcode
import logging

logger = logging.getLogger('django')

class Signup(View):
    def get(self, request):
        return render(request, 'signup.html')
    
    def post(self, request):
        ign = request.POST.get('ign')
        discord_name = request.POST.get('discord_name')
        otp_secret = pyotp.random_base32()

        user = User(
            ign = ign,
            discord_name = discord_name,
            otp_secret = otp_secret
        )
        request.session["pending_signup"] = {
            'ign': ign,
            'discord_name': discord_name,
            'otp_secret': otp_secret,
        }
        error_message = self.validateUser(user)

        if error_message:
            data = {
                    'error': error_message,
                    'values': request.session.get("pending_signup")
                }
            del request.session["pending_signup"]
            return render(request, 'signup.html', data)

        return redirect("otp_setup")

    def validateUser(self, user):
        error_message = None
        if (not user.ign):
            error_message = "Please enter your in game name."
        elif (not user.discord_name):
            error_message = "Please enter your discord name."
        elif user.isExists():
            error_message = "This in game name is already registered"
            logger.warning(f"Already registered. Attempted values: IGN: \"{user.discord_name}\" | Discord Name: \"{user.ign}\"")
        return error_message
    
class OTP_Setup(View):
    def get(self, request):
        pending = request.session.get("pending_signup")
        if not pending:
            logger.warning(f"otp set up page entered without a pending signup")
            return redirect("signup")
        
        totp = pyotp.TOTP(pending["otp_secret"])
        uri = totp.provisioning_uri(name=pending['discord_name'], issuer_name="BPTradeHub")

        img = qrcode.make(uri)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        qr_b64 = base64.b64encode(buf.getvalue()).decode()
        request.session["qr_b64"] = qr_b64
        
        return render(request, "otp_setup.html", {"qr_b64": qr_b64})
    
    def post(self, request):
        pending = request.session.get("pending_signup")
        code = request.POST["otp_code"]
        totp = pyotp.TOTP(pending["otp_secret"])
        qr_b64 = request.session.get("qr_b64")

        if totp.verify(code):
            user = User(
                ign = pending["ign"],
                discord_name = pending["discord_name"],
                otp_secret = pending["otp_secret"],
            )
            user.register()
            request.session['user'] = user.id
            del request.session["pending_signup"]
            del request.session["qr_b64"]
            logger.info(f"New user registered: IGN: \"{user.discord_name}\" | Discord Name: \"{user.ign}\"")
            return redirect('homepage')
        
        return render(request, "otp_setup.html", {"qr_b64": qr_b64, "error": "Invalid code"})