from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from random import randint
from benefitapp.models import *
from django.db import IntegrityError
from django.core import serializers
from django.db.models import Q
from benefitapp.utils import json_response, token_required, apikey_required,sendmail,decode_base64,make_thumbnil,upload_image,getDate,documentsUpload
from datetime import datetime
from django.db import connection
import vimeo
import json
import base64
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
import os


class getFollowersList(APIView):
    
    """
    get Followers list by user id
    
    @method GET
    @access	private
    @param	integer user_id
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id,format=None):        
        if user_id.isnumeric():
            followType = request.GET.get('followType', 'by')
            try:
                profile = Profiles.objects.get(userid=user_id)
                if followType=='to':
                    followers = Followings.objects.filter(followingprofileid=profile)  # get followers list
                else:
                    followers = Followings.objects.filter(profileid=profile)  # get following list
                field = []                
                if followers:                   
                    for fobj in followers:
                        if followType=='to':
                            userId = fobj.profileid.userid.id
                            profileId = fobj.profileid.id
                            firstName = fobj.profileid.firstname
                            lastName = fobj.profileid.lastname
                            companyname = fobj.profileid.companyname
                        else:
                            userId = fobj.followingprofileid.userid.id
                            profileId = fobj.followingprofileid.id
                            firstName = fobj.followingprofileid.firstname
                            lastName = fobj.followingprofileid.lastname
                            companyname = fobj.followingprofileid.companyname
                            
                        field.append({
                            'id':fobj.id,
                            'userid':userId,
                            'profileid':profileId,
                            'firstname':firstName,                           
                            'lastname':lastName,
                            'companyname':companyname,
                        })
                return json_response({'status':'success','result':json.dumps(field),'total':len(followers),'followType':followType}, status=200)
            except Users.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid User'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)


class getAllUsersList(APIView):
    
    """
    get all user list
    
    @method GET
    @access	private
    @param	integer user_id
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id,format=None):        
        if user_id.isnumeric():
            try:               
                Profile = Profiles.objects.get(userid=user_id)                    
                blockedUsers = Userblock.objects.filter(profileid=Profile)
                if len(blockedUsers)>0:                    
                    profile = Profiles.objects.filter(~Q(userid__logintype='T')).exclude(pk__in=[p.blockedprofileid.id for p in blockedUsers])
                else:
                    profile = Profiles.objects.filter(~Q(userid__logintype='T'))  #profile = Profiles.objects.filter(userid__is_active=1)                                   
                field = []                
                if profile:                   
                    for uobj in profile:
                        field.append({
                            'profileid':uobj.id,
                            'userid':uobj.userid.id,
                            'status':uobj.userid.is_active,     
                            'firstname':uobj.firstname,
                            'lastname':uobj.lastname,
                            'companyname':uobj.companyname,
                        })
                return json_response({'status':'success','result':json.dumps(field)}, status=200)
            except Users.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid User'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200) 
    
