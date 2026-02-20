from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('apply/', views.apply_attachment, name='apply'),
    path('logbook/<int:attachment_id>/', views.logbook, name='logbook'),
    path('evaluate/<int:attachment_id>/', views.evaluate, name='evaluate'),
]
