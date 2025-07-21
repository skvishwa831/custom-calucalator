from datetime import datetime
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
from polls.serializers import ContactSerializer
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html")


class CalculateView(View):
    @csrf_exempt
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
                if (
                    ("pm" in s or "am" in s or "AM" in s or "PM" in s)
                    and "]" in s
                    and "[" in s
                    and ":" in s
                ):
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
                    if(data[1]):
                        print('data found', data[1])
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
                    self.saveRecord(
                        last_remembered_datetime,
                        phoneNumber,
                        phoneNumber,
                        right_single_data,
                        left_single_data,
                    )
            data = {"value": sum(left_data)}
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


class record_fetch(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        decoded_str = request.body.decode("utf-8")
        json_obj = json.loads(decoded_str)
        phone = json_obj.get("phone", None)
        contacts = Contact.objects.filter(phone=phone)
        serializer = ContactSerializer(contacts, many=True)
        data = {"data": serializer.data}
        return JsonResponse(data)


class shutDown(View):
    @csrf_exempt
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
