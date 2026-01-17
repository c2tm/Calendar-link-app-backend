from django.urls import path
from . import views

urlpatterns = [
    path("getEventLink/", views.getEventLink.as_view(), name="get_event_link"),
    path("getOrUpdateUser/<int:pk>/", views.GetUpdateUserView.as_view(), name="get_or_update_user"),
    #path("webhooks/whop/", views.whop_webhook, name="whop_webhook")
]