from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
urlpatterns = [
    path('api/', include('core.urls')),
    path('api/', include('accounts.urls')),
    path('api/', include('elections.urls')),
    path('api/', include('voting.urls')),
    path('api/', include('results.urls')),
    path('api/', include('monitoring.urls')),
    path('api/', include('audit.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
