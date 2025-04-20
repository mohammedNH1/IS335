from django.urls import path
from . import views
#from .views import RideHistoryView, RideDetailView

app_name = "app"
urlpatterns = [
    path('' , views.log_in , name = "login"),
    path('main/' , views.main , name = "main"),
    path('register/', views.register, name="register" ),
    path("login/" , views.log_in , name="login"),
    path("profile/", views.profile , name= "profile"),
    path("bookRide/", views.bookRide, name="bookRide"),
    path("rideDetails/", views.rideDetails, name="rideDetails"),
    path('api/surge-areas/', views.surge_areas_view, name='surge-areas-api'),
    path('searchDriver/', views.searchDriver, name='searchDriver'), 
    path('process_offers/', views.process_offers, name='process_offers'),
    path('ride-details/<uuid:ride_id>/', views.ride_details, name='ride_details'),
    path("ride_history/", views.ride_history, name="ride_history"),
    path("explore/", views.explore, name="explore"),
    path('api/surge-areas-explore/', views.surge_areas_view_explore, name='surge-areas-api-explore'),
    

]