class composeMails(APIView):
    
    """
    compose new mail
    
    @method POST
    @access	private
    @param	integer fromProfile
    @param	integer toProfile
    @param	string message
    @param	string toAllFollowers
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request,format=None):
        fromProfile = request.POST.get('fromProfile', None)
        toProfile = request.POST.get('toProfile', None)
        message = request.POST.get('message', None)
        toAllFollowers = request.POST.get('toAllFollowers', None)
        
        if fromProfile.isnumeric():
            #groupid = fromProfile+toProfile.replace(',','')
            groupid = randint(0,999999999)
            if toAllFollowers and toAllFollowers == 'yes':
                try:
                    profile = Profiles.objects.get(userid=fromProfile)
                    try:
                        followers = Followings.objects.filter(followingprofileid=profile)
                        if message:                           
                            for fobj in followers:
                                try:
                                    profileObj = Profiles.objects.get(id=fobj.profileid.id)
                                    compose = Messages.objects.create(fromprofile=profile,toprofile=profileObj, message=message,createdate = datetime.utcnow(),groupid=groupid)
                                    
                                    if compose:
                                        # Insert User get Inbox Notification entry into pushnotification table                                        
                                        actionId = profile.userid.id
                                        if profile.companyname:
                                            profileName = profile.companyname
                                        else:
                                            profileName = profile.firstname
                                        pushmessage = '%s sent a message to your inbox.' %(profileName)
                                        try:
                                            if profileObj.id!=profile.id:
                                                notification = Pushnotification.objects.create(message=pushmessage,receiverprofileid=profileObj,is_post_read=0,is_push_read=0,is_deliver=0,action_id=actionId,action_type='inbox',senderprofileid=profile,status=1,createdate=datetime.utcnow())
                                            else:
                                                pass
                                        except:                        
                                            pass
                                    
                                except Profiles.DoesNotExist:
                                    pass
                            return json_response({'status':'success','msg':'Send successfully'}, status=200)
                        else:
                            return json_response({'status':'error','msg':'Message cant be blank'}, status=200)
                    except Followings.DoesNotExist:
                        return json_response({'status':'error','msg':'Invalid User id'}, status=200)
                except Profiles.DoesNotExist:
                    return json_response({'status':'error','msg':'Invalid User id'}, status=200)
            else:               
                try:
                    profile = Profiles.objects.get(userid=fromProfile)
                    if toProfile:
                        toList = toProfile.split(',')
                    else:
                        toList = []                   
                    if message:                                           
                        for toid in toList:
                            toId = int(toid)
                            try:
                                profileObj = Profiles.objects.get(userid=toId)
                                compose = Messages.objects.create(fromprofile=profile,toprofile=profileObj, message=message,createdate = datetime.utcnow(),groupid=groupid)
                                
                                if compose:
                                    # Insert User get Inbox Notification entry into pushnotification table                                    
                                    actionId = profile.userid.id
                                    if profile.companyname:
                                        profileName = profile.companyname
                                    else:
                                        profileName = profile.firstname
                                    pushmessage = '%s sent a message to your inbox.' %(profileName)
                                    try:
                                        if profileObj.id!=profile.id:
                                            notification = Pushnotification.objects.create(message=pushmessage,receiverprofileid=profileObj,is_post_read=0,is_push_read=0,is_deliver=0,action_id=actionId,action_type='inbox',senderprofileid=profile,status=1,createdate=datetime.utcnow())
                                        else:
                                            pass
                                    except:                        
                                        pass
                                
                            except Profiles.DoesNotExist:
                                pass
                        return json_response({'status':'success','msg':'Send successfully'}, status=200)                        
                    else:
                        return json_response({'status':'error','msg':'Message cant be blank'}, status=200)
                except Profiles.DoesNotExist:
                    return json_response({'status':'error','msg':'Invalid User id'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User id'
            }, status=400)


class inboxList(APIView):
    
    """
    get inbox mails list by user id
    
    @method GET
    @access	private
    @param	integer user_id    
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id,format=None):        
        if user_id.isnumeric():
            page = int (request.GET.get('page', 1))  
            recordsPerPage = int (request.GET.get('recordsPerPage', 10))
            try:
                profile = Profiles.objects.get(userid=user_id)
                inboxlist = Messages.objects.filter(toprofile=profile,todelete='N').order_by('-createdate')
                field = []
                thumburl = settings.BASE_URL + settings.STATIC_URL+ settings.MEDIA_URL+'thumbs/'
                if len(inboxlist)>0:
                    count = inboxlist.count()
                    paginator = Paginator(inboxlist, recordsPerPage)
                    try:
                        inboxObj = paginator.page(page)
                    except PageNotAnInteger:
                        # If page is not an integer, deliver first page.
                        inboxObj = paginator.page(1)
                    except EmptyPage:
                        # If page is out of range (e.g. 9999), deliver last page of results.
                        inboxObj = paginator.page(paginator.num_pages)
                            
                    for mObj in inboxObj:
                        if mObj.toprofile.profilephoto:
                            to_small_thumb = thumburl+'small_'+ mObj.toprofile.profilephoto
                            to_medium_thumb = thumburl+'medium_'+ mObj.toprofile.profilephoto                    
                        else:
                            to_small_thumb = ''
                            to_medium_thumb = ''
                        
                        if mObj.fromprofile.profilephoto:
                            from_small_thumb = thumburl+'small_'+ mObj.fromprofile.profilephoto
                            from_medium_thumb = thumburl+'medium_'+ mObj.fromprofile.profilephoto                    
                        else:
                            from_small_thumb = ''
                            from_medium_thumb = ''
                                
                        if mObj.createdate:                           
                            createdate = getDate(mObj.createdate)
                        else:                           
                            createdate = getDate(datetime.utcnow())
                        field.append({
                            'id':mObj.id,
                            'toid': mObj.toprofile.id,
                            'to_firstname': mObj.toprofile.firstname,
                            'to_lastname': mObj.toprofile.lastname,
                            'to_companyname': mObj.toprofile.companyname,
                            'to_small_thumb' : to_small_thumb,
                            'to_medium_thumb' : to_medium_thumb,
                            'fromid': mObj.fromprofile.id,
                            'firstname': mObj.fromprofile.firstname,
                            'lastname': mObj.fromprofile.lastname,
                            'from_companyname': mObj.fromprofile.companyname,
                            'from_small_thumb' : from_small_thumb,
                            'from_medium_thumb': from_medium_thumb,
                            'message': mObj.message,
                            'createdate': createdate,
                        })
                    return json_response({'status':'success','result':json.dumps(field),'total':len(inboxlist)}, status=200)
                else:
                    return json_response({'status':'success','msg':'Empty result','result':'Record not found'}, status=200) 
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid User id'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User id'
            }, status=400)



