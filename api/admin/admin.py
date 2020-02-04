from django.contrib import admin
from django import forms
from django.forms import ModelForm, Textarea
from benefitapp.models import Category,Users,Profiles,Followings,Post,Comments,Postlikes,Postratings,Favorites,Products,Albums,Postcategory,Imagetag,Poststatistics,Profilecategory,Videoviewhistory
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User,Group
from datetime import datetime
from django.utils.html import format_html
from django.conf.urls import patterns, include, url
from django.template import RequestContext    
from django.shortcuts import render_to_response
from django.core import serializers
from django.conf import settings
from django.views.generic import TemplateView,ListView
import json
from benefitapp.utils import json_response, token_required, apikey_required,sendmail,decode_base64,make_thumbnil,upload_image,getDate
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.contrib.sites.models import Site
from django.views.generic import ListView, DetailView

admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Token)

admin.site.register(Users)
admin.site.register(Post)