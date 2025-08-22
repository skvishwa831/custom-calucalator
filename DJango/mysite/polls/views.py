from datetime import datetime, timedelta, time
import os
import re
from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView, View
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
import json
from polls.models import Contact
from polls.serializers import (
    ContactSerializer,
    CustomerNamesSerializer,
    GameDashBoardSerializer,
    GameRecordsSerializer,
    GameWinningNumbersRecordSerializer,
    GamesTypesSerializer,
)
from django.utils import timezone
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import CustomerNames, GameDashBoard, GameRecords, GameWinningNumbersRecord, GamesTypes, User
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView
from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import (
    OutstandingToken,
    BlacklistedToken,
)
from polls.authentication import CustomJWTAuthentication
from datetime import date
import logging

logger = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html")


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)

        # Save the JTI of the new token
        self.user.current_token_jti = str(refresh["jti"])
        self.user.save(update_fields=["current_token_jti"])

        data["refresh"] = str(refresh)
        data["access"] = str(refresh.access_token)
        return data


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class CustomerNamesListView(APIView):

    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            customer_names = CustomerNames.objects.all()
            serializer = CustomerNamesSerializer(customer_names, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching customer names: {e}")
            return Response({"error": "Failed to fetch customer names"}, status=500)


class CustomLoginView(APIView):
    authentication_classes = []  # Disable auth for this endpoint
    permission_classes = []  # Allow anyone to access

    def post(self, request):
        try:
            decoded_str = request.body.decode("utf-8")
            json_obj = json.loads(decoded_str)
            username = json_obj.get("username")
            password = json_obj.get("password")

            user = authenticate(email=username, password=password)

            if user is None or not user.is_active:
                return Response(
                    {"error": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )

            # Blacklist all previous refresh tokens
            for token in OutstandingToken.objects.filter(user=user):
                try:
                    BlacklistedToken.objects.get_or_create(token=token)
                except Exception:
                    pass

            # Create new tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token

            # ✅ Store the new access token's jti
            user.current_token_jti = access["jti"]
            user.save()

            return Response(
                {
                    "access": str(access),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error in login view: {e}")
            return Response({"error": "Failed to login"}, status=500)


class GamesTypesListView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            games = GamesTypes.objects.all()
            serializer = GamesTypesSerializer(games, many=True)
            return Response(serializer.data)
        except Exception as e:
            logger.error(f"Error fetching game types: {e}")
            return Response({"error": "Failed to fetch game types"}, status=500)


User = get_user_model()


def register(request):
    try:
        if request.method == "POST":
            decoded_str = request.body.decode("utf-8")
            json_obj = json.loads(decoded_str)
            email = json_obj.get("email")
            name = json_obj.get("name")
            password = json_obj.get("password")
            confirm_password = json_obj.get("confirm_password")
            secret_key = json_obj.get("scrate_kay")

            if not secret_key:
                return JsonResponse({"error": "Secret key is required."}, status=401)

            if secret_key != "v9$TgL#2pQ@zX8!rWm7^bKfE1&uYdC6*oJ":
                return JsonResponse({"error": "Invalid secret key."}, status=401)

            if not email or not name or not password:
                messages.error(request, "All fields are required.")
                return JsonResponse({"error": "All fields are required."}, status=400)

            if password != confirm_password:
                messages.error(request, "Passwords do not match.")
                return JsonResponse({"error": "Passwords do not match."}, status=400)

            if User.objects.filter(email=email).exists():
                messages.error(request, "Email already registered.")
                return JsonResponse({"error": "Email already registered."}, status=400)

            user = User(email=email, name=name)
            user.set_password(password)  # 🔐 hashes the password
            user.save()
            return JsonResponse(
                {"message": "User registered successfully."}, status=201
            )
        else:
            messages.error(request, "Invalid request method.")
            return JsonResponse({"error": "Invalid request method."}, status=400)
    except Exception as e:
        logger.error(f"Error in register view: {e}")
        return JsonResponse({"error": str(e)}, status=500)


class CalculateView(APIView):  # ✅ Use APIView
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            decoded_str = request.body.decode("utf-8")
            json_obj = json.loads(decoded_str)
            message = json_obj.get("message", "")
            save = json_obj.get("save", False)
            phoneNumber = json_obj.get("phoneNumber", 0000000000)
            test_strings = message.splitlines()
            right_data = []
            left_data = []
            last_remembered_amount = 0
            last_remembered_datetime = timezone.now()
            last_remembered_name = "unknown"
            for s in test_strings:
                if self.isNamingAndTimeTagged(s):
                    list_data = s.split("]")
                    last_remembered_name = list_data[1].split(":")[0].strip()
                    data = list_data[1].split(":")
                    list_data = s.split("[")
                    list_data = list_data[1].split(",")
                    time = list_data[1].split("]")[0].strip()
                    day_month = list_data[0]
                    combined = f"{day_month} {time}"
                    last_remembered_datetime = datetime.strptime(
                        combined, "%d/%m %I:%M %p"
                    ).replace(year=2025)
                    if data[1]:
                        s = data[1]
                    else:
                        continue

                l = self.extract_ints(s)
                right_single_data = 0
                left_single_data = 0

                if len(l) > 1:
                    last_remembered_amount = l[-1]
                    for i in l[:-1]:
                        right_data.append(i)
                        right_single_data = i
                        left_data.append(l[-1])
                        left_single_data = l[-1]

                if len(l) == 1:
                    right_single_data = l[0]
                    right_data.append(l[0])
                    left_data.append(last_remembered_amount)
                    left_single_data = last_remembered_amount

                if last_remembered_name != "unknown":
                    phoneNumber = last_remembered_name

                if save or last_remembered_name != "unknown":
                    if right_single_data != 0 and left_single_data != 0:
                        self.saveRecord(
                            last_remembered_datetime,
                            phoneNumber,
                            phoneNumber,
                            right_single_data,
                            left_single_data,
                        )

            data = {"value": sum(left_data), "name": last_remembered_name}
            logger.info(
                f"\n{'-'*50}\nrequest:{json_obj}\nresponse:{data}\nSaved:{save}\n{'-'*50}"
            )
            return JsonResponse(data)
        except Exception as e:
            logger.error(f"Error in CalculateView: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    def extract_ints(self, s: str) -> list[int]:
        nums = []
        current = ""
        for ch in s:
            if ch.isdigit():
                current += ch
            elif current:
                nums.append(int(current))
                current = ""
        if current:
            nums.append(int(current))
        return nums

    def read_two_number_groups(self, input_string):
        pattern = r"(\d+)\D*(\d+)"
        match = re.search(pattern, input_string)

        if match:
            num1 = match.group(1)
            num2 = match.group(2)
            return int(num1), int(num2)  # Convert to integers
        else:
            return (
                None,
                None,
            )  # Or raise an error, or return empty list, depending on desired behavior

    def saveRecord(
        self, last_remembered_datetime, name="", phone="", matka_number=000, amount=000
    ):
        new_contact = Contact(
            name=name,
            phone=phone,
            matka_number=matka_number,
            amount=amount,
            created_at=last_remembered_datetime,  # Assuming you want to set this later or it will be auto-set
        )
        # Save it to the database
        new_contact.save()

    def isNamingAndTimeTagged(self, s: str) -> bool:
        return (
            ("pm" in s or "am" in s or "AM" in s or "PM" in s)
            and "]" in s
            and "[" in s
            and ":" in s
        )


class SaveRecords(APIView):  # ✅ Use APIView
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            decoded_str = request.body.decode("utf-8")
            json_obj = json.loads(decoded_str)
            message = json_obj.get("message", "")
            name = json_obj.get("name", "")
            game_name = json_obj.get("gameName", "")
            test_strings = message.splitlines()
            right_data = []
            left_data = []
            last_remembered_amount = 0
            last_remembered_datetime = timezone.now()
            last_remembered_name = "unknown"
            for s in test_strings:
                if self.isNamingAndTimeTagged(s):
                    list_data = s.split("]")
                    last_remembered_name = list_data[1].split(":")[0].strip()
                    data = list_data[1].split(":")
                    list_data = s.split("[")
                    list_data = list_data[1].split(",")
                    time_local = list_data[1].split("]")[0].strip()
                    day_month = list_data[0]
                    combined = f"{day_month} {time_local}"
                    last_remembered_datetime = datetime.strptime(
                        combined, "%d/%m %I:%M %p"
                    ).replace(year=2025)
                    if data[1]:
                        s = data[1]
                    else:
                        continue
                l = self.extract_ints(s)
                right_single_data = 0
                left_single_data = 0

                if len(l) > 1:
                    last_remembered_amount = l[-1]
                    for i in l[:-1]:
                        right_data.append(i)
                        right_single_data = i
                        left_data.append(l[-1])
                        left_single_data = l[-1]

                if len(l) == 1:
                    right_single_data = l[0]
                    right_data.append(l[0])
                    left_data.append(last_remembered_amount)
                    left_single_data = last_remembered_amount

                if last_remembered_name != "unknown":
                    phoneNumber = last_remembered_name
            # ------------------------
            now = datetime.now()
            cutoff_time = time(5, 0)  # This is the correct usage of the 'time' class
            if now.time() < cutoff_time:
                adjusted_date = (now - timedelta(days=1)).date()
            else:
                adjusted_date = now.date()
            # ----------------------------
            gameRecordSerializer = GameRecordsSerializer(
                data={
                    "name": name,
                    "gameName": game_name,
                    "content": json.dumps(
                        {"matka_number": right_data, "amount": left_data}
                    ),
                    "date": adjusted_date
                }
            )
            if gameRecordSerializer.is_valid(raise_exception=True):
                gameRecordSerializer.save()

            found_user = GameDashBoard.objects.filter(
                name=name, date=adjusted_date
            ).first()
            if found_user:
                found_user.totalAmount += sum([int(i) for i in left_data])
                found_user.save()
            else:
                GameDashBoard.objects.create(
                    name=name,
                    totalAmount=sum([int(i) for i in left_data]),
                    date=adjusted_date,
                )
            data = {
                "value": sum([int(i) for i in left_data]),
                "name": last_remembered_name,
            }
            logger.info(f"\n{'-'*50}\nrequest:{json_obj}\nresponse:{data}\n{'-'*50}")
            return JsonResponse(data)
        except Exception as e:
            logger.error(f"Error in CalculateView: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    def extract_ints(self, s: str) -> list[int]:
        nums = []
        current = ""
        for ch in s:
            if ch.isdigit():
                current += ch
            elif current:
                nums.append(current)
                current = ""
        if current:
            nums.append(current)
        return nums

    def read_two_number_groups(self, input_string):
        pattern = r"(\d+)\D*(\d+)"
        match = re.search(pattern, input_string)

        if match:
            num1 = match.group(1)
            num2 = match.group(2)
            return int(num1), int(num2)  # Convert to integers
        else:
            return (
                None,
                None,
            )  # Or raise an error, or return empty list, depending on desired behavior

    def saveRecord(
        self, last_remembered_datetime, name="", phone="", matka_number=000, amount=000
    ):
        new_contact = Contact(
            name=name,
            phone=phone,
            matka_number=matka_number,
            amount=amount,
            created_at=last_remembered_datetime,  # Assuming you want to set this later or it will be auto-set
        )
        # Save it to the database
        new_contact.save()

    def isNamingAndTimeTagged(self, s: str) -> bool:
        return (
            ("pm" in s or "am" in s or "AM" in s or "PM" in s)
            and "]" in s
            and "[" in s
            and ":" in s
        )

class GameWinnnigNumbers(View):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        try:
            adjusted_date = self.getDate()
            model_data = GameWinningNumbersRecord.objects.filter(date=adjusted_date).all()
            serializer = GameWinningNumbersRecordSerializer(model_data, many=True)
            if(len(serializer.data) == 0):
                schema_data = {
                "Sridevi Open": ["0", "0", "0"],
                "Sridevi Close": ["0", "0"],
                "Time Bazar Open": ["0", "0", "0"],
                "Time Bazar Close": ["0", "0"],
                "Milan Day Open": ["0", "0", "0"],
                "Milan Day Close": ["0", "0"],
                "Rajadani Day Open": ["0", "0", "0"],
                "Rajadani Day Close": ["0", "0"],
                "Kalyan Open": ["0", "0", "0"],
                "Kalyan Close": ["0", "0"],
                "Sridevi Night Open": ["0", "0", "0"],
                "Sridevi Night Close": ["0", "0"],
                "Milan Night Open": ["0", "0", "0"],
                "Milan Night Close": ["0", "0"],
                "Rajadani Night Open": ["0", "0", "0"],
                "Rajadani Night Close": ["0", "0"],
                "Kalyan Night Open": ["0", "0", "0"],
                "Kalyan Night Close": ["0", "0"],
                "Main Bazar Open": ["0", "0", "0"],
                "Main Bazar Close": ["0", "0"],
            }
                return JsonResponse(schema_data, safe=False)
            records = json.loads(serializer.data[0].get("records", "{}"))
            return JsonResponse(records, safe=False)
        except Exception as e:
            logger.error(f"Error in GameWinningNumbers: {e}")
            return JsonResponse({"error": str(e)}, status=500)
        
    def post(self, request, *args, **kwargs):
        try:
            # Handle POST request data here
            decoded_str = request.body.decode("utf-8")
            request_data = json.loads(decoded_str)
            adjusted_date = self.getDate()
            try:
                found_record = GameWinningNumbersRecord.objects.filter(date=adjusted_date).first()
                found_record.records = json.dumps(request_data)
                found_record.save()
            except Exception as e:
                is_valid_data = GameWinningNumbersRecordSerializer(data={
                    "date": self.getDate(),
                    "records": json.dumps(request_data)
                })
                if is_valid_data.is_valid(raise_exception=True):
                    is_valid_data.save()
            # Process the data and save it
            return JsonResponse({"message": "Data saved successfully"}, status=201)
    
        except Exception as e:
            logger.error(f"Error in GameWinningNumbers: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    def getDate(self):
        now = datetime.now()
        cutoff_time = time(5, 0)  # This is the correct usage of the 'time' class
        if now.time() < cutoff_time:
            adjusted_date = (now - timedelta(days=1)).date()
        else:
            adjusted_date = now.date()
        return adjusted_date
class GameDashBoardView(View):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            games = {}
            adjusted_date = self.getDate()
            try:
                found_record = GameWinningNumbersRecord.objects.filter(date=adjusted_date).first()
                games = json.loads(found_record.records) if found_record else {}
            except Exception as e:
                logger.error(f"Error in GameDashBoardView: {e}")
            unique_vals = GameDashBoard.objects.filter(date=adjusted_date).order_by()
            jsonData = GameDashBoardSerializer(unique_vals, many=True).data
            final_data = []
            for item in jsonData:
                user_name = item.get("name", "")
                final_ob = {
                    "id": item.get("id", ""),
                    "name": user_name,
                    "totalAmount": item.get("totalAmount", 0),
                    "date": item.get("date", ""),
                    "win": [],
                    "winAmount": 0,
                }
                if user_name:
                    all_data = GameRecordsSerializer(
                        GameRecords.objects.filter(name=user_name, date=adjusted_date).all(), many=True
                    ).data
                    for matka in all_data:
                        if games.get(matka.get("gameName", "")):
                            content = json.loads(matka.get("content", {}))
                            for index, matk_number in enumerate(content.get("matka_number", [])):
                                if matk_number in games.get(matka.get("gameName", "")):
                                    win_amount = content.get("amount", [])[index]
                                    grant_win_amount = self.get_win_amount(
                                        win_amount, matk_number
                                    )
                                    final_ob["winAmount"] += grant_win_amount
                                    final_ob["win"].append(
                                        {
                                            "matk_number": matk_number,
                                            "gameName": matka.get("gameName", ""),
                                            "amount": f"R: {win_amount}, w: {grant_win_amount}",
                                        }
                                    )
                final_data.append(final_ob)
            return JsonResponse(final_data, safe=False)
        except Exception as e:
            logger.error(f"Error in GameDashBoardView: {e}")
            return JsonResponse({"error": str(e)}, status=500)

    def get_win_amount(self, amount, matka):
        matka_str = str(matka)
        amount = int(amount)

        # Ensure matka_number is not more than 3 digits
        if len(matka_str) > 3:
            raise ValueError("matka_number must not exceed 3 digits")

        # Condition 1: Single digit
        if len(matka_str) == 1:
            return amount * 9

        # Condition 2: Two digits
        if len(matka_str) == 2:
            if matka_str[0] == matka_str[1]:  # Condition 4: Both digits same
                return amount * 250
            return amount * 90  # Condition 2

        # Condition 3: Three digits
        if len(matka_str) == 3:
            digits = list(matka_str)
            unique_digits = set(digits)

            if len(unique_digits) == 1:  # Condition 6: All digits same
                return amount * 500
            elif len(unique_digits) == 2:  # Condition 5: Two digits same
                return amount * 250
            else:
                return amount * 125  # Condition 3

        # Fallback (shouldn't be reached)
        return amount

    def getDate(self):
        now = datetime.now()
        cutoff_time = time(5, 0)  # This is the correct usage of the 'time' class
        if now.time() < cutoff_time:
            adjusted_date = (now - timedelta(days=1)).date()
        else:
            adjusted_date = now.date()
        return adjusted_date


class record_fetch(View):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        decoded_str = request.body.decode("utf-8")
        json_obj = json.loads(decoded_str)
        phone = json_obj.get("phone", None)
        contacts = Contact.objects.filter(phone=phone)
        serializer = ContactSerializer(contacts, many=True)
        data = {"data": serializer.data}
        return JsonResponse(data)


class fetch_saved_Names(View):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            unique_vals = (
                Contact.objects.order_by().values_list("name", flat=True).distinct()
            )
            data = {"data": list(unique_vals)}
            return JsonResponse(data)
        except Exception as e:
            logger.error(f"Error in fetch_saved_Names: {e}")
            return JsonResponse({"error": str(e)}, status=500)


class delete_records(View):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            decoded_str = request.body.decode("utf-8")
            json_obj = json.loads(decoded_str)
            name = json_obj.get("name", None)
            pwd = json_obj.get("pwd", None)
            if name:
                if name == "all":
                    if pwd != "delete":
                        return JsonResponse({"error": "Invalid password"}, status=403)
                    Contact.objects.all().delete()
                    data = {"value": "success"}
                    return JsonResponse(data)
                # Delete the contact with the given name
                Contact.objects.filter(name=name).delete()
                data = {"value": "success"}
                return JsonResponse(data)
            else:
                return JsonResponse({"error": "Name not provided"}, status=400)
        except Exception as e:
            logger.error(f"Error in delete: {e}")
            return JsonResponse({"error": str(e)}, status=500)


class shutDown(View):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        self.shutdown_pc(5)
        data = {"value": "success"}
        return JsonResponse(data)

    def shutdown_pc(self, delay_seconds=0):
        if os.name == "nt":  # For Windows operating systems
            os.system(f"shutdown /s /t {delay_seconds}")
        elif os.name == "posix":  # For Linux/macOS operating systems
            os.system(f"sudo shutdown -h +{delay_seconds // 60}")
        else:
            print("Unsupported operating system for direct shutdown command.")
