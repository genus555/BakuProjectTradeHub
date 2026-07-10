from django.urls import path
from .views.home import Home
from .views.login import Login, logout
from .views.signup import Signup, OTP_Setup

urlpatterns = [
    path('', Home.as_view(), name='homepage'),
    path('home', Home.as_view(), name='home'),
    path('signup', Signup.as_view(), name='signup'),
    path('otp_setup', OTP_Setup.as_view(), name='otp_setup'),
    path('login', Login.as_view(), name='login'),
    path('logout', logout, name='logout'),
]