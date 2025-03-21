from django.urls import path
from . import views
app_name = "app"
urlpatterns = [
    path('' , views.log_in , name = "login"),
    path('main/' , views.main , name = "main"),
    path('register/', views.register, name="register" ),
    path("login/" , views.log_in , name="login"),
    path("profile/", views.profile , name= "profile"),
    path("bookRide/", views.bookRide, name="bookRide"),
    path("rideDetails/", views.rideDetails, name="rideDetails"),
]