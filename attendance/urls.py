from django.urls import path
from attendance.views import get_attendance_qr_text, mark_attendance, close_attendance_marking

urlpatterns = [
    path("attendance/qr/", get_attendance_qr_text, name="get_attendance_qr_text"),
    path("attendance/mark/", mark_attendance, name="mark_attendance"),
    path("attendance/close/", close_attendance_marking, name="close_attendance_marking"),
]