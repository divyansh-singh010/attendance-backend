from django.shortcuts import render
from rest_framework_simplejwt.tokens import RefreshToken
import secrets
from dotenv import load_dotenv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import requests
from .models import Profile
from django.contrib.auth.models import User
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import os
from django.views.decorators.csrf import csrf_exempt

load_dotenv()

# Create your views here.
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {"refresh": str(refresh), "access": str(refresh.access_token)}


def generateRandom256BitPassword():
    # 256 bit hex string
    return secrets.token_hex(32)

@api_view(["POST"])
def login(request):
    data = request.data
    if not data["code"]:
        return Response(
            {"message": "Please provide a code."}, status=status.HTTP_400_BAD_REQUEST
        )
    code = data["code"]
    client_id = os.getenv("OAUTH_CLIENT_ID")
    client_secret = os.getenv("OAUTH_CLIENT_SECRET")
    request_data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    request_url = "https://oauth.iitd.ac.in/token.php"
    response = requests.post(request_url, request_data)
    if response.status_code != 200:
        return Response(
            {"message": "Invalid code provided.", "error": str(response)},
            status=status.HTTP_400_BAD_REQUEST,
        )
    response_data = response.json()
    access_token = response_data["access_token"]
    request_url = "https://oauth.iitd.ac.in/resource.php"
    response = requests.post(request_url, data={"access_token": access_token})
    if response.status_code != 200:
        return Response(
            {"message": "Invalid access token provided."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    response_data = response.json()
    user_id = response_data["user_id"]
    name = response_data["name"]
    mail = response_data["mail"]
    uniqueiitdid = response_data["uniqueiitdid"]
    category = response_data["category"]
    department = response_data["department"]

    # Check if user exists in database
    user = User.objects.filter(username=user_id).first()
    if not user:
        user = User.objects.create_user(
            username=user_id,
            password=generateRandom256BitPassword(),
            email=mail,
            first_name=name,
        )
        if category == "faculty":
            user.is_staff = True
        user.save()
        Profile.objects.create(
            kerberosID=user_id,
            name=name,
            email=mail,
            uniqueiitdid=uniqueiitdid,
            category=category,
            department=department,
        )
    tokens = get_tokens_for_user(user)
    return Response(
        {
            "message": "Login successful.",
            "tokens": tokens,
            "user": {
                "username": user_id,
                "name": name,
                "email": mail,
                "uniqueiitdid": uniqueiitdid,
                "category": category,
                "department": department,
            },
        }
    )


@api_view(["GET"])
def get_profile(request):
    if not request.user.is_authenticated:
        return Response(
            {"message": "User not authenticated."}, status=status.HTTP_401_UNAUTHORIZED
        )
    user = request.user
    profile = Profile.objects.filter(kerberosID=user.username).first()
    if not profile:
        return Response(
            {"message": "Profile not found."}, status=status.HTTP_404_NOT_FOUND
        )
    return Response(
        {
            "message": "Profile found.",
            "profile": {
                "kerberosID": profile.kerberosID,
                "name": profile.name,
                "email": profile.email,
                "uniqueiitdid": profile.uniqueiitdid,
                "category": profile.category,
                "department": profile.department,
            },
        }
    )


# Create your views here.
@api_view(["GET"])
def get_device_registration_qr_text(request):
    if not request.user.is_authenticated:
        return Response(
            {"message": "Please login first."}, status=status.HTTP_401_UNAUTHORIZED
        )
    profile = Profile.objects.get(kerberosID=request.user.username)
    qr_text = profile.kerberosID + "#" + profile.name
    public_key = RSA.import_key(open("public_key.pem").read())
    cipher_rsa = PKCS1_OAEP.new(public_key)
    qr_text = cipher_rsa.encrypt(qr_text.encode())
    qr_text = qr_text.hex()
    if profile.deviceUUID:
        return Response(
            {"qr_text": qr_text, "status": "One Device is already registered"},
            status=status.HTTP_200_OK,
        )
    return Response({"qr_text": qr_text}, status=status.HTTP_200_OK)


@api_view(["POST"])
def register_device(request):
    data = request.data
    if not data["qr_text"] or not data["udid"]:
        return Response(
            {"message": "Please provide a QR text."}, status=status.HTTP_400_BAD_REQUEST
        )
    private_key = RSA.import_key(
        open("private_key.pem").read(), passphrase="caic_2024"
    )
    cipher_rsa = PKCS1_OAEP.new(private_key)
    qr_text = data["qr_text"]
    deviceUUID = data["udid"]
    
    try:
        qr_text = bytes.fromhex(qr_text)
        qr_text = cipher_rsa.decrypt(qr_text)
        qr_text = qr_text.decode()
        qr_text = qr_text.split("#")
        if len(qr_text) != 3:
            return Response(
                {"message": "Invalid QR text."}, status=status.HTTP_400_BAD_REQUEST
            )    
    except Exception as e:
        return Response(
            {"message": "Invalid QR text."}, status=status.HTTP_400_BAD_REQUEST
        )
    kerberosID = qr_text[0]
    entryNumber = qr_text[1]
    name = qr_text[2]
    if not User.objects.filter(username=kerberosID).exists():
        return Response(
            {"message": "Please scan qr at device registration portal"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    student = Profile.objects.get(kerberosID=kerberosID)
    user = User.objects.get(username=kerberosID)
    if not student.deviceUUID:
        student.deviceUUID = deviceUUID
        student.save()
    if student.deviceUUID != deviceUUID:
        return Response(
            {"message": "One Device is already Registered"},
            status=status.HTTP_400_BAD_REQUEST,
        )
    tokens = get_tokens_for_user(user)
    return Response(
        {
            "tokens": tokens,
            "student": {
                "kerberosID": student.kerberosID,
                "entryNumber": student.uniqueiitdid,
                "name": student.name,
                "department": student.department,
                "mail": student.email,
            },
        },
        status=status.HTTP_200_OK,
    )

