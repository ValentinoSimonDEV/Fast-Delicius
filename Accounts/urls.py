from django.urls import path
from .views import login_view, logout

urlpatterns = [
    path('login/', login_view.as_view(), name='login_view'),

]