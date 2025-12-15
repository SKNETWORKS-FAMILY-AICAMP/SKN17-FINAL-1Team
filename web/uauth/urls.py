from django.urls import path
from uauth import views

app_name = 'uauth'

urlpatterns = [
    path('find-password/', views.find_password, name='find_password'),
    path('send-verification-code/', views.send_verification_code, name='send_verification_code'),
    path('send-password-reset-code/', views.send_password_reset_code, name='send_password_reset_code'),
    path('verify-code/', views.verify_code, name='verify_code'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('change-password/', views.change_password, name='change_password'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup, name='signup'),
    path('signup/form/', views.signup_form, name='signup_form'),
    path('signup-api/', views.signup_view, name='signup_api'),
    path('check/', views.check_login_status, name='check_login'),
    path('withdraw/', views.withdraw, name='withdraw'),
    path("profile/edit/", views.update_profile, name="update_profile"),
]
