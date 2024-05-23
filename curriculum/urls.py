from django.urls import path
from curriculum.views import add_course, get_courses_this_semester, get_current_semester, get_courses_for_student, get_course_attendance_for_student, get_courses_for_given_semester, get_semesters

urlpatterns = [
    path("course/add/", add_course, name="add_course"),
    path("courses/this_semester/", get_courses_this_semester, name="get_courses_this_semester"),
    path("semesters/", get_semesters, name="get_semesters"),
    path("semester/current/", get_current_semester, name="get_current_semester"),
    path("courses/student/", get_courses_for_student, name="get_courses_for_student"),
    path("courses/attendance/student/", get_course_attendance_for_student, name="get_course_attendance_for_student"),
    path("courses/semester/", get_courses_for_given_semester, name="get_courses_for_given_semester"),
]