from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),  # Changed 'home' to 'index' for consistency
    path('login/', views.user_login, name='login'),
    path('signup/', views.user_signup, name='signup'),
    path('logout/', views.user_logout, name='logout'),
    path('add/', views.add_expense, name='add_expense'),
    path('home/', views.home_expense, name='home_expense'),
    path('export/', views.export_expenses, name='export_expenses'),
    path('add_income/', views.add_income, name='add_income'),  # Add income page
    path('update_budget/', views.update_budget, name='update_budget'),  # Update budget page
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
