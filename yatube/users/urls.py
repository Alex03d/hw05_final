from django.contrib.auth.views import \
    LoginView, \
    LogoutView, \
    PasswordResetView
from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    path(
        'password_change_form/',
        LoginView.as_view(template_name='users/password_change_form.html'),
        name='password_change_form'
    ),
    path(
        'password_change_done/',
        LoginView.as_view(template_name='users/password_change_done.html'),
        name='password_change_done'
    ),
    path(
        'password_reset_complete/',
        LoginView.as_view(template_name='users/password_reset_complete.html'),
        name='password_reset_complete'
    ),
    path(
        'password_reset_confirm/',
        LoginView.as_view(template_name='users/password_reset_confirm.html'),
        name='password_reset_confirm'
    ),
    path(
        'password_reset_done/',
        LoginView.as_view(template_name='users/password_reset_done.html'),
        name='password_reset_done'
    ),
    path(
        'password_reset_form/',
        PasswordResetView.as_view(
            template_name='users/password_reset_form.html'
        ),
        name='password_reset_form'
    ),
]
