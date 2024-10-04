from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Route for the home page
    path('add/', views.add_expense, name='add_expense'),  # Route for adding expenses
]