class sentList(APIView):
    
    """
    get send mail list by user id
    
    @method GET
    @access	private
    @param	integer user_id    
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id,format=None):        
        if user_id.isnumeric():
            page = int (request.GET.get('page', 1))  
            recordsPerPage = int (request.GET.get('recordsPerPage', 10))
            try:
                profile = Profiles.objects.get(userid=user_id)
                sentlist = Messages.objects.filter(fromprofile=profile,fromdelete='N').order_by('-createdate')
                field = []
                thumburl = settings.BASE_URL + settings.STATIC_URL+ settings.MEDIA_URL+'thumbs/'
                if len(sentlist)>0:
                    count = sentlist.count()
                    paginator = Paginator(sentlist, recordsPerPage)
                    try:
                        sentObj = paginator.page(page)
                    except PageNotAnInteger:
                        # If page is not an integer, deliver first page.
                        sentObj = paginator.page(1)
                    except EmptyPage:
                        # If page is out of range (e.g. 9999), deliver last page of results.
                        sentObj = paginator.page(paginator.num_pages)
                            
                    for mObj in sentObj:
                        if mObj.toprofile.profilephoto:
                            to_small_thumb = thumburl+'small_'+ mObj.toprofile.profilephoto
                            to_medium_thumb = thumburl+'medium_'+ mObj.toprofile.profilephoto                    
                        else:
                            to_small_thumb = ''
                            to_medium_thumb = ''
                        
                        if mObj.fromprofile.profilephoto:
                            from_small_thumb = thumburl+'small_'+ mObj.fromprofile.profilephoto
                            from_medium_thumb = thumburl+'medium_'+ mObj.fromprofile.profilephoto                    
                        else:
                            from_small_thumb = ''
                            from_medium_thumb = ''
                                
                        if mObj.createdate:                           
                            createdate = getDate(mObj.createdate)
                        else:                           
                            createdate = getDate(datetime.utcnow())
                        field.append({
                            'id':mObj.id,
                            'toid': mObj.toprofile.id,
                            'to_firstname': mObj.toprofile.firstname,
                            'to_lastname': mObj.toprofile.lastname,
                            'to_companyname': mObj.toprofile.companyname,
                            'to_small_thumb' : to_small_thumb,
                            'to_medium_thumb' : to_medium_thumb,
                            'fromid': mObj.fromprofile.id,
                            'firstname': mObj.fromprofile.firstname,
                            'lastname': mObj.fromprofile.lastname,
                            'from_companyname': mObj.fromprofile.companyname,
                            'from_small_thumb' : from_small_thumb,
                            'from_medium_thumb': from_medium_thumb,
                            'message': mObj.message,
                            'createdate': createdate,
                        })
                    return json_response({'status':'success','result':json.dumps(field),'total':len(sentlist)}, status=200)
                else:
                    return json_response({'status':'success','msg':'Empty result','result':'Record not found'}, status=200) 
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid User id'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User id'
            }, status=400)
        

class getMessageDetail(APIView):
    
    """
    get messgae detail by id
    
    @method GET
    @access	private
    @param	integer message_id    
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,message_id,format=None):       
        if message_id.isnumeric():
            try:               
                message = Messages.objects.get(id=message_id)
                thumburl = settings.BASE_URL + settings.STATIC_URL+ settings.MEDIA_URL+'thumbs/'
                if message.toprofile.profilephoto:
                    to_small_thumb = thumburl+'small_'+ message.toprofile.profilephoto
                    to_medium_thumb = thumburl+'medium_'+ message.toprofile.profilephoto                    
                else:
                    to_small_thumb = ''
                    to_medium_thumb = ''
                
                if message.fromprofile.profilephoto:
                    from_small_thumb = thumburl+'small_'+ message.fromprofile.profilephoto
                    from_medium_thumb = thumburl+'medium_'+ message.fromprofile.profilephoto                    
                else:
                    from_small_thumb = ''
                    from_medium_thumb = ''
                
                if message.createdate:                           
                    createdate = getDate(message.createdate)
                else:                           
                    createdate = getDate(datetime.utcnow())
                return json_response({'status':'success','result':{
                                                            'id':message.id,
                                                            'toid':message.toprofile.id,
                                                            'to_firstname': message.toprofile.firstname,
                                                            'to_lastname': message.toprofile.lastname,
                                                            'to_companyname': message.toprofile.companyname,
                                                            'to_small_thumb' : to_small_thumb,
                                                            'to_medium_thumb' : to_medium_thumb,
                                                            'fromid': message.fromprofile.id,
                                                            'firstname': message.fromprofile.firstname,
                                                            'lastname': message.fromprofile.lastname,
                                                            'from_companyname': message.fromprofile.companyname,
                                                            'from_small_thumb' : from_small_thumb,
                                                            'from_medium_thumb': from_medium_thumb,
                                                            'message': message.message,
                                                            'createdate': createdate,
                                                            'message':message.message
                                                        }}, status=200)
            except Messages.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid Message Id'}, status=200) 
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Message Id'
            }, status=200)



