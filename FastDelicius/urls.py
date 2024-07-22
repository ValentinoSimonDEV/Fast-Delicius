from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path , include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
openapi.Info(
    title="API Fast Delicius",
    default_version='v1',
    description="Documentación de la API de Comida Rápida",
    terms_of_service="https://www.google.com/policies/terms/",
    contact=openapi.Contact(email="contact@fastdelicius.local"),
    license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
    url='https://improved-disco-pjg9xrqgqgprh6qp9-8000.app.github.dev/',

)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Products.urls')),
    path('', include('Accounts.urls')),
    path('cart/' , include('Cart.urls')),
    path('' , include('Orders.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

urlpatterns += static(settings.MEDIA_URL , document_root=settings.MEDIA_ROOT)
