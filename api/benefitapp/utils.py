from __future__ import division
import os, sys
import json
from django.conf import settings
from django.http import HttpResponse
from rest_framework.response import Response
from django.core.mail import send_mail,get_connection, EmailMultiAlternatives,EmailMessage
#from auth.models import Token
from benefitapp.models import Users
import base64
from datetime import datetime
import time
import random
import hashlib
from mimetypes import guess_extension, guess_type
from django.db import connection
import urllib


def json_response(response_dict, status=200):
    connection.close()
    return Response(response_dict, status, None, {'Access-Control-Allow-Origin' : '*', 'Access-Control-Allow-Headers' : 'Content-Type, X-APIKEY, X-AUTHTOKEN', 'Access-Control-Allow-Methods' : 'HEAD, GET, OPTIONS, POST, DELETE'})
    
    #response = HttpResponse(json.dumps(response_dict), content_type="application/json", status=status)
    #response['Access-Control-Allow-Origin'] = '*'
    #response['Access-Control-Allow-Headers'] = 'Content-Type, X-APIKEY, X-AUTHTOKEN'
    #response["Access-Control-Allow-Methods"] = "HEAD, GET, OPTIONS, POST, DELETE"
    #return response


def token_required(func):
    def inner(self,request, *args, **kwargs):
        if request.method == 'OPTIONS':
            return func(self,request, *args, **kwargs)
            
        #auth_header = request.META.get('HTTP_X_AUTHTOKEN', None)
        if request.method == 'POST':
            auth_header = request.POST.get('X-AUTHTOKEN',None)
        else:
            auth_header = request.GET.get('X-AUTHTOKEN',None)
            
        if auth_header:
            try:
                user = Users.objects.get(ssotoken=auth_header,is_active=1)
            except Users.DoesNotExist:
                user = None
            
            if user is not None:
                request.token = auth_header
                return func(self,request, *args, **kwargs)
            else:
                return json_response({'status':'error','msg': 'Sorry, Authentication failed. Seems you logged into other device or your account is deactivated.'}, status=401)
        
        return json_response({'status':'error','msg': 'Sorry, Authentication failed. Seems you logged into other device or your account is deactivated.'}, status=401)

    return inner

def apikey_required(func):
    def inner(self, request,*args, **kwargs):
        if request.method == 'OPTIONS':
            return func(self,request, *args, **kwargs)
        
        #apiKey_header = request.META.get('HTTP_X_APIKEY', None)
        if request.method == 'POST':
            apiKey_header = request.POST.get('X-APIKEY',None)
        else:
            apiKey_header = request.GET.get('X-APIKEY',None)
            
        if apiKey_header:
            if apiKey_header == 'fba59e6508136b60e7bbb35ea44af36c':
                return func(self,request, *args, **kwargs)
            else:
                return json_response({
                    'status':'error',
                    'msg': 'Invalid API Key'
                }, status=401)
        return json_response({
            'status':'error',
            'msg': 'Invalid API Key'
        }, status=401)

    return inner


# send mail
def sendmail(subject,message,recipient,frommail='',page=''):
    if frommail:
        from_email=frommail
    else:
        from_email=settings.EMAIL_HOST_USER
    if page=='bulk':
        msg=EmailMessage(subject, message, from_email, recipient)
    else:
        msg=EmailMessage(subject, message, from_email, [recipient])
    
    msg.content_subtype='html'                                                                                                                                                                           
    send = msg.send()
    if send:
        return 'success'
    else:
        return 'failed'
    

