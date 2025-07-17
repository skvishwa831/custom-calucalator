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

import logging

logger = logging.getLogger(__name__)


def index(request):
    return render(request, "index.html")


class CalculateView(View):
    @csrf_exempt
    def post(self, request, *args, **kwargs):
        decoded_str = request.body.decode("utf-8")
        json_obj = json.loads(decoded_str)
        message = json_obj.get("message", "")
        save = json_obj.get("save", False)
        phoneNumber = json_obj.get("phoneNumber", 0000000000)
        test_strings = message.splitlines()
        right_data = []
        left_data = []
        for s in test_strings:
            n1, n2 = self.read_two_number_groups(s)
            if n1 is not None and n2 is not None:
                right_data.append(n1)
                left_data.append(n2)
        if save:
            for i in range(len(right_data)):
                self.saveRecord(phoneNumber, phoneNumber, right_data[i], left_data[i])
        data = {"value": sum(left_data)}
        logger.info(f"\n{'-'*50}\nrequest:{json_obj}\nresponse:{data}\nSaved:{save}\n{'-'*50}")
        return JsonResponse(data)

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

    def saveRecord(self, name="", phone="", matka_number=000, amount=000):
        new_contact = Contact(
            name=name,
            phone=phone,
            matka_number=matka_number,
            amount=amount,
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
