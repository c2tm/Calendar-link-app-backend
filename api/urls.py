from django.urls import path
from . import views

urlpatterns = [
    path("getEventLink/", views.getEventLink.as_view(), name="get_event_link"),
    path("getOrUpdateUser/<int:pk>/", views.GetUpdateUserView.as_view(), name="get_or_update_user"),
    path("download/<path:key>/", views.DownloadIcsView.as_view(), name="download-ics")
    #path("webhooks/whop/", views.whop_webhook, name="whop_webhook")
]