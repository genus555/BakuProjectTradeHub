from django.urls import path
from .views.home import Home
from .views.create import Create
from .views.editowned import EditOwned
from .views.login import Login, logout
from .views.seek import SeekOwned, SeekUsers
from .views.signup import Signup, OTP_Setup
from .views.userinv import UserInv

urlpatterns = [
    path('', Home.as_view(), name='homepage'),
    path('create', Create.as_view(), name='create'),
    path('editowned/<int:ob_id>', EditOwned.as_view(), name='editowned'),
    path('home', Home.as_view(), name='home'),
    path('login', Login.as_view(), name='login'),
    path('logout', logout, name='logout'),
    path('otp_setup', OTP_Setup.as_view(), name='otp_setup'),
    path('seek_owned', SeekOwned.as_view(), name='seek_owned'),
    path('seek_users', SeekUsers.as_view(), name='seek_users'),
    path('signup', Signup.as_view(), name='signup'),
    path('userinv/<int:owner_id>', UserInv.as_view(), name='userinv'),
]