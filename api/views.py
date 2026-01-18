from django.shortcuts import render
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.urls import reverse
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse
from django.utils.timezone import now
from rest_framework import generics, views, status
from .serializers import UserSerializer, MyTokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from openai import OpenAI
from .ical_utils import ics_from_data_uri, looks_like_ics, normalize_crlf
from django.views.decorators.csrf import csrf_exempt
from .models import Subscription
from django.http import FileResponse, Http404
import os
import json
import uuid
import urllib.request
import datetime

# Create your views here.

User = get_user_model()
client = OpenAI()

class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

#Use custom serializer to get user id when the user logs in
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class GetUpdateUserView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

class getEventLink(views.APIView):
    permission_classes = [IsAuthenticated]
    MAX_ICS_SIZE = 200_000

    def post(self, request):
        current_user = User.objects.get(email=request.user)
        # subscription = Subscription.objects.filter(user=current_user).first()
        tokens = current_user.tokens

        if current_user.bypass_token_limit or tokens > 0:
            event_details = request.data['event_details']
            prompt = os.environ['FINAL_LINK_CREATION_PROMPT']

            for platform in request.data['platforms']:
                prompt = prompt + " " + platform
            openai_response = client.responses.create(
                model="gpt-4o-mini",
                instructions=prompt,
                input=event_details
            )

            openai_response_decoded = json.loads(openai_response.output_text)
            ical_check = openai_response_decoded.get('links', {}).get('icalendar')
            ical_dataurl = ical_check if ical_check is not None else False

            if isinstance(ical_dataurl, str) and ical_dataurl.lower().startswith("data:text/calendar"):
                try:
                    ics_text = ics_from_data_uri(ical_dataurl)
                except Exception:
                    return Response({"detail": "invalid icalendar data url"}, status=status.HTTP_400_BAD_REQUEST)

                if not looks_like_ics(ics_text) or len(ics_text.encode("utf-8")) > self.MAX_ICS_SIZE:
                    return Response({"detail": "invalid or too large ics payload"}, status=status.HTTP_400_BAD_REQUEST)

                filename = f"ical/{slugify('event')}-{uuid.uuid4().hex}.ics"
                path_key = default_storage.save(filename, ContentFile(ics_text))
                download_path = reverse("download-ics", kwargs={"key": path_key})
                download_url = request.build_absolute_uri(download_path)

                openai_response_decoded['links']['icalendar'] = download_url
            
            if not current_user.bypass_token_limit:
               current_user.tokens = tokens - 1
               current_user.save()
            return Response(json.dumps(openai_response_decoded), status=status.HTTP_200_OK)
        else:
            return Response(json.dumps({"msg": "No free tokens remaining"}), status=status.HTTP_400_BAD_REQUEST)
        
class DownloadIcsView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request, key: str):
        if not default_storage.exists(key):
            raise Http404
        f = default_storage.open(key, "rb")
        return FileResponse(
            f,
            as_attachment=True,
            filename="event.ics",
            content_type="text/calendar; charset=utf-8",
        )       

"""

TODO: Integrate Stripe instead once I have a business set up.

"""
        
        