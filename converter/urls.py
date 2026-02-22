from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("convert/", views.convert_file, name="convert"),
    path("download/<str:token>/", views.download_file, name="download"),
]