# image thumb creation    
def make_thumbnil(filename,userid,thumb_of,PATH, millis,ext,vimeo='no'):    
    from PIL import Image
    import os
    
    # create thumb directory
    try:
        os.makedirs(settings.MEDIA_ROOT + PATH+'thumbs/')
    except OSError:
        pass
    
    #millis = int(round(time.time() * 1000))
    sizes = [(612, 612),(205, 205),(410, 410)]   
    index = 0
    if os.path.exists(settings.MEDIA_ROOT + PATH+filename):
        for size in sizes:
            try:
                im = Image.open(settings.MEDIA_ROOT + PATH+filename)
                """
                newSize = getImageHeight(im,size)
                if newSize:
                    im.thumbnail(newSize)
                else:
                    im.thumbnail(size)
                """
                if vimeo=='yes':
                    im = cropit(im, size)
                    im.thumbnail(size,Image.ANTIALIAS)
                else:
                    im.thumbnail(size,Image.ANTIALIAS)
                
                #make original image
                if index==0:
                    originalname = "%s_%s_%s%s" % (thumb_of,millis,userid,ext)
                    im.save(settings.MEDIA_ROOT + PATH + originalname, "JPEG",quality=70)                                    
                
                # thumbnil                
                if index==1:
                    thumbname = "small_%s_%s_%s%s" % (thumb_of,millis,userid,ext)
                    im.save(settings.MEDIA_ROOT + PATH+'thumbs/'+thumbname, "JPEG",quality=70)
                else:
                    thumbname = "medium_%s_%s_%s%s" % (thumb_of,millis,userid,ext)        
                    im.save(settings.MEDIA_ROOT + PATH+'thumbs/'+thumbname, "JPEG",quality=70)
                index += 1
            except IOError:
                pass
    else:
        pass


def upload_image(fileToBedelete,fileType,imageDataUrl,PATH,userId,millis,content):
    try:
        os.makedirs(settings.MEDIA_ROOT +PATH)
    except OSError:
        pass
    imageExtension = ['.png','.gif','.jpg','.jpeg','.bmp']
    ext = '.jpeg' #guess_extension(guess_type(fileType)[0])
    if ext=='.jpe':
       ext='.jpg'
    else:
       ext = ext;
    fileName = "%s_%s_%s%s" % (content,millis, str(userId),ext)
    binary_data = decode_base64(imageDataUrl)
    fd = open(settings.MEDIA_ROOT + PATH + fileName, 'wb')
    fd.write(binary_data)
    fd.close()
    
    if ext in imageExtension:        
        make_thumbnil(fileName,userId,content,PATH,millis,ext)
        
    if fileToBedelete:
        unlinkFile(fileToBedelete,PATH)   #unlinkFile(ext,fileToBedelete,imageExtension,PATH)
        
    return fileName;


def unlinkFile(fileToBedelete,PATH):    
    folder_path = settings.MEDIA_ROOT + PATH
    file_object_path = os.path.join(folder_path, fileToBedelete)    
    if os.path.isfile(file_object_path):
        os.unlink(settings.MEDIA_ROOT + PATH+'/'+fileToBedelete)
        smallThumFile = 'small_'+fileToBedelete
        mediumThumFile = 'medium_'+fileToBedelete
        if os.path.exists(settings.MEDIA_ROOT + PATH+'thumbs/'+smallThumFile):
            os.unlink(settings.MEDIA_ROOT + PATH+'thumbs/'+smallThumFile)
        if os.path.exists(settings.MEDIA_ROOT + PATH+'thumbs/'+mediumThumFile):
            os.unlink(settings.MEDIA_ROOT + PATH+'thumbs/'+mediumThumFile)
"""
#def unlinkFile(ext,fileToBedelete,imageExtension,PATH):

def unlinkFile(ext,fileToBedelete,PATH):
    imageExtension = ['.png','.gif','.jpg','.jpeg','.bmp']
    folder_path = settings.MEDIA_ROOT + PATH
    file_object_path = os.path.join(folder_path, fileToBedelete)    
    if os.path.isfile(file_object_path):
        os.unlink(settings.MEDIA_ROOT + PATH+'/'+fileToBedelete)
        if ext in imageExtension:
            smallThumFile = 'small_'+fileToBedelete
            mediumThumFile = 'medium_'+fileToBedelete
            os.unlink(settings.MEDIA_ROOT + PATH+'thumbs/'+smallThumFile)
            os.unlink(settings.MEDIA_ROOT + PATH+'thumbs/'+mediumThumFile)

"""        

