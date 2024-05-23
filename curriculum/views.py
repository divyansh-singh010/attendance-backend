from django.shortcuts import render
from curriculum.models import Course, Semester, CourseClassDates
from attendance.models import Attendance
from kerberos_profiles.models import Profile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime


# Create your views here.
@api_view(["POST"])
def add_course(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response(
            {"message": "Please login first."}, status=status.HTTP_401_UNAUTHORIZED
        )

    if (
        not request.data.get("course_code")
        or not request.data.get("course_name")
        or not request.data.get("semester_id")
        or not request.data.get("number_of_classes")
    ):
        return Response(
            {"message": "Please provide all the required fields."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    course_code = request.data.get("course_code")
    course_name = request.data.get("course_name")
    semester_id = request.data.get("semester_id")
    number_of_classes = request.data.get("number_of_classes")
    semester = Semester.objects.get(id=semester_id)
    course_instructor = Profile.objects.get(kerberosID=course_instructor)
    course = Course.objects.create(
        courseCode=course_code,
        courseName=course_name,
        semester=semester,
        courseInstructor=course_instructor,
        numberOfClasses=number_of_classes,
    )
    course.save()
    return Response(
        {"message": "Course added successfully.", "course_code": course_code}
    )


@api_view(["GET"])
def get_courses_this_semester(request):
    if not request.user.is_authenticated:
        return Response(
            {"message": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED
        )
    semester_id = request.GET.get("semester_id")
    semester = Semester.objects.filter(id=semester_id).first()
    instructor = Profile.objects.get(kerberosID=request.user.username)
    courses = Course.objects.filter(
        courseInstructor=instructor, semester=semester)
    courses_data = []
    for course in courses:
        courses_data.append(
            {
                "course_code": course.courseCode,
                "course_name": course.courseName,
                "number_of_classes": course.numberOfClasses,
            }
        )

    return Response({"courses": courses_data, "semester_id": semester.id})


@api_view(["GET"])
def get_current_semester(request):
    if not request.user.is_authenticated:
        return Response(
            {"message": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED
        )
    semester = Semester.objects.filter(
        startDate__lte=datetime.now(), endDate__gte=datetime.now()
    ).first()
    return Response(
        {
            "semester_id": semester.id,
            "academic_year": semester.academicYear,
            "semester_number": semester.semesterNumber,
        }
    )


@api_view(["GET"])
def get_semesters(request):
    if not request.user.is_authenticated:
        return Response(
            {"message": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED
        )
    semesters = Semester.objects.all()
    semesters_data = []
    for semester in semesters:
        semesters_data.append(
            {
                "semester_id": semester.id,
                "academic_year": semester.academicYear,
                "semester_number": semester.semesterNumber,
            }
        )
    return Response({"semesters": semesters_data})


@api_view(["GET"])
def get_courses_for_given_semester(request):
    if not request.user.is_authenticated:
        return Response(
            {"message": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED
        )
    if not request.GET.get("semester_id"):
        return Response(
            {"message": "Semester ID not provided."}, status=status.HTTP_400_BAD_REQUEST
        )
    semester_id = request.GET.get("semester_id")
    semester = Semester.objects.get(id=semester_id)
    instructor = Profile.objects.get(kerberosID=request.user.username)
    courses = Course.objects.filter(
        courseInstructor=instructor, semester=semester)
    courses_data = []
    for course in courses:
        courses_data.append(
            {
                "course_code": course.courseCode,
                "course_name": course.courseName,
                "number_of_classes": course.numberOfClasses,
            }
        )
    return Response({"courses": courses_data, "semester_id": semester_id})


@api_view(["POST"])
def get_courses_for_student(request):
    if not request.user.is_authenticated:
        return Response(
            {"message": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED
        )
    semester_id = request.data.get("semester_id")

    semester = Semester.objects.filter(id=semester_id).first()
    if not semester:
        return Response(
            {"message": "No active semester."}, status=status.HTTP_404_NOT_FOUND
        )
    student = Profile.objects.get(kerberosID=request.user.username)
    courses_registered = Attendance.objects.filter(
        student=student, course__semester=semester).values('course').distinct()
    courses_data = []
    for course in courses_registered:
        courses_data.append(
            {
                "course_code": course.courseCode,
                "course_name": course.courseName,
                "number_of_classes": course.numberOfClasses,
            }
        )

    return Response({"courses": courses_data})


@api_view(["GET"])
def get_course_attendance_for_student(request):
    if not request.user.is_authenticated:
        return Response(
            {"message": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED
        )
    if not request.GET.get("course_code") or not request.GET.get("semester_id"):
        return Response(
            {"message": "Course code or semester ID not provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    course_code = request.GET.get("course_code")
    semester_id = request.GET.get("semester_id")
    semester = Semester.objects.filter(
        id=semester_id
    ).first()
    course = Course.objects.get(courseCode=course_code)
    student = Profile.objects.get(kerberosID=request.user.username)
    attendances = Attendance.objects.filter(course=course, student=student)
    attendance_data = []
    total_classes = course.numberOfClasses
    present_count = 0
    for attendance in attendances:
        present_count += 1
        attendance_data.append(
            {
                "date": attendance.date,
                "time": attendance.time,
            }
        )
    return Response(
        {
            "attendance": attendance_data,
            "total_classes": total_classes,
            "present_count": present_count,
        }
    )
