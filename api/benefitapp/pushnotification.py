from __future__ import unicode_literals
from django.conf import settings
import random
import hashlib
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import base64
import json
from benefitapp.serializers import UserSerializer
from benefitapp.models import Users,Profiles,Followings,Category,Profilecategory,userSocailProfile,Post,Products,Userblock
from django.db import IntegrityError
from django.core import serializers
from django.db.models import Q
from benefitapp.utils import json_response, token_required, apikey_required,sendmail,make_thumbnil_profile,decode_base64,upload_image_profile,ssoTokenGenerator
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import vimeo
import os
import time
from django.template.loader import render_to_string
from passlib.hash import pbkdf2_sha256
 


class test(APIView):
    
    def post(self, request, format=None):
        return  json_response({"success": "Successfully tested."})
        #return  Response({"success": "Successfully tested."})