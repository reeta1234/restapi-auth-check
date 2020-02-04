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
from benefitapp.models import Users,Profiles,Followings,Category,Profilecategory,userSocailProfile,Post,Products,Userblock,Pushnotification
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
import hashlib


class UserSignUp(APIView):
    """
    Create a new user using signup page
    
    @method Post
    @access	private
    @param	string email
    @param	string password
    @param	string fullName    
    @param	string referalCode
    @param	string loginType
    @param	string deviceId
    @param	string deviceToken  
    @return	json array
    """
        
    @apikey_required
    def post(self, request, format=None):
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        fullName = request.POST.get('fullName', None)
        companyName = request.POST.get('companyName', None)
        referalCode=request.POST.get('referalCode', None)
        loginType=request.POST.get('loginType', 'B')
        deviceId=request.POST.get('deviceId', None)
        deviceToken=request.POST.get('deviceToken',None)
        templatePath = os.path.join(settings.BASE_DIR, 'templates/admin/email')
        baseUrl = settings.BASE_URL + settings.STATIC_URL        

        if email is not None and password is not None and (fullName is not None or companyName is not None):
            """
            if companyName is not None:
                fullName = companyName
            else:
                fullName = fullName
            """
            token = ssoTokenGenerator(32)
            hashkey = ssoTokenGenerator(6)
            usercode = ssoTokenGenerator(6)
            encryptPassword = hashlib.md5(password).hexdigest()
            try:
                user = Users.objects.get(email=request.POST['email'])
                return json_response({'status':'error','msg': 'User already exists'}, status=status.HTTP_400_BAD_REQUEST)
            except Users.DoesNotExist:
                #referCode=fullName.replace(' ','')+ssoTokenGenerator(4)
                referCode=ssoTokenGenerator(6)
                subject="User Registration Activation Email"            
                #message="Email Verification Code: "+hashkey
                message = render_to_string(templatePath+'/email_verification.html', {'hashkey': hashkey,'email':email,'baseUrl':baseUrl})
                if referalCode:                    
                    try:
                        usercode = Profiles.objects.get(referalcode=referalCode)
                        user = Users.objects.create(email=request.POST['email'], password=encryptPassword,ssotoken=token,hash=hashkey,logintype=loginType,deviceid=deviceId,devicetoken=deviceToken,is_active=1,notification=1,usercode=usercode,isfirsttimelogin=0,createdate = datetime.utcnow())
                                                                    
                        try:
                            userid = Users.objects.get(email=request.POST['email'])                        
                            userp = Profiles.objects.create(userid=userid,firstname=fullName,companyname=companyName,referalcode=referCode,updatedate=datetime.utcnow())
                            try:
                                userprofile = Profiles.objects.get(userid=userid.id)
                                
                                
                                if user:
                                    # Insert User referral code Notification entry into pushnotification table                                    
                                    actionId = userid.id
                                    if userprofile.companyname:
                                        profileName = userprofile.companyname
                                    else:
                                        profileName = userprofile.firstname
                                    message = '%s registered using your referral code.' %(profileName)
                                    try:                       
                                        notification = Pushnotification.objects.create(message=message,receiverprofileid=usercode,is_post_read=0,is_push_read=0,is_deliver=0,action_id=actionId,action_type='referral_used',senderprofileid=userprofile,status=1,createdate=datetime.utcnow())                               
                                    except:                        
                                        pass
                                
                                follower = Followings.objects.create(profileid=userprofile, followingprofileid=usercode, createdate=datetime.utcnow())
                            except Profiles.DoesNotExist:
                                return json_response({'status':'error','msg': 'Invalid user id'}, status=status.HTTP_400_BAD_REQUEST)
                            sendStatus = sendmail(subject,message,request.POST['email'])     
                            return json_response({'status':'success','data':{'token': token,'email': user.email,'id' : userid.id,'userReferalCode':referCode,'loginType':loginType}, 'msg' : 'User sign up successfully.'})
                        except Users.DoesNotExist:
                            return json_response({'status':'error','msg': 'Invalid email id'}, status=status.HTTP_400_BAD_REQUEST)
                    except Profiles.DoesNotExist:
                        return json_response({'status':'error','msg':'Invalid referral code'})                   
                else:                    
                    user = Users.objects.create(email=request.POST['email'], password=encryptPassword,ssotoken=token,hash=hashkey,logintype=loginType,deviceid=deviceId,devicetoken=deviceToken,is_active=1,notification=1,usercode=usercode,isfirsttimelogin=0,createdate = datetime.utcnow())
                    try:
                        userid = Users.objects.get(email=request.POST['email'])
                        userp = Profiles.objects.create(userid=userid,firstname=fullName,companyname=companyName,referalcode=referCode,updatedate=datetime.utcnow())
                        sendStatus = sendmail(subject,message,request.POST['email'])     
                        return json_response({'status':'success','data':{'token': token,'email': user.email,'id' : userid.id,'userReferalCode':referCode,'loginType':loginType}, 'msg' : 'User sign up successfully.'})
                    except Users.DoesNotExist:
                        return json_response({'status':'error','msg': 'Invalid userid'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return json_response({'status':'error','msg': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
        

class UserAuthSignUp(APIView):
    """
    Create a new user by social media.
    
    @method Post   
    @access	private
    @param	string firstName
    @param	string lastName
    @param	string email    
    @param	string gender
    @param	integer clientId
    @param	string profileType
    @param	string deviceId
    @param	string deviceToken  
    @return	json array
    """
        
    @apikey_required
    def post(self, request, format=None):            
        firstName = request.POST.get('firstName', None)
        lastName = request.POST.get('lastName', None)
        companyName = request.POST.get('companyName', None)
        email = request.POST.get('email', None)
        gender = request.POST.get('gender', None)   
        clientId = request.POST.get('clientId', None)        
        profiletype=request.POST.get('profileType', 'B')
        deviceId=request.POST.get('deviceId', None)
        deviceToken=request.POST.get('deviceToken',None)

        if clientId is not None:
            token = ssoTokenGenerator(32)
            hashkey = ssoTokenGenerator(6)
            usercode = ssoTokenGenerator(6)
            referCode=ssoTokenGenerator(6)
            
            # Reset device id and device token
            if deviceId and deviceToken:
                try:
                    user = Users.objects.get(deviceid=deviceId,devicetoken=deviceToken)
                    if user:
                        user.deviceid = ''
                        user.devicetoken = ''
                        user.save()
                    else:
                        pass
                except Users.DoesNotExist:
                    pass
            else:
                pass
            
            # Social login
            try:
                authid = userSocailProfile.objects.get(profileid=clientId)
                try:
                    user = Users.objects.get(id=authid.userid.id)
                    isFirstTimeLogin = user.isfirsttimelogin
                    if user.ssotoken == "":
                        user.ssotoken = token
                    user.deviceid =  deviceId
                    user.devicetoken = deviceToken
                    user.save()
                    return json_response({'status':'success','data':{'email': user.email,'token': user.ssotoken,'id' : user.id,'userReferalCode':referCode,'loginType':profiletype, 'isFirstTimeLogin':2},'msg': 'User already exists'}, status=200)
                except Users.DoesNotExist:
                    return json_response({'status':'error','msg': 'Invalid User id'}, status=status.HTTP_400_BAD_REQUEST)     
            except userSocailProfile.DoesNotExist:
                try:    
                    userid = Users.objects.get(email=email)
                    try:
                        userprofile = Profiles.objects.get(userid=userid)
                        return json_response({'status':'success','data':{'email': userid.email,'token': userid.ssotoken,'id' : userid.id,'userReferalCode':userprofile.referalcode,'loginType':profiletype,'isFirstTimeLogin':2},'msg':'User sign up successfully'})                
                    except Profiles.DoesNotExist:
                        userp = Profiles.objects.create(userid=userid,firstname=firstName,companyname=companyName,gender=gender,referalcode=referCode,updatedate=datetime.utcnow())
                        userprofile = Profiles.objects.get(userid=userid)
                        user = userSocailProfile.objects.create(userid=userid,profiletype=profiletype,profileid=clientId)
                        return json_response({'status':'success','data':{'email': userid.email,'token': userid.ssotoken,'id' : userid.id,'userReferalCode':userprofile.referalcode,'loginType':profiletype,'isFirstTimeLogin':2},'msg':'User sign up successfully'})                
                except Users.DoesNotExist:
                    user = Users.objects.create(email=email,ssotoken=token,hash=hashkey,logintype=profiletype,deviceid=deviceId,devicetoken=deviceToken,is_active=1,notification=1,usercode=usercode,isfirsttimelogin=1,createdate=datetime.utcnow(),lastlogindate=datetime.utcnow())
                    try:
                        userid = Users.objects.get(email=email)
                        user = userSocailProfile.objects.create(userid=userid,profiletype=profiletype,profileid=clientId)
                        userp = Profiles.objects.create(userid=userid,firstname=firstName,companyname=companyName,gender=gender,referalcode=referCode,updatedate=datetime.utcnow())
                        return json_response({'status':'success','data':{'email': userid.email,'token': token,'id' : userid.id,'userReferalCode':referCode,'loginType':profiletype,'isFirstTimeLogin':1},'msg':'User sign up successfully'})
                    except Users.DoesNotExist:
                        return json_response({'status':'error','msg': 'Invalid userid'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return json_response({'status':'error','msg': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)        
    

class UserSignIn(APIView):
    
    """
    User login with email & password
    
    @method Post
    @access	private
    @param	string email
    @param	string password
    @param	string loginType        
    @return	json array
    """
    
    @apikey_required
    def post(self, request, format=None):
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        loginType=request.POST.get('loginType', 'B')
        deviceId=request.POST.get('deviceId', None)
        deviceToken=request.POST.get('deviceToken',None)        
    
        if email is not None and password is not None:
            encryptPassword = hashlib.md5(password).hexdigest()
            if deviceId and deviceToken:
                try:
                    user = Users.objects.get(deviceid=deviceId,devicetoken=deviceToken)           
                    if user:
                        user.deviceid = ''
                        user.devicetoken = ''
                        user.save()
                    else:
                        pass
                except Users.DoesNotExist:
                    pass
            else:
                pass
        
            try:
                user = Users.objects.get(email=request.POST['email'], password=encryptPassword,is_active=1)
            except Users.DoesNotExist:
                user = None
                
            if user is not None:
                if user.id:
                    try:
                        profile = Profiles.objects.get(userid=user)
                        firstname = profile.firstname
                        lastname = profile.lastname
                        referralCode = profile.referalcode
                    except Profiles.DoesNotEsixt:
                        firstname = lastname = referralCode = ''
                    
                    if (user.ssotoken == ""):
                        user.ssotoken =  ssoTokenGenerator(32)
                    user.deviceid =  deviceId
                    user.devicetoken = deviceToken
                    user.lastlogindate= datetime.utcnow()
                    if user.isfirsttimelogin==0:
                         user.isfirsttimelogin= 1
                    else:
                        if user.isfirsttimelogin==1:
                            user.isfirsttimelogin= 2
                    user.save()
                    return json_response({
                        'status':'success',
                        'data':{
                            'token': user.ssotoken,
                            'email': user.email,
                            'firstname': firstname,
                            'lastname': lastname,
                            'id' : user.id,
                            'loginType':loginType,
                            'userReferalCode':referralCode,
                            'isFirstTimeLogin':user.isfirsttimelogin
                        },
                        'msg': 'User logged in successfully'
                    })
                else:
                    return json_response({'status':'error','msg': 'Invalid User4'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return json_response({'status':'error','msg': 'Invalid Username/Password Or Inactivate account'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Data'
            }, status=400)
        

class Logout(APIView):
    
    """
    user logout on basis of Authorization : Token <authToken value>
    """

    @apikey_required
   
    def post(self, request, format=None):
        auth_header = request.POST.get('X-AUTHTOKEN',None)
        apiKey_header = request.POST.get('X-APIKEY',None)
        try:
            #user = Users.objects.get(ssotoken=request.token)
            user = Users.objects.get(ssotoken=auth_header)
            #user.ssotoken = ''
            user.deviceid = ''
            user.devicetoken = ''
            user.save()
        except Users.DoesNotExist:
            pass
        return json_response({'status': 'success', 'msg' : 'User logout'})



class UserChangePassword(APIView):
    
    """
    User change password
    
    @method Post
    @access	private
    @param	string email
    @param	string oldpassword
    @param	string newpassword        
    @return	json array
    """
    
    @apikey_required
    @token_required
    def post(self, request, format=None):
        email = request.POST.get('email', None)
        oldpassword = request.POST.get('oldpassword', None)
        newpassword = request.POST.get('newpassword', None)
        templatePath = os.path.join(settings.BASE_DIR, 'templates/admin/email')
        baseUrl = settings.BASE_URL + settings.STATIC_URL
    
        if email is not None and oldpassword is not None:
            try:
                encryptOldPassword = hashlib.md5(oldpassword).hexdigest()
                user = Users.objects.get(email=request.POST['email'], password=encryptOldPassword)
            except Users.DoesNotExist:
                user = None
                
            if user is not None:
                if user.id:
                    user.password = hashlib.md5(newpassword).hexdigest()
                    user.ssotoken = ''
                    user.save()
                    subject="Password Changed"
                    #message="Password Changed Notification mail"
                    message = render_to_string(templatePath+'/change_password.html', {'userid': user.id,'email':user.email,'baseUrl':baseUrl})
                    sendStatus = sendmail(subject,message,request.POST['email'])     
                    return json_response({
                        'status':'success',
                        'msg': 'User password changed successfully.',
                        'sendStatus':sendStatus,
                    })
                else:
                    return json_response({'status':'error','msg': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return json_response({'status':'error','msg': 'Old password is incorrect'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Data'
            }, status=400)
        
class UserEmailVerification(APIView):
    
    """
    User Email Verification
    
    @method Post 
    @access	private
    @param	string verificationCode    
    @return	json array
    """
    
    @apikey_required
    def post(self, request, format=None):        
        verificationCode = request.POST.get('verificationCode', None)  
    
        if verificationCode is not None:
            try:
                user = Users.objects.get(hash=request.POST['verificationCode'])
            except Users.DoesNotExist:
                user = None
                
            if user is not None:
                if user.id:
                    user.is_active = 1					
                    user.save()
                    return json_response({
                        'status':'success',
                        'data':{
                            'token': user.ssotoken,
                            'email': user.email,
                            'id' : user.id
                        },
                        'msg': 'Email verify successfully.'
                    })
                else:
                    return json_response({'status':'error','msg': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return json_response({'status':'error','msg': 'Invalid Email/Verification Code'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Data'
            }, status=400)


class UserForgetPassword(APIView):
    
    """
    User forget password
    
    @method Post
    @access	private
    @param	string email    
    @return	json array
    """
    
    @apikey_required
    def post(self, request, format=None):
        email = request.POST.get('email', None)
        templatePath = os.path.join(settings.BASE_DIR, 'templates/admin/email')
        baseUrl = settings.BASE_URL + settings.STATIC_URL
    
        if email is not None :
            try:
                user = Users.objects.get(email=request.POST['email'])
            except Users.DoesNotExist:
                user = None
                
            if user is not None:
                newpassword= ssoTokenGenerator(8)
                if user.id:
                    user.password =  hashlib.md5(newpassword).hexdigest()#newpassword					
                    user.save()
                    subject="Forget Password"
                    #message="Forget Password Notification mail"
                    #message+="<br> New password: " + newpassword
                    message = render_to_string(templatePath+'/forget_password.html', {'userid': user.id,'email':user.email,'newpassword':newpassword,'baseUrl':baseUrl})
                    sendStatus = sendmail(subject,message,request.POST['email'])     
                    return json_response({
                        'status':'success',
                        'data':{
                            'newpassword': user.password,
                            'email': user.email,
                            'id' : user.id,
                            'sendStatus':sendStatus,
                        },
                        'msg': 'An email has been sent on your email address with new password.'
                    })
                else:
                    return json_response({'status':'error','msg': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return json_response({'status':'error','msg': 'Invalid Email'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Data'
            }, status=400)



class UpdateUserProfile(APIView):
    
    """
    Update user profile
    
    @method Post
    @access	private    
    @param	string FirstName
    @param	string LastName
    @param	string Gender
    @param	string profileImage
    @param	string Website
    @param	string Location
    @param	integer Age
    @param	integer userid    
    @return	json array
    """
    
    @apikey_required
    @token_required
    def post(self, request, format=None):
        user_id = Users.objects.filter(id=request.POST['userid'])        
        #user_id = request.POST.get('userid', None)
        firstname=request.POST.get('FirstName', None)        
        companyName = request.POST.get('companyName', None)
        """
        if companyName is not None and firstname is None:
            firstname = companyName
        else:
            firstname = firstname
        """
            
        millis = int(round(time.time() * 1000))
            
        if user_id.exists():
            try:
                user = Profiles.objects.get(userid=request.POST['userid'])
            except Profiles.DoesNotExist:
                user = None
                
            if user is not None:
                if user.userid:
                    if (firstname or companyName):
                        """
                        if companyName and companyName is not None:
                            firstname = companyName
                        else:
                            firstname = firstname
                        """
                        user.firstname=firstname
                        user.lastname=request.POST.get('LastName', None)
                        user.companyname=companyName
                        user.gender=request.POST.get('Gender',None)
                        
                        # Profile Image Create
                        profileImage = request.POST.get('profileImage',None)
                        filename = ''                    
                        if profileImage in [None, '']:
                            filename = ''
                        else:                        
                            filename = "profile_%s.jpeg" % str(request.POST['userid']).replace('.','_')
                            """
                            binary_data = decode_base64(profileImage)
                            fd = open(settings.MEDIA_ROOT + settings.MEDIA_URL + filename, 'wb')
                            fd.write(binary_data)
                            fd.close()                        
                            # Profile Image Thumb
                            #thumbname = "uploaded_image_%s_thumb.png" % str(request.POST['userid']).replace('.','_')
                            """
                            upload_image_profile(filename,profileImage,settings.MEDIA_URL)
                            make_thumbnil_profile(filename,request.POST['userid'],'profile',settings.MEDIA_URL)
                            user.profilephoto = filename+'?%s' %(millis)
                        
                        user.age=request.POST.get('Age',None)
                        user.website=request.POST.get('Website',None)
                        user.location=request.POST.get('Location',None)
                        user.updatedate = datetime.utcnow()
                        user.save()
                        
                        return json_response({
                            'status':'success',                    
                            'msg': 'User Profile Updated successfully.',                    
                        })
                    else:
                        return json_response({'status':'error','msg': 'Fullname is required.'}, status=status.HTTP_400_BAD_REQUEST)
                else:                    
                    return json_response({'status':'error','msg': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user_id1 = Users.objects.get(id=request.POST['userid'])
                user = Profiles.objects.create(userid=user_id1,firstname=request.POST.get('FirstName',None), lastname=request.POST.get('LastName',None),gender=request.POST.get('Gender',None),
                                               profilephoto=request.FILES.get('ProfilePhoto', None),age=request.POST.get('Age',None),location=request.POST.get('Location',None),updatedate=datetime.utcnow())
                return json_response({'status':'success','msg': 'User Profile Updated successfully'})               
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Data'
            }, status=400)


class UpdateUserProfileStep2(APIView):
    
    """
    update user profile step2
    
    @method Post 
    @access	private
    @param	string bio
    @param string category
    @param integer userid
    @return	json array
    """
    
    @apikey_required
    @token_required
    def post(self, request, format=None):
        user_id = Users.objects.filter(id=request.POST['userid'])        
        bio = request.POST.get('Bio', None)           
        
        categoryString = request.POST.get('category', None)
        if categoryString:
            category = categoryString.split(',')
        else:
            category = []
        
        if user_id.exists():
            try:
                user = Profiles.objects.get(userid=request.POST['userid'])
            except Profiles.DoesNotExist:
                user = None
                
            if user is not None:
                if user.userid:                    
                    user.bio = bio                
                    user.updatedate = datetime.utcnow()
                    user.save()
                    Profilecategory.objects.filter(profileid=user).delete()
                    # Update profilecategory table
                    for pkid in category: 
                        cId = int(pkid)
                        try:
                            catid = Category.objects.get(id=cId)
                            Profilecategory.objects.create(categoryid = catid,profileid = user,createdate = datetime.utcnow())
                        except Category.DoesNotExist:
                            pass
                        
                    return json_response({
                        'status':'success',                    
                        'msg': 'User Profile Updated successfully.',                        
                    })
                else:                    
                    return json_response({'status':'error','msg': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                user_id1 = Users.objects.get(id=request.POST['userid'])
                user = Profiles.objects.create(userid=user_id1,firstname=request.POST.get('FirstName',None), lastname=request.POST.get('LastName',None),gender=request.POST.get('Gender',None),
                                               profilephoto=request.FILES.get('ProfilePhoto', None),age=request.POST.get('Age',None),location=request.POST.get('Location',None),updatedate=datetime.utcnow())
                return json_response({'status':'success','msg': 'User Profile Updated successfully'})               
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Data'
            }, status=400)
        
       
class getUserList(APIView):
    
    """
    get User List
    
    @method Post 
    @access	private
    @param	none    
    @return	json array
    
    """
    @apikey_required
    @token_required
    def get(self, request, format=None):
        
        page = int (request.GET.get('page', 1))  
        recordsPerPage = int (request.GET.get('recordsPerPage', 10))
        searchText = request.GET.get('searchText', None)
        profile_url =  profileimg = settings.BASE_URL + settings.STATIC_URL+ settings.MEDIA_URL
        field = []
        if searchText:           
            userlist = Profiles.objects.filter(Q(firstname=searchText) | Q(lastname=searchText)).all().order_by('firstname').select_related('userid')
        else: 
        	userlist = Profiles.objects.all().order_by('firstname').select_related('userid')
        
        if userlist:
            count = userlist.count()
            paginator = Paginator(userlist, recordsPerPage) # Show 25 contacts per page  
            try:
                userObj = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                userObj = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                userObj = paginator.page(paginator.num_pages)
            
            for profileObj in userObj:
                joinedOn = ''
                if profileObj.userid.createdate is not None:
                    joinedOn = profileObj.userid.createdate.strftime('%m/%d/%Y')
                    
                field.append(
                    {
                    'userStatus':profileObj.userid.is_active, 
                    'firstname':profileObj.firstname,
                    'lastname' : profileObj.lastname,
                    'type' : profileObj.userid.logintype,
                    'updatedate' : joinedOn,
                    'profilephoto' : profileObj.profilephoto,
                    'userid' : profileObj.userid.id
                    }
                )
            
            #data = serializers.serialize('json', userObj, fields=('firstname','lastname','type','updatedate','profilephoto','userid'))
            return json_response({'status':'success','data': json.dumps(field), 'profile_url': profile_url, 'total': count}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'No record found'
            }, status=400)


class getUserDetail(APIView):
    
    """
    Get user detail by id
    
    @method Get 
    @access	private   
    @param integer userid
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id,format=None):
        
        userid = user_id              
        if userid:
                try:
                    user = Profiles.objects.get(userid=userid)
                    userid = Users.objects.get(id=userid)
                    category = Category.objects.all()
                    catdata = serializers.serialize('json', category)
                    profilecategory = Profilecategory.objects.select_related('profileid').filter(profileid=user.id)
                    profilecatdata = serializers.serialize('json', profilecategory,fields=('categoryid'))
                    profileimg = mediumthumbimg = smallthumbimg = ''                    
                    if user.profilephoto:
                        profileimg = settings.BASE_URL + settings.STATIC_URL+ settings.MEDIA_URL + user.profilephoto                        
                        mediumthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/medium_'+user.profilephoto
                        smallthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/small_'+user.profilephoto
                    
                    bannerimg = medium_banner_thumbimg = small_banner_thumbimg = ''
                    if user.banner:
                        bannerimg = settings.BASE_URL + settings.STATIC_URL+ settings.BANNER_URL + user.banner                        
                        medium_banner_thumbimg = settings.BASE_URL + settings.STATIC_URL+settings.BANNER_URL+'thumbs/medium_'+user.banner
                        small_banner_thumbimg = settings.BASE_URL + settings.STATIC_URL+settings.BANNER_URL+'thumbs/small_'+user.banner
                        
                    totalMyFollowers = Followings.objects.filter(profileid=user)
                    
                    totalFollowing = Followings.objects.filter(followingprofileid=user)         
                                                                       
                    #Total Text Post
                    totalText = Post.objects.filter(profileid=user.id,type='T')
                    
                    #Total Video Post
                    totalVideo = Post.objects.filter(profileid=user.id,type='V')
                    
                    #Total Image Post
                    totalImage = Post.objects.filter(profileid=user.id,type='I')
                    
                    #Total All Post
                    totalAllPost = Post.objects.filter(profileid=user.id)
                    
                    #Total All Products
                    totalProducts = Products.objects.filter(profileid=user.id)
                                                        
                    return json_response({'status':'success','data':
                            {'userid':userid.id,'profileid':user.id,'email':userid.email,'firstname':user.firstname,'lastname':user.lastname,'companyname':user.companyname,'gender':user.gender,'age':user.age,'location':user.location,'about':user.bio,
                             'image':profileimg,'mediumthumb':mediumthumbimg,'smallthumb':smallthumbimg, 'referalcode' : user.referalcode,'bannerimg':bannerimg,'medium_banner_thumbimg':medium_banner_thumbimg,'small_banner_thumbimg':small_banner_thumbimg,'website':user.website,'totalMyFollowers':len(totalMyFollowers),'totalFollowing':len(totalFollowing),'totalText':len(totalText),'totalVideo':len(totalVideo),'totalImage':len(totalImage),'totalAllPost':len(totalAllPost),'totalProducts':len(totalProducts)},
                            'categorylist':catdata,'profilecategory':profilecatdata}, status=200)
                except Profiles.DoesNotExist:
                    return json_response({'status':'error','msg':'Invalid User Id'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Data'
            }, status=400)
        
        

class setUserStatus(APIView):
    
    """
    Set user status
    
    @method Get 
    @access	private   
    @param integer userid
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request, format=None,**kwargs):
        user = Users.objects.get(id=kwargs['user_id'])        
        if user:
                if user.is_active==1:
                    userstatus=0
                    result="Deactiavte"
                else:
                    userstatus=1
                    result="Actiavte"
                user.is_active =  userstatus
                user.save()
                return json_response({'status':'success','msg':'Status Changed successfully','userstatus':result
                    }, status=200)                       
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Data'
            }, status=400)


class updateReferralCode(APIView):
    
    """
    Update referral code
    
    @method Post
    @access	private   
    @param integer userid
    @param string referralCode
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):
        userid = request.POST.get('userId', None)
        referralcode = request.POST.get('referralCode', None)      
        if userid:
                if len(referralcode)>6 or len(referralcode)<6:
                     return json_response({'status':'error','msg':'Referral code must be 6 character.'}, status=200)
                else:
                    try:
                        userprofile = Profiles.objects.get(userid=userid)            
                        userprofile.referalcode =  referralcode
                        userprofile.save()
                        return json_response({'status':'success','msg':'Referral Code Updated successfully'}, status=200)   
                    except Profiles.DoesNotExist:
                        return json_response({'status':'error','msg':'Invalid User id'}, status=200)   
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User id'
            }, status=400)
        

class UpdateUserBanner(APIView):
    
    """
    Update user profile's banner
    
    @method Post
    @access	private   
    @param integer userId    
    @return	json array
    """
    
    @apikey_required
    @token_required
    def post(self, request, format=None):
        userId = request.POST['userId']
        user = Users.objects.filter(id=userId)
        millis = int(round(time.time() * 1000))
        if user.exists():
            try:
                user = Profiles.objects.get(userid=user)
                
                # Profile Banner Image Create
                bannerImage = request.POST.get('bannerImage',None)
                filename = ''                    
                if bannerImage in [None, '']:
                    filename = ''
                else:                        
                    filename = "banner_%s.jpeg" % str(userId).replace('.','_')                   
                    upload_image_profile(filename,bannerImage,settings.BANNER_URL)
                    make_thumbnil_profile(filename,userId,'banner',settings.BANNER_URL)                   
                    
                user.banner=filename+'?%s' %(millis)
                user.updatedate = datetime.utcnow()
                user.save()
                return json_response({'status':'success','msg': 'User Profile Updated successfully.'},status=200)
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg': 'Invalid User Id'}, status=400)                     
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=400)


class reportAdminAboutUser(APIView):
    
    """
    Report admin about any abused user
    
    @method Post
    @access	private   
    @param integer profileId    
    @return	json array
    """    
    @apikey_required
    @token_required
    def post(self, request, format=None):               
        profileId = request.POST.get('profileId', None)       
        if profileId.isnumeric():
            try:
                profile = Profiles.objects.get(userid=profileId)
                subject="User Report"                           
                admin_email_id = settings.EMAIL_HOST_USER
                fromId = profile.userid.email
                templatePath = os.path.join(settings.BASE_DIR, 'templates/admin/email')
                baseUrl = settings.BASE_URL + settings.STATIC_URL
                message = render_to_string(templatePath+'/userreport.html', {'profile_id': profile.id,'user_id':profile.userid.id,'firstname':profile.firstname,'lastname':profile.firstname,'email':profile.userid.email,'baseUrl':baseUrl})
                sendStatus = sendmail(subject,message,admin_email_id,fromId)
                if sendStatus=='success':
                    return json_response({'status':'success','msg':'Mail sent successfully','sendmail':sendStatus}, status=200)
                else:
                    return json_response({'status':'success','msg':'Mail sent failed','sendmail':sendStatus}, status=200)                 
            except Profiles.DoesNotExist:
                return json_response({'status':'success','msg':'Invalid User'}, status=200)    
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)


class blockUser(APIView):
    
    """
    Block user
    
    @method Post
    @access	private   
    @param integer blockBy
    @param integer blockTo
    @return	json array
    """    
    @apikey_required
    @token_required
    def post(self, request,format=None):
        blockBy = request.POST.get('blockBy', None)
        blockTo = request.POST.get('blockTo', None)
        if blockBy.isnumeric() and blockTo.isnumeric():
            try:
                blockto = Profiles.objects.get(userid=blockTo)
                blockby = Profiles.objects.get(userid=blockBy)  
                try:                
                    block = Userblock.objects.get(profileid=blockby, blockedprofileid=blockto).delete()                   
                    return json_response({'status':'success','result':'Now you are unblock this person.','blockby':blockby.id,'blockto':blockto.id,'isBlock':False}, status=200)                    
                except Userblock.DoesNotExist:                               
                    block = Userblock.objects.create(profileid=blockby, blockedprofileid=blockto, createdate=datetime.utcnow())                   
                    return json_response({'status':'success','result':'Successfully blocked.','blockby':blockby.id,'blockto':blockto.id,'isBlock':True}, status=200)
            except Profiles.DoesNotExist:
                 return json_response({'status':'success','msg':'Invalid User'}, status=200)   
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)
        