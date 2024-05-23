from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from kerberos_profiles.models import Profile
from curriculum.models import Course, CourseClassDates
from datetime import datetime
from Crypto.PublicKey import RSA
from attendance.models import CourseAttendanceKey, Attendance
from Crypto.Cipher import PKCS1_OAEP


def generate_RSA_keypair():
    key = RSA.generate(2048)
    private_key = key.export_key(passphrase="caic_2024")
    public_key = key.publickey().export_key()
    return private_key, public_key


# Create your views here.
@api_view(["GET"])
def get_attendance_qr_text(request):
    print(request.user.is_staff)
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response(
            {"message": "Please login first."}, status=status.HTTP_401_UNAUTHORIZED
        )
    if (
        not request.GET.get("course_code")
        or not request.GET.get("semester_id")
    ):
        return Response(
            {"message": "Please provide all the required fields."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    course_code = request.GET.get("course_code")
    semester_id = request.GET.get("semester_id")
    timestamp = datetime.now()
    day = timestamp.weekday()
    time = timestamp.time()
    professor = Profile.objects.get(kerberosID=request.user.username)
    course = Course.objects.filter(
        courseCode=course_code, courseInstructor=professor, semester=semester_id).first()
    if not Course:
        return Response(
            {"message": "No course found."}, status=status.HTTP_404_NOT_FOUND
        )
    # generate public and private key pair
    private_key, public_key = generate_RSA_keypair()
    # save the public key and private key in the database
    CourseAttendanceKey.objects.create(
        course=course,
        privateKey=private_key.decode(),
        publicKey=public_key.decode(),
    )

    qr_text = f"{public_key.decode()}#{course_code}"

    try:
        CourseClassDates.objects.create(
            course=course,
            classDate=timestamp.date(),
        )
    except:
        print("Class date already exists.")

    return Response(
        {
            "message": "Attendance QR code generated.",
            "qr_text": qr_text,
        }
    )


@api_view(["POST"])
def mark_attendance(request):
    if not request.user.is_authenticated:
        return Response(
            {"message": "Please login first."}, status=status.HTTP_401_UNAUTHORIZED
        )
    data = request.data
    if not data["encrypted_text"] or not data["course_code"] or not data["semester_id"]:
        return Response(
            {"message": "Encrypted text not provided."}, status=status.HTTP_400_BAD_REQUEST
        )

    encrypted_text = data["encrypted_text"]
    course_code = data["course_code"]
    semester_id = data["semester_id"]

    timestamp = datetime.now()
    day = timestamp.weekday()
    time = timestamp.time()
    date = timestamp.date()

    course = Course.objects.filter(
        courseCode=course_code, semester=semester_id).first()

    if not course:
        return Response(
            {"message": "No course found."}, status=status.HTTP_404_NOT_FOUND
        )

    course_attendance_key = CourseAttendanceKey.objects.filter(
        course=course
    ).first()

    if (not course_attendance_key):
        return Response(
            {"message": "Attendance not started."}, status=status.HTTP_400_BAD_REQUEST
        )

    private_key = RSA.import_key(
        course_attendance_key.privateKey, passphrase="caic_2024")

    cipher_rsa = PKCS1_OAEP.new(private_key)
    encrypted_text = bytes.fromhex(encrypted_text)
    decrypted_text = cipher_rsa.decrypt(encrypted_text)
    decrypted_text = decrypted_text.decode()
    decrypted_text = decrypted_text.split("#")

    if len(decrypted_text) != 2:
        return Response(
            {"message": "Invalid QR code."}, status=status.HTTP_400_BAD_REQUEST
        )

    kerberosID = decrypted_text[0]
    deviceUUID = decrypted_text[1]

    if kerberosID != request.user.username:
        return Response(
            {"message": "Invalid QR code."}, status=status.HTTP_400_BAD_REQUEST
        )

    student = Profile.objects.filter(kerberosID=kerberosID).first()

    if not student.deviceUUID:
        return Response(
            {"message": "Device not registered."}, status=status.HTTP_400_BAD_REQUEST
        )

    if student.deviceUUID != deviceUUID:
        return Response(
            {"message": "Wrong device."}, status=status.HTTP_400_BAD_REQUEST
        )

    # check if CourseAttendanceKey is more than 15 secounds old
    if (timestamp - course_attendance_key.timestamp).seconds > 15:
        course_attendance_key.delete()
        # generate public and private key pair
        private_key, public_key = generate_RSA_keypair()
        # save the public key and private key in the database
        CourseAttendanceKey.objects.create(
            course=course,
            privateKey=private_key.decode(),
            publicKey=public_key.decode(),
        )

        return Response(
            {"message": "QR code expired."}, status=status.HTTP_400_BAD_REQUEST
        )

    try:
        Attendance.objects.create(
            student=student,
            course=course,
            date=date,
            time=time,
        )

        return Response(
            {"message": f"Attendance marked for course: {course_code}."}
        )

    except Exception as e:
        return Response(
            {"message": str(e)}, status=status.HTTP_400_BAD_REQUEST
        )


@api_view(["POST"])
def close_attendance_marking(request):
    print(request.user.is_staff)
    if not request.user.is_authenticated or not request.user.is_staff:
        return Response(
            {"message": "Please login first."}, status=status.HTTP_401_UNAUTHORIZED
        )
    data = request.data
    if not data["course_code"] or not data["semester_id"]:
        return Response(
            {"message": "Course code or semester id not provided."}, status=status.HTTP_400_BAD_REQUEST
        )

    course_code = data["course_code"]
    semester_id = data["semester_id"]

    course = Course.objects.filter(
        courseCode=course_code, semester=semester_id).first()

    if not course:
        return Response(
            {"message": "Course not found."}, status=status.HTTP_404_NOT_FOUND
        )

    course_attendance_key = CourseAttendanceKey.objects.filter(
        course=course).first()

    if not course_attendance_key:
        return Response(
            {"message": "Attendance not started."}, status=status.HTTP_400_BAD_REQUEST
        )

    course_attendance_key.delete()

    return Response(
        {"message": "Attendance closed."}
    )