class deleteMessage(APIView):
    
    """
    delete messgae by id
    
    @method POST
    @access	private
    @param	string toDelete
    @param	string fromDelete
    @param	integer messageId    
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request,format=None):
        toDelete = request.POST.get('toDelete', None)
        fromDelete = request.POST.get('fromDelete', None)
        message_id = request.POST.get('messageId', None)        
        if message_id.isnumeric() and toDelete is not None and fromDelete is not None:
            try:               
                message = Messages.objects.get(id=message_id)
                if toDelete is not None and toDelete == 'Y':
                    message.todelete =  toDelete
                if fromDelete is not None and fromDelete == 'Y':    
                    message.fromdelete = fromDelete
                message.save()
                return json_response({'status':'success','result':{'id':message.id,'message':message.message}}, status=200)
            except Messages.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid Message Id'}, status=200) 
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Message Id'
            }, status=200)


class inviteUsers_old(APIView):
    
    """
    Invite Users
    
    @method POST
    @access	private
    @param	integer fromProfile
    @param	integer toProfile
    @param	string referalCode    
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request,format=None):
        fromProfile = request.POST.get('fromProfile', None)
        toProfile = request.POST.get('toProfile', 'All')
        referalCode = request.POST.get('referalCode', None)       
        subject = 'The Benefit app invite'
        templatePath = os.path.join(settings.BASE_DIR, 'templates/admin/email')
        baseUrl = settings.BASE_URL + settings.STATIC_URL
        if fromProfile.isnumeric():
            to_email_ids= []
            to_list = ''
            if toProfile=='All':
                try:
                    profile = Profiles.objects.get(userid=fromProfile)
                    message = render_to_string(templatePath+'/invite.html', {'profileid': profile.id,'userid':profile.userid.id,'firstname':profile.firstname,'lastname':profile.lastname,'baseUrl':baseUrl})
                    try:
                        userList = Users.objects.all()
                        if userList:
                            for uObj in userList:
                                to_email_ids.append(uObj.email)                                    
                        sendStatus = sendmail(subject,message,to_email_ids,fromProfile,page='bulk')
                        if sendStatus=='success':
                            return json_response({'status':'success','msg':'Send successfully'}, status=200)
                        else:
                            return json_response({'status':'success','msg':'Mail send failed','sendmail':sendStatus}, status=200)         
                    except Users.DoesNotExist:
                        return json_response({'status':'error','msg':'Invalid User id'}, status=200)
                except Profiles.DoesNotExist:
                    return json_response({'status':'error','msg':'Invalid User id'}, status=200)
            else:               
                try:
                    profile = Profiles.objects.get(userid=fromProfile)
                    message = render_to_string(templatePath+'/invite.html', {'profileid': profile.id,'userid':profile.userid.id,'firstname':profile.firstname,'lastname':profile.lastname,'referalcode':profile.userid.usercode,'baseUrl':baseUrl})
                    if toProfile:
                        toList = toProfile.split(',')
                    else:
                        toList = []                   
                    if message:                                           
                        try:                                
                            userList = Users.objects.filter(id__in=toList)
                            if userList:
                                for uObj in userList:
                                    to_email_ids.append(uObj.email)                                                
                            sendStatus = sendmail(subject,message,to_email_ids,fromProfile,page='bulk')
                        except Users.DoesNotExist:
                            pass                       
                        if sendStatus=='success':
                            return json_response({'status':'success','msg':'Send successfully','sendStatus':sendStatus}, status=200)
                        else:
                            return json_response({'status':'success','msg':'Mail send failed','sendmail':sendStatus}, status=200)                     
                    else:
                        return json_response({'status':'error','msg':'Message cant be blank'}, status=200)
                except Profiles.DoesNotExist:
                    return json_response({'status':'error','msg':'Invalid User id'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User id'
            }, status=400)
        
        
class inviteUsers(APIView):
    
    """
    Invite Users to get access benefit
    
    @method POST
    @access	private
    @param	integer fromProfile
    @param	integer toProfile
    @param	string referalCode    
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request,format=None):
        fromProfile = request.POST.get('fromProfile', None)
        toProfile = request.POST.get('toProfile', None)
        referalCode = request.POST.get('referalCode', None)       
        subject = 'The Benefit app invite'
        templatePath = os.path.join(settings.BASE_DIR, 'templates/admin/email')
        baseUrl = settings.BASE_URL + settings.STATIC_URL
        if fromProfile.isnumeric():                            
            try:
                profile = Profiles.objects.get(userid=fromProfile)
                message = render_to_string(templatePath+'/invite.html', {'profileid': profile.id,'userid':profile.userid.id,'firstname':profile.firstname,'lastname':profile.lastname,'referalcode':profile.referalcode,'baseUrl':baseUrl})                            
                if message:
                    if toProfile is not None:
                        fromUserId = profile.userid.email
                        sendStatus = sendmail(subject,message,toProfile,fromUserId)                     
                        if sendStatus=='success':
                            return json_response({'status':'success','msg':'Send successfully','sendStatus':sendStatus}, status=200)
                        else:
                            return json_response({'status':'success','msg':'Mail send failed','sendmail':sendStatus}, status=200)
                    else:
                        return json_response({'status':'success','msg':'Recipient email id is required'}, status=200)      
                else:
                    return json_response({'status':'error','msg':'Message cant be blank'}, status=200)
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid User id'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User id'
            }, status=400)
        
        
class contact(APIView):
    
    """
    Contact with users
    
    @method POST
    @access	private
    @param	integer userId   
    @param	string message    
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request,format=None):
        userId = request.POST.get('userId', None)       
        message = request.POST.get('message', None)
        templatePath = os.path.join(settings.BASE_DIR, 'templates/admin/email')
        baseUrl = settings.BASE_URL + settings.STATIC_URL
        subject = 'Message from benefit'
        if userId.isnumeric():
            try:
                profile = Profiles.objects.get(userid=userId)
                contactMessage = render_to_string(templatePath+'/contact.html', {'profileid': profile.id,'userid':profile.userid.id,'firstname':profile.firstname,'lastname':profile.lastname,'baseUrl':baseUrl,'message':message})
                toEmailId = settings.EMAIL_HOST_USER
                fromId = profile.userid.email
                sendStatus = sendmail(subject,contactMessage,toEmailId,fromId)
                if sendStatus=='success':
                    return json_response({'status':'success','msg':'Send successfully','sendStatus':sendStatus}, status=200)
                else:
                    return json_response({'status':'success','msg':'Mail send failed','sendmail':sendStatus}, status=200)                
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid User id'}, status=200)                
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User id'
            }, status=400)