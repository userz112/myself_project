from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import urls as users_urls
from listings import urls as listings_urls
from assistant import urls as assistant_urls


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/users/', include(users_urls)),
    path('api/listings/', include(listings_urls)),
    path('api/assistant/', include(assistant_urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) # 用于开发环境，实际部署时注释掉
