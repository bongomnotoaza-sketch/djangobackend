from django.urls import path
from .views import UpdatesView,UpdatesGetView


urlpatterns = [
    path("create-updates/", UpdatesView.as_view(), name="updates"),
    path("get-updates/list/", UpdatesGetView.as_view(), name="updates-list"),
]