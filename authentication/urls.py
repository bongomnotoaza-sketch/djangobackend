from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('login-page/', views.login_page, name='login_page'),  # Make sure this URL is correct
    path('get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),  # Add this
    path('register/', views.register, name='register'),
    path('verify-email/', views.verify_email, name='verify_email'),
    path("current-user/", views.current_user, name="current_user"),
    path('password_reset_page/', views.password_reset_page, name='password_reset_page'),
    path('password-recovery/', views.password_recovery, name='password_recovery'),
    path('password-reset/', views.password_reset, name='password_reset'),
    path('update-info/', views.update_info, name='update_info'),
    path('logout/', views.logout, name='logout'),
]