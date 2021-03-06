from django.urls import path
from .views import *
app_name = "common"

urlpatterns = [
    path("", index, name="index"),
    # path("donors_list/<int:myid>/", views.donors_list, name="donors_list"),
    # path("donors_details/<int:myid>/", views.donors_details, name="donors_details"),
    path("home", home, name="home"),
    path("request_blood/", request_blood, name="request_blood"),
    path("see_all_request/", see_all_request, name="see_all_request"),
    path("become_donor/", become_donor, name="become_donor"),
    path("about/", about , name="about"),
    path("login_user/", login_user , name="login_user"),
    path("blood_group/", blood_group , name="blood_group"),
    # path("login/", views.Login, name="login"),
    # path("logout/", views.Logout, name="logout"),
    # path('profile/', views.profile, name='profile'),
    # path('edit_profile/', views.edit_profile, name='edit_profile'),
    # path('change_status/', views.change_status, name='change_status'),
    
    #functions
    path("get_request_data", get_request_data , name="get_request_data"),
]

