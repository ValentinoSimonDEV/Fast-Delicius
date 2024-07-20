from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path , include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Products.urls')),
    path('', include('Accounts.urls')),
    path('cart/' , include('Cart.urls')),
    path('' , include('Orders.urls'))
]

urlpatterns += static(settings.MEDIA_URL , document_root=settings.MEDIA_ROOT)