def decode_base64(data):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += b'='* missing_padding
    return base64.decodestring(data)

def getDate_OLD(date1):
    if date1:
        date_format = "%m-%d-%Y %H:%M:%S"
                 
        
        d1 = datetime.strftime(date1, "%m-%d-%Y %H:%M:%S")
        d2 = datetime.strftime(datetime.utcnow(), "%m-%d-%Y %H:%M:%S")
        
        #convert string to actual date and time
        time1  = datetime.strptime(d1, date_format)
        time2  = datetime.strptime(d2, date_format)
         
        #find the difference between two dates
        diff = time2 - time1
                     
        #print days
        days = diff.days
        daysStr =  (str(days) + ' D')
        
        # print hours        
        hours = int((diff.seconds) / 3600)  
        hoursStr = (str(hours) + ' H')
        
        # minutes
        minutes = int((diff.seconds) / 60)
        minutesStr = (str(minutes) + ' M')
                
        if days>0:
            time = daysStr       
        else:
            if minutes<1:
                time = 'Just now'
            elif minutes<60:
                time = minutesStr
            else:
                time = hoursStr            
        return time    #return d1+'--'+d2+'---'+str(time1)+'---'+str(time2)+'---'+str(diff)



# image thumb creation    
def make_thumbnil_profile(filename,userid,thumb_of,PATH):    
    from PIL import Image
    import os
    
    # create thumb directory
    try:
        os.makedirs(settings.MEDIA_ROOT + PATH+'thumbs/')
    except OSError:
        pass
    
    #millis = int(round(time.time() * 1000))
    
    if thumb_of=='banner':
        sizes = [(612, 612),(205, 170),(410, 170)]
    else:
        sizes = [(612, 612),(410, 410),(80, 80)]
    
    #sizes = [(320, 320),(640, 400)]
    index = 0
    if os.path.exists(settings.MEDIA_ROOT + PATH+filename):
        for size in sizes:
            try:
                im = Image.open(settings.MEDIA_ROOT + PATH+filename)
                """
                newSize = getImageHeight(im,size)
                if newSize:
                    im.thumbnail(newSize)
                else:
                    im.thumbnail(size)
                """
                im.thumbnail(size,Image.ANTIALIAS)
                
                #make original image
                if index==0:
                    originalname = "%s_%s.jpeg" % (thumb_of,userid)
                    im.save(settings.MEDIA_ROOT + PATH + originalname, "JPEG",quality=70)
                
                #thumbnil    
                if index==1:
                    thumbname = "small_%s_%s.jpeg" % (thumb_of,userid)
                    im.save(settings.MEDIA_ROOT + PATH+'thumbs/'+thumbname, "JPEG",quality=70)
                else:
                    thumbname = "medium_%s_%s.jpeg" % (thumb_of,userid)        
                    im.save(settings.MEDIA_ROOT + PATH+'thumbs/'+thumbname, "JPEG",quality=70)
                index += 1
            except IOError:
                pass
    else:
        pass


def getImageHeight(im,arraysize):
    imgsize = im.size
    imgwidth = imgsize[0]
    imgheight = imgsize[1]
    desired_width = arraysize[0]
    desired_height = int(imgheight*(desired_width / imgwidth))               
    
    if imgwidth<=desired_width:
        newSize = (imgwidth,desired_height)        
    else:
        newSize = (desired_width,desired_height)

    return newSize


def upload_image_profile(fileName,imageDataUrl,PATH):
    # create image directory
    try:
        os.makedirs(settings.MEDIA_ROOT +PATH)
    except OSError:
        pass
    binary_data = decode_base64(imageDataUrl)
    fd = open(settings.MEDIA_ROOT + PATH + fileName, 'wb')
    fd.write(binary_data)
    fd.close()        


