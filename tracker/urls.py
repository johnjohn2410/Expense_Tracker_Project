from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('', views.index, name='index'),
    path('add/', views.add_expense, name='add_expense'),
]
