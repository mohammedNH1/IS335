from django.urls import path
from . import views
app_name = "app"
urlpatterns = [
    path('' , views.main , name = "main"),
    path('register/', views.register, name="register" ),
]