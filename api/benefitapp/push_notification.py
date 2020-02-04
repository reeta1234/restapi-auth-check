from __future__ import unicode_literals
from django.conf import settings
from rest_framework.views import APIView
from rest_framework import status
from benefitapp.models import Users,Profiles,Pushnotification
from django.db import IntegrityError
from django.db import connection
from django.core import serializers
from django.db.models import Q
from benefitapp.utils import json_response, token_required, apikey_required, getDate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import json
#from apns import APNs, Frame, Payload

class pushTest(APIView):
    def get(self, request, format=None):
        deviceId = request.POST.get('deviceId', None)
        deviceType = request.POST.get('deviceType', None)
        
         
        apns = APNs(use_sandbox=False, cert_file='cert/PushCert.pem', key_file='cert/PushKey.pem')
        # Send a notification
        token_hex = 'ed11f65b41ecbca11f36106e5e01abe9b1d8acf821a6a8dc6fc9fcbe0d5902c0'
        payload = Payload(alert="New PUSH World!", sound="default", badge=500)
        status = apns.gateway_server.send_notification(token_hex, payload)
        
        return json_response({'status':'success','msg': 'PushNotification Test'})
    
class getPushNotificationCount(APIView):
    """
    Return Count of UnRead Push for a particular user
    
    @method Post
    @access	private
    @param	string userId
    @return	json array
    """
        
    @apikey_required
    @token_required
    def post(self, request, format=None):
        userId = request.POST.get('userId', None)
        
        if userId and userId is not None:
            try:
                Profile = Profiles.objects.get(userid=userId)     
                try:
                    #cursor = connection.cursor()                
                    #cursor.execute("SELECT COUNT(id) from  pushnotification where ReceiverProfileId='"+ userId +"' AND isPushRead = '0' ")
                    #cursorResult = cursor.fetchone()
                    pushNotificationCount = Pushnotification.objects.filter(receiverprofileid=Profile,is_push_read=0)
                    if len(pushNotificationCount)>0:
                        return json_response({'status':'success','msg': 'PushNotification Count', 'count' : len(pushNotificationCount)})
                    else:
                        return json_response({'status':'success','msg': 'PushNotification Count Exc', 'count' : 0})
                    return json_response({'status':'success','msg': 'PushNotification Count', 'count' : cursorResult[0]})
                except Pushnotification.DoesNotExist:
                    return json_response({'status':'success','msg': 'PushNotification Count Exc', 'count' : 1110})
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg': 'Invalid User Id'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return json_response({'status':'error','msg': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)


class getPushNotificationList(APIView):
    """
    Return List of Push for a particular user
    
    @method Post
    @access	private
    @param	string userId
    @return	json array
    """
        
    @apikey_required
    @token_required
    def post(self, request, format=None):
        userId = int(request.POST.get('userId', None))
        page = int (request.GET.get('page', 1))  
        recordsPerPage = int (request.GET.get('recordsPerPage', 10))
        markRead = request.POST.get('markRead', False)
        if userId and userId is not None:
            try:
                Profile = Profiles.objects.get(userid=userId)     
                try:
                    pushMessages = Pushnotification.objects.filter(receiverprofileid=Profile).order_by('-createdate')
                    paginator = Paginator(pushMessages, recordsPerPage)
                    
                    try:
                        pushMessagesObj = paginator.page(page)
                    except PageNotAnInteger:                       
                        pushMessagesObj = paginator.page(1)
                    except EmptyPage:                       
                        pushMessagesObj = paginator.page(paginator.num_pages)
                    
                    
                    messageList = []
                    for msg in pushMessagesObj:
                        if msg.senderprofileid>0:
                            senderName = msg.senderprofileid.firstname
                            if msg.senderprofileid.profilephoto:
                                senderPhoto = settings.BASE_URL + settings.STATIC_URL+ settings.MEDIA_URL + msg.senderprofileid.profilephoto
                            else:
                                senderPhoto = "assets/vendor/theme/img/avatar.png";
                        else:
                            senderName = senderPhoto =''
                            
                        messageList.append({
                                'id'            :   msg.id,
                                'message'       :   msg.message,
                                #'profileid'    :   msg.profileid.id,
                                'userName'      :   senderName,
                                'companyname'   :   msg.senderprofileid.companyname,
                                'userPhoto'     :   senderPhoto,
                                'isPostRead'    :   msg.is_post_read,
                                'isPushRead'    :   msg.is_push_read,
                                'isDeliver'     :   msg.is_deliver,
                                'actionId'      :   msg.action_id,
                                'actionType'    :   msg.action_type,
                                'createdDate'   : getDate(msg.createdate)
                        })
                    
                    if markRead:
                        Pushnotification.objects.filter(receiverprofileid=Profile).update(is_push_read=1)
                    
                    return json_response({'status':'success','msg': 'PushNotification List', 'result' : json.dumps(messageList), 'total':len(pushMessages)})
                except Pushnotification.DoesNotExist:
                    return json_response({'status':'success','msg': 'PushNotification List Exc', 'result' : json.dumps([])})
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg': 'Invalid User'}, status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return json_response({'status':'error','msg': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)

class markAsRead(APIView):
    """
    Mark Read Status for Push and Post depends on requested type
    
    @method Post
    @access	private
    @param	string userId
    @param	string pushId
    @param	string type (post or push)
    @return	json array
    """
        
    @apikey_required
    @token_required
    def post(self, request, format=None):
        userId = request.POST.get('userId', None)
        pushId = request.POST.get('pushId', None)
        markType = request.POST.get('markType', None)
        
        if (userId and userId is not None) and (pushId and pushId is not None) and (markType == "push" or markType == "post"):
            try:
                Profile = Profiles.objects.get(userid=userId) 
                try:
                    if (markType == "push") :
                        Pushnotification.objects.filter(id=pushId,receiverprofileid=Profile).update(is_push_read=1)
                    else:
                        Pushnotification.objects.filter(id=pushId,receiverprofileid=Profile).update(is_post_read=1)
                        
                    return json_response({'status':'success','msg': 'PushNotification Marked as Read'})
                except Pushnotification.DoesNotExist:
                    return json_response({'status':'error','msg': 'Invalid notification.'})
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg': 'Invalid user.'})
        else:
            return json_response({'status':'error','msg': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)
