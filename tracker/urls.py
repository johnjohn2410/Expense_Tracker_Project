from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.home_expense, name='home_expense'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('add_expense/', views.add_expense, name='add_expense'),
    path('delete_expense/<int:expense_id>/', views.delete_expense, name='delete_expense'),
    path('add_income/', views.add_income, name='add_income'),
    path('export_expenses/', views.export_expenses, name='export_expenses'),
    path('update_budget/', views.update_budget, name='update_budget'),
    path('health/', views.health_check, name='health_check'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