def documentsUpload(filename,millis,PATH,userId,fileToBedelete):        
    # Rename file with new name    
    filenamesaved = filename.name
    ext = guess_extension(guess_type(filenamesaved)[0])
    if ext=='.jpe':
       ext='.jpg'
    else:
       ext = ext;
    filenamestr = filenamesaved.split(ext)
    filenamesaved = "%s_%s_%s_%s%s" % (filenamestr[0],'document',millis,userId,ext)
    
    if fileToBedelete:
        folder_path = settings.MEDIA_ROOT + PATH
        file_object_path = os.path.join(folder_path, fileToBedelete)    
        if os.path.isfile(file_object_path):
            os.unlink(settings.MEDIA_ROOT + PATH+'/'+fileToBedelete)
    
    dest_file = open(settings.MEDIA_ROOT+PATH+ str(filenamesaved), 'wb+')
    path = settings.MEDIA_ROOT+PATH+ str(filename)
    for chunk in  filename.chunks():
        dest_file.write(chunk)
    dest_file.close()
    
    return filenamesaved

def ssoTokenGenerator(lengthval):
    alphabet = "abcdefghijklmnopqrstuvwxyz0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    pw_length = lengthval
    mypw = ""

    for i in range(lengthval):
        next_index = random.randrange(len(alphabet))
        mypw = mypw + alphabet[next_index]
    
    m = hashlib.md5()
    m.update(mypw)
    if pw_length == 32:
        return m.hexdigest()
    else:
        return mypw
    
def chekPrice(price):
    try:
        int(price)==int
        return True
    except ValueError:
        try:
            float(price)==float
            return True
        except ValueError:
            return False


def getDateFormat(date,type):
    if date:
        if type==1:
            date_format = "%m/%d/%y at %I:%M%P"
        elif type==2:
            date_format = "%b.%dth at %I:%M%p"
        else:
            date_format = " %m/%d/%y at %I:%M%P"
    
        return datetime.strftime(date, date_format)


def getDate(givendate):
    date_format = "%Y-%m-%d %H:%M:%S"
    if givendate:
        return datetime.strftime(givendate,date_format)
    else:
        return datetime.strftime(datetime.utcnow(),date_format)
    

def makeCustomVideoThumb(post_id,video_id,thumbUrl,default='no'):
    if video_id and thumbUrl:
        url = thumbUrl        
        uopen = urllib.urlopen(url)
        stream = uopen.read()
        if default=='yes':
            content = 'vimeo_default'
            post_id = video_id = 0
            fileName = "vimeo_default_0_0.jpeg"
        else:
            content = 'vimeo'  
            fileName = "%s_%s_%s.jpeg" % (content,str(video_id), str(post_id))   
        file = open(settings.MEDIA_ROOT+settings.VIMEO_URL+fileName,'w')
        file.write(stream)
        file.close()
        
        make_thumbnil(fileName,post_id,content,settings.VIMEO_URL,video_id,'.jpeg','yes')
        
        return fileName
    else:
        fileName = "vimeo_default_0_0.jpeg"
        return fileName
    
    
def boxParamsCenter(width, height):
    """
    Calculate the box parameters for cropping the center of an image based
    on the image width and image height
    """
    if isLandscape(width, height):
        upper_x = int((width/2) - (height/2))
        upper_y = 0
        lower_x = int((width/2) + (height/2))
        lower_y = height
        return upper_x, upper_y, lower_x, lower_y
    else:
        upper_x = 0
        upper_y = int((height/2) - (width/2))
        lower_x = width
        lower_y = int((height/2) + (width/2))
        return upper_x, upper_y, lower_x, lower_y
 
def isLandscape(width, height):
    """
    Takes the image width and height and returns if the image is in landscape
    or portrait mode.
    """
    if width >= height:
        return True
    else:
        return False
 
def cropit(img, size):
    """
    Performs the cropping of the input image to generate a square thumbnail.
    It calculates the box parameters required by the PIL cropping method, crops
    the input image and returns the cropped square.
    """
    img_width, img_height = size
    upper_x, upper_y, lower_x, lower_y = boxParamsCenter(img.size[0], img.size[1])
    box = (upper_x, upper_y, lower_x, lower_y)
    region = img.crop(box)
    return region

        