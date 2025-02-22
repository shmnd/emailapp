from django.urls import include, path, re_path
from . import views
from authentication.views import UserRegisterView,UserLoginView,LogoutView
app_name = 'authentication'

urlpatterns = [
    path("signup/medico/check/admin", UserRegisterView.as_view(), name="signup"),
    path("login/", UserLoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout'),
]