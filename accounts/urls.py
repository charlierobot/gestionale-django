from django.urls import path
from django.contrib.auth.views import LogoutView, LoginView
from .views import CustomLoginView
from .views import registrazione
app_name = 'accounts'

urlpatterns = [
    path('registrazione/', registrazione, name='registrazione'),
    path('login/', CustomLoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
