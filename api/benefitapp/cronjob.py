from rest_framework.views import APIView
from django.conf import settings
from benefitapp.models import Post,Pushnotification,Users,Profiles
from django.db.models import Q
import vimeo
import json
from django.http import HttpResponse
from benefitapp.utils import makeCustomVideoThumb
from datetime import datetime, timedelta
#from gcm import *
import sendNotifications
#from apns import APNs, Frame, Payload

def updateVideoThumb(request):    
    try:
        time_threshold = datetime.utcnow() - timedelta(minutes=60)
        #postList = Post.objects.filter(~Q(length=''),type='V',thumbnailurl='vimeo_default_0_0.jpeg',createdate__lte=time_threshold)
        postList = Post.objects.filter(~Q(length=''),(Q(thumbnailurl='vimeo_default_0_0.jpeg') | Q(thumbnailurl='')),type='V',createdate__lte=time_threshold)
        if len(postList)>0:
            for pObj in postList:                  
                if pObj.length is not None:
                    try:
                        post = Post.objects.get(id = pObj.id)
                        thumbUrl = getVideoThumb(pObj.length)
                        if thumbUrl != 'default':
                            newVideoThumb = makeCustomVideoThumb(pObj.id,pObj.length,thumbUrl,default='no')
                        else:
                            newVideoThumb = 'vimeo_default_0_0.jpeg'
                        post.thumbnailurl = newVideoThumb
                        post.poststatus = 1
                        post.save()
                        
                        # Update video title and description
                        updateVimeoVideoDetails(pObj.length,post.title,post.description)
                                            
                        # Insert User Video Ready to watch Notification entry into pushnotification table                            
                        actionId = post.id
                        message = 'Your video %s has been added to feed.' %(post.title)
                        try:
                            toProfile = Profiles.objects.get(id=post.profileid.id)
                            notification = Pushnotification.objects.create(message=message,receiverprofileid=toProfile,is_post_read=0,is_push_read=0,is_deliver=0,action_id=actionId,action_type='video_post',senderprofileid=toProfile,status=1,createdate=datetime.utcnow())                               
                        except:                        
                            pass
                    except Post.DoesNotExist:
                        pass
        else:
            return HttpResponse("Empty result")
    except Post.DoesNotExist:
        pass
    return HttpResponse("CronJob")
    
       
def getVideoThumb(video_id):  
    if video_id:
        v = vimeo.VimeoClient(token=settings.VIMEO_TOKEN,)    
        vimeoUrl = '/videos/%s' %int(video_id)                
        json_data = v.get(vimeoUrl)    
        json_input = json.dumps(json_data.json())            
        data  = json.loads(json_input)               
        if len(data)>1:            
            if 'pictures' in data:  #if hasattr(data, 'pictures'):         
                if data['pictures']!=None:
                    vimeoThumb = data['pictures']['sizes'][-1]['link']
                else:
                    vimeoThumb = 'default'
            else:
                vimeoThumb = 'default' #'http://i.vimeocdn.com/video/default_640'         
            
            """
            if ('_' in vimeoThumb) and ('.' in vimeoThumb) and ('x' in vimeoThumb):
                urlParts = vimeoThumb.split('_')
                firstPart = urlParts[0]
                lastPartSplit = urlParts[1].split('.')
                
                widthHeightArr = lastPartSplit[0].split('x')
                width = int(widthHeightArr[0])
                height = int(widthHeightArr[1])
                
                if(height > width) :
                    finalThumb = firstPart + "_612x612.jpg?r=pad"    
                else:
                    finalThumb = vimeoThumb
            else:
                finalThumb = vimeoThumb
            """
                    
            return vimeoThumb
        else:
            return 'http://i.vimeocdn.com/video/default_640'                
    else:
        return 'http://i.vimeocdn.com/video/default_640'


def updateVimeoVideoDetails(video_id,title,description):
    if video_id:        
        v = vimeo.VimeoClient(token=settings.VIMEO_TOKEN,)        
        postdata={'name': title, 'description': description}
        vimeoUrl = '/videos/%s' %int(video_id)
        json_data = v.patch(vimeoUrl,data=postdata)
        return 'Updated Successfully'
   
def userPushNotification(request):
    try:
        pushNotificationList = Pushnotification.objects.filter(is_deliver = 0)
        if len(pushNotificationList)>0:
            for pushObj in pushNotificationList:
                deviceid = pushObj.receiverprofileid.userid.deviceid
                devicetoken = pushObj.receiverprofileid.userid.devicetoken
                if (deviceid and devicetoken):
                    # get notification count  for specific user by userid
                    try:
                        profile = Profiles.objects.get(userid=pushObj.receiverprofileid.userid)
                        try:
                            userNotificationCnt = Pushnotification.objects.filter(is_deliver = 0,receiverprofileid = profile)
                            totalUnreadPush = Pushnotification.objects.filter(is_push_read = 0,receiverprofileid = profile)
                            totalCount = len(totalUnreadPush)
                            
                        except Pushnotification.DoesNotExist:
                            totalCount = 0
                    except Profiles.DoesNotExist:
                        totalCount =0
                    if deviceid=='android':
                        android = sendNotifications.AndroidPushNotifications(api_key="AIzaSyCFkxq5EeWqmcbt5LsEYyxIS2Qf_RXGzhI")
                        status = android.send_push_notification(message = pushObj.message,token_device = devicetoken, unReadMsgCount = totalCount, icon="icon", title="The Benefit")                        
                    else:
                        # cert_filepath = "cert/PushCert.pem"
                        # priv_filepath = "cert/PushKey.pem"
                        # ios = sendNotifications.IOSPushNotifications(privatekey_filepath=priv_filepath,certificate_filepath=cert_filepath,sandbox=True)
                        # status = ios.send_push_notification(message=pushObj.message,token_device=devicetoken, badge = totalCount, unReadMsgCount = totalCount)
                        
                        apns = APNs(use_sandbox=False, cert_file='cert/PushCert.pem', key_file='cert/PushKey.pem')
                        payload = Payload(alert=""+pushObj.message, sound="default", badge=totalCount, custom={'unReadMsgCount':totalCount})
                        status = apns.gateway_server.send_notification(devicetoken, payload)
                        
                        #print(status)                                    
                    updateDeliverStatus = Pushnotification.objects.filter(id = pushObj.id).update(is_deliver = 1)
            return HttpResponse("PushCronJob")
        else:
            return HttpResponse("Empty Result")
    except Pushnotification.DoesNotExist:
        return HttpResponse("Empty Result")
    return HttpResponse("PushCronJob")
