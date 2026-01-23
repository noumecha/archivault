from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),

    # Dashboard urls
    path("", include("apps.dashboards.urls")),

    # layouts urls
    path("", include("apps.layouts.urls")),

    # Pages urls
    path("", include("apps.pages.urls")),

    # Auth urls
    path("", include("apps.authentication.urls")),

    # Card urls
    path("", include("apps.cards.urls")),

    # UI urls
    path("", include("apps.ui.urls")),

    # Extended UI urls
    path("", include("apps.extended_ui.urls")),

    # Icons urls
    path("", include("apps.icons.urls")),

    # Forms urls
    path("", include("apps.forms.urls")),

    # FormLayouts urls
    path("", include("apps.form_layouts.urls")),

    # Tables urls
    path("", include("apps.tables.urls")),
    # apps urls
    path('', include('apps.documents.urls')),
    path('', include('apps.administration.urls')),
    path('circulation', include('apps.circulation.urls')),
    path('historique', include('apps.historique.urls')),
    path('thematique', include('apps.thematique.urls')),
    path('rapports', include('apps.rapports.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('', include('apps.users.urls')),
    # autoreload browser dev
    path("__reload__/", include("django_browser_reload.urls"))
]

handler403 = "config.views.custom_permission_denied_view"
handler404 = "config.views.custom_page_not_found_view"
handler500 = "config.views.custom_server_error_view"

# form files
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
