from django.urls import path
from kerberos_profiles.views import (
    get_profile,
    login,
    get_device_registration_qr_text,
    register_device,
)

urlpatterns = [
    path("profile/", get_profile, name="get_profile"),
    path("login/", login, name="login"),
    path("device/register/", register_device, name="register_device"),
    path("device/qr/", get_device_registration_qr_text, name="get_device_registration_qr_text"),
]