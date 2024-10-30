from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', views.home, name='home'),
    path('login/', views.login, name='login'),
    path('search/', views.search, name='search'),
    path('profile/', views.profile, name='profile'),
    path('toggle_favorite/', views.toggle_favorite, name='toggle_favorite'),
    path('write_review/', views.write_review, name='write_review'),
    path('toggle_fav_profile/', views.toggle_fav_profile, name='toggle_fav_profile'),
    path('review/', views.review, name='review'),
    path('delete_review/', views.delete_review, name='delete_review'),
    path('password_reset/', views.password_reset, name='password_reset'),
    path('reset_confirm/<uidb64>/<token>', views.password_reset, name='reset_confirm'),
    path('reset-confirm/<uidb64>/<token>/', views.password_reset_confirm, name='password_reset_confirm'),
]
