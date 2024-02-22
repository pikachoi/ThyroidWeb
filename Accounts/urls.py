from django.urls import path
from .views import *

urlpatterns = [
    path("login/", login_view, name = "login"),
    path("logout/", logout_view, name = "logout"),
    path("signup/", signup_view, name = "signup"),
    path('id_search/', id_search, name='id_search'),
    path('password_search/', password_search, name='password_search'),
    path('password_reset/', password_reset, name='password_reset'),

]
