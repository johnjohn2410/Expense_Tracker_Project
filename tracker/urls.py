from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Changed 'home' to 'index' for consistency
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('add/', views.add_expense, name='add_expense'),
]
