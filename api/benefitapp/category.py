from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings
from benefitapp.models import Category,Users,Profiles,Followings,Post,Comments,Postlikes,Postratings,Favorites,Products,Albums,Postcategory,Imagetag,Poststatistics,Commentlikes,Userblock,Productstatistics,Productcategory,Productimages,Postsharings,Pushnotification,Producttag
from django.db import IntegrityError
from django.core import serializers
from django.db.models import Q
from benefitapp.utils import json_response, token_required, apikey_required,sendmail,decode_base64,make_thumbnil,upload_image,getDate,documentsUpload,chekPrice,unlinkFile,makeCustomVideoThumb
from datetime import datetime
from django.db import connection
import vimeo
import json
import base64
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
import os

    
class category(APIView):
    
    """
    Insert category into master category table
    
    @method POST
    @access	private
    @param	string name    
    @param	string description    
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):
        name = request.POST.get('name', None)
        description = request.POST.get('description', None)
        
        if name:
                try:
                    category = Category.objects.get(name=name)
                    return json_response({'status':'error','msg': 'Category name already exists,please choose another name.'}, status=status.HTTP_400_BAD_REQUEST)
                except Category.DoesNotExist:
                    category = Category.objects.create(name=name, description=description,create_date = datetime.utcnow())
                    return json_response({'status':'success','msg':'category created successfully','id':category.id}, status=200)                       
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Data'
            }, status=400)
        

class getCategoryList(APIView):
    
    """
    Get category list
    
    @method POST
    @access	private
    @param	None    
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request, format=None):
        try:
            category = Category.objects.all()
            catdata = serializers.serialize('json', category)
            return json_response({'status':'success','result': catdata}, status=200)
        except Category.DoesNotExist:          
            return json_response({'status':'error','msg':'No records found','result':'Record not found'}, status=200)  
                                                

class viewMyReferalCode(APIView):
    
    """
    View my referal code
    
    @method GET
    @access	private
    @param	integer user_id    
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id,format=None):        
        if user_id:
            try:
                user = Profiles.objects.get(userid=user_id)                    
                return json_response({'status':'success','result':
                    {'id':user.id,'referalCode':user.referalcode}
                }, status=200)
            except Profiles.DoesNotExist:
                 return json_response({'status':'success','result':'Invalid User'
                }, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Data'
            }, status=400)
        

class followProducer(APIView):
    
    """
    Follow producer
    
    @method POST
    @access	private
    @param	integer followBy
    @param	integer followTo  
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request,format=None):
        followBy = request.POST.get('followBy', None)
        followTo = request.POST.get('followTo', None)
        if followBy.isnumeric() and followTo.isnumeric():
            if followBy != followTo:
                try:
                    followto = Profiles.objects.get(userid=followTo)
                    followby = Profiles.objects.get(userid=followBy)  
                    try:                
                        follower = Followings.objects.get(profileid=followby, followingprofileid=followto).delete()                   
                        return json_response({'status':'success','result':'Now you are  unfollowing this person.','isFollow':False}, status=200)  
                    except Followings.DoesNotExist:                               
                        follower = Followings.objects.create(profileid=followby, followingprofileid=followto, createdate=datetime.utcnow())
                        
                        if follower:
                            # Insert User follower Notification entry into pushnotification table                            
                            actionId = followby.userid.id
                            if followby.companyname:
                                profileName = followby.companyname
                            else:
                                profileName = followby.firstname
                            message = '%s started following you.' %(profileName)
                            try:
                                if followto.id!=followby.id:
                                    notification = Pushnotification.objects.create(message=message,receiverprofileid=followto,is_post_read=0,is_push_read=0,is_deliver=0,action_id=actionId,action_type='follow',senderprofileid=followby,status=1,createdate=datetime.utcnow())
                                else:
                                    pass
                            except:                        
                                pass
                        
                        return json_response({'status':'success','followby':followby.id,'followto':followto.id,'isFollow':True}, status=200)
                except Profiles.DoesNotExist:
                     return json_response({'status':'success','msg':'Invalid User'}, status=200)
            else:
                return json_response({'status':'error','msg':"You can't follow to yourself"}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)


class unfollowProducer(APIView):
    
    """
    Unfollow producer
    
    @method POST
    @access	private
    @param	integer followBy
    @param	integer followTo  
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):
        followBy = request.POST.get('followBy', None)
        followTo = request.POST.get('followTo', None)  
        if followBy.isnumeric() and followTo.isnumeric():
            try:
                followby = Profiles.objects.get(userid=followBy)  
                followto = Profiles.objects.get(userid=followTo)            
                follower = Followings.objects.filter(profileid=followby, followingprofileid=followto).delete()                  
                return json_response({'status':'success','followby':followby.id,'followto':followto.id,'msg':'deleted'}, status=200)
            except Profiles.DoesNotExist:
                 return json_response({'status':'success','msg':'Invalid User'}, status=200)     
        else:
            return json_response({
                'status':'error',
                 'msg': 'Invalid User Id'
            }, status=400)


class addPost(APIView):
    
    """
    Add / Edit post
    
    @method POST
    @access	private
    @param	integer userId
    @param	string title
    @param	string description    
    @param	string scope
    @param	string type    
    @param	string posturl
    @param	string thumbnailurl    
    @param	string length
    @param	string fileType    
    @param	string categoryId
    @param	string tagText    
    @return	json array
    """
    from rest_framework.parsers import FormParser,MultiPartParser,FileUploadParser
    parser_classes = (FormParser, MultiPartParser,FileUploadParser,)
    @apikey_required
    @token_required    
    def post(self, request, format=None):
        userId = request.POST.get('userId', None)
        title = request.POST.get('title', None)
        description = request.POST.get('description', None)
        scope = request.POST.get('scope', None)
        type = request.POST.get('type', 'T-Text')
        posturl = request.POST.get('posturl', None)
        thumbnailurl = request.POST.get('thumbnailurl', None)
        length = request.POST.get('length', None)
        fileType = request.POST.get('fileType', "data:image/png;base64,")        
        categoryString = request.POST.get('categoryId', None)
        tagText = request.POST.get('tagText', None)
        if categoryString:
            category = categoryString.split(',')
        else:
            category = []
        
        if tagText:
            tagList = tagText.split(',')
        else:
            tagList = []
            
        postId = request.POST.get('postId', None)        
        if userId and userId.isnumeric():            
                try:
                    profile = Profiles.objects.get(userid=userId)
                    #categoryId = Category.objects.get(id=1)
                                                                    
                    if scope == 'false':
                        scope = 0
                    elif scope == 'true': 
                        scope = 1
                    else:
                        scope = 0
                    
                    filename = ''
                    millis = int(round(time.time() * 1000))
                    fileToBedelete = ''                                              
                    if postId:
                        if category:
                            for pkid in category:                                 
                                if pkid.isnumeric():
                                    cId = int(pkid)
                                else:
                                    return json_response({'status':'error','msg':'Invalid category'})
                        try:
                            post = Post.objects.get(id=postId,profileid=profile)
                            
                            # file upload
                            if type=='V':
                                if length:                                    
                                    filename = makeCustomVideoThumb(postId,length,"http://i.vimeocdn.com/video/default_640",'yes')
                                else:
                                    filename = ''
                            elif type=='D':
                                if u'file' in request.FILES:
                                    fileToBedelete = post.thumbnailurl
                                    filename = documentsUpload(request.FILES['file'],millis,settings.POST_MEDIA_URL,userId,fileToBedelete)
                                else:
                                    filename = ''
                            else:
                                if thumbnailurl in [None, '']:
                                    filename = ''
                                else:                                                            
                                    fileToBedelete = post.thumbnailurl
                                    filename = upload_image(fileToBedelete,fileType,thumbnailurl,settings.POST_MEDIA_URL,userId,millis,content='post') 
                                                                                                        
                            
                            if title:
                                post.title = title
                            if description:
                                post.description=description
                            if scope:
                                post.scope=scope
                            if type:
                                post.type = type
                            if posturl:
                                post.posturl = posturl
                            if filename:
                                post.thumbnailurl=filename
                            if length:
                                post.length=length
                            #if categoryId:
                                #post.categoryid = categoryId
                            post.createdate=datetime.utcnow()
                            post.save()
                            
                            # Update Post Category
                            if category:
                                Postcategory.objects.filter(postid=post).delete()
                                for pkid in category: 
                                    cId = int(pkid)
                                    try:                                        
                                        catid = Category.objects.get(id=cId)
                                        Postcategory.objects.create(categoryid = catid,postid = post,createdate = datetime.utcnow())
                                    except Category.DoesNotExist:
                                        pass
                            
                            # Reopen Tag which was removed from benefit
                            
                            # Update Image tag
                            if tagText:
                                Imagetag.objects.filter(postid=post).delete()
                                for tag in tagList:                                     
                                    Imagetag.objects.create(tagtext = tag,postid = post,createdate = datetime.utcnow())                            
                                    
                            return json_response({'status':'success','msg':'Post updated successfully','scope':scope}, status=200)
                        except Post.DoesNotExist:
                            return json_response({'status':'error','msg':'Invalid post id'},status=200)                        
                    else:                        
                        #if title: # Removed title validation while post add on 29th march
                            if category:
                                for pkid in category:                                 
                                    if pkid.isnumeric():
                                        cId = int(pkid)
                                    else:
                                        return json_response({'status':'error','msg':'Invalid category'})
                            # file upload
                            if type=='V':
                                poststatus = 0
                                if length:                                    
                                    filename = makeCustomVideoThumb(0,length,"http://i.vimeocdn.com/video/default_640",'yes')
                                else:
                                    filename = ''
                            elif type=='D':
                                poststatus = 1
                                if u'file' in request.FILES:                                    
                                    fileToBedelete = ''
                                    filename = documentsUpload(request.FILES['file'],millis,settings.POST_MEDIA_URL,userId,fileToBedelete)
                                else:
                                    filename = ''
                            else:
                                poststatus = 1
                                if thumbnailurl in [None, '']:
                                    filename = ''
                                else:                                                            
                                    fileToBedelete = ''
                                    filename = upload_image(fileToBedelete,fileType,thumbnailurl,settings.POST_MEDIA_URL,userId,millis,content='post')
                                    
                            post = Post.objects.create(profileid=profile,title=title, description=description,scope=scope,type=type,posturl=posturl,thumbnailurl=filename,poststatus=poststatus,length=length,createdate=datetime.utcnow()) #categoryid=categoryId
                            recentPost = Post.objects.filter(profileid = profile).order_by('-id')[0]
                            if category:
                                for pkid in category: 
                                    cId = int(pkid)
                                    try:
                                        catid = Category.objects.get(id=cId)
                                        Postcategory.objects.create(categoryid = catid,postid = recentPost,createdate = datetime.utcnow())
                                    except Category.DoesNotExist:
                                        pass
                            
                            # Reopen Tag which was removed from benefit
                            
                            # Insert Image Tag
                            if tagText:
                               for tag in tagList:                                     
                                    Imagetag.objects.create(tagtext = tag,postid = recentPost,createdate = datetime.utcnow())
                            
                            
                            return json_response({'status':'success','msg':'Post added successfully','scope':scope,'recentPost':recentPost.id}, status=200)
                        #else:
                            #return json_response({'status':'error','msg':'Post title is required'}, status=200)
                except Profiles.DoesNotExist:
                     return json_response({'status':'error','msg':'Invalid User'}, status=200)           
                
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=400)


class putComment(APIView):
    
    """
    Put coment on post and video
    
    @method POST
    @access	private
    @param	integer postId
    @param	integer profileId
    @param	integer ParentCommentId        
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):        
        postId = request.POST.get('postId', None)
        profileId = request.POST.get('profileId', None)
        comment = request.POST.get('comment', None)
        ParentCommentId = request.POST.get('ParentCommentId', None)       
        if profileId.isnumeric() and postId.isnumeric():
            try:
                profile = Profiles.objects.get(userid=profileId)
                try:
                    post = Post.objects.get(id=postId)
                    if ParentCommentId:
                        ParentCommentId = ParentCommentId
                    else:
                        ParentCommentId = 0
                    comment = Comments.objects.create(postid=post,profileid=profile,comment=comment,parentcommentid=ParentCommentId,createdate=datetime.utcnow())
                    
                    if comment:                    
                        # Insert User Comment Notification entry into pushnotification table                    
                        actionId = post.id
                        if profile.companyname:
                            profileName = profile.companyname
                        else:
                            profileName = profile.firstname
                        message = '%s commented on your post.' %(profileName)
                        try:
                            toProfile = Profiles.objects.get(id=post.profileid.id)
                            if toProfile.id!=profile.id:
                                notification = Pushnotification.objects.create(message=message,receiverprofileid=toProfile,is_post_read=0,is_push_read=0,is_deliver=0,action_id=actionId,action_type='comment_post',senderprofileid=profile,status=1,createdate=datetime.utcnow())
                            else:
                                pass
                        except:                        
                            pass
                    return json_response({'status':'success','msg':'Comment added successfully'}, status=200)
                except Post.DoesNotExist:
                     return json_response({'status':'success','msg':'Invalid Post'}, status=200)        
            except Profiles.DoesNotExist:        
                return json_response({'status':'success','msg':'Invalid User'}, status=200)                           
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)


class postLike(APIView):
    
    """
    Post like content
    
    @method POST
    @access	private
    @param	integer postId
    @param	integer profileId   
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):        
        postId = request.POST.get('postId', None)
        profileId = request.POST.get('profileId', None)        
        if profileId.isnumeric() and postId.isnumeric():
            try:
                profile = Profiles.objects.get(userid=profileId)
                try:
                    post = Post.objects.get(id=postId)
                    postlike = Postlikes.objects.filter(postid=post,profileid=profile)
                    if len(postlike)>0:
                        postlike = Postlikes.objects.filter(postid=post,profileid=profile).delete()
                        totalLikes = Postlikes.objects.filter(postid=post)
                        try:
                            # Post Statistics                    
                            poststatistics = Poststatistics.objects.get(postid=post)
                            poststatistics.totallike += 1
                            poststatistics.save()
                        except Poststatistics.DoesNotExist:
                            pass
                        return json_response({'status':'success','msg':'Removed like','totalLikes':len(totalLikes)}, status=200)
                    else:
                        postlike = Postlikes.objects.create(postid=post,profileid=profile,createdate=datetime.utcnow())
                        
                        if postlike:
                            # Insert User Post Like Notification entry into pushnotification table                            
                            actionId = post.id
                            if profile.companyname:
                                profileName = profile.companyname
                            else:
                                profileName = profile.firstname
                            message = '%s liked your post.' %(profileName)
                            try:
                                toProfile = Profiles.objects.get(id=post.profileid.id)
                                if toProfile.id!=profile.id:
                                    notification = Pushnotification.objects.create(message=message,receiverprofileid=toProfile,is_post_read=0,is_push_read=0,is_deliver=0,action_id=actionId,action_type='like_post',senderprofileid=profile,status=1,createdate=datetime.utcnow())
                                else:
                                    pass
                            except:                        
                                pass
                    
                        totalLikes = Postlikes.objects.filter(postid=post)                        
                        # Post Statistics
                        try:
                            poststatistics = Poststatistics.objects.get(postid=post)
                            poststatistics.totallike += 1
                            poststatistics.save()
                        except Poststatistics.DoesNotExist:
                            Poststatistics.objects.create(postid=post,totallike=1)
                        return json_response({'status':'success','msg':'added successfully','totalLikes':len(totalLikes)}, status=200)
                except Post.DoesNotExist:
                    return json_response({'status':'success','msg':'Invalid Post'}, status=200)    
            except Profiles.DoesNotExist:
                return json_response({'status':'success','msg':'Invalid User'}, status=200)    
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)

    
class ratePost(APIView):
    
    """
    Rate Post/video
    
    @method POST
    @access	private
    @param	integer postId
    @param	integer profileId
    @param	float rating        
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):        
        postId = request.POST.get('postId', None)
        profileId = request.POST.get('profileId', None)
        rating = request.POST.get('rating', None)       
        if profileId.isnumeric() and postId.isnumeric():
            try:
                profile = Profiles.objects.get(userid=profileId)
                try:                    
                    ratePost = Postratings.objects.get(postid=postId,profileid=profileId)                    
                    ratePost.rating = rating
                    createdate=datetime.utcnow()
                    ratePost.save()                    
                except Postratings.DoesNotExist:                   
                    post = Post.objects.get(id=postId)
                    postrating = Postratings.objects.create(postid=post,profileid=profile,rating=rating,createdate=datetime.utcnow())
                
                # Post Statistics  
                try:                                        
                    poststatistics = Poststatistics.objects.get(postid=postId)
                    poststatistics.totalrating += 1
                    poststatistics.save()
                except Poststatistics.DoesNotExist:
                    pass
                    
                # count total rating    
                try:
                    totalRating = Postratings.objects.filter(postid=postId)
                except Postratings.DoesNotExist:
                    totalRating =0
                return json_response({'status':'success','msg':'added successfully','totalRating':len(totalRating)}, status=200)
            except Profiles.DoesNotExist:
                return json_response({'status':'success','msg':'Invalid User'}, status=200) 
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User id or Post Id'
            }, status=200)


class deletePost(APIView):
    
    """
    Delete feed content
    
    @method GET
    @access	private    
    @param	integer user_id
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self,request,user_id,format=None):                    
        try:
            #user = Users.objects.get(id=user_id)            
            profile = Profiles.objects.get(userid=user_id)
            postId = request.GET.get('postId', None)           
            try:
                post = Post.objects.get(id=postId) #,profileid=user.id
                if post:
                    comment = Comments.objects.filter(postid=post).delete()
                    favorites = Favorites.objects.filter(postid=post).delete()
                    postlikes = Postlikes.objects.filter(postid=post).delete()
                    postratings = Postratings.objects.filter(postid=post).delete()
                    postsharings = Postsharings.objects.filter(postid=post).delete()
                    poststatistics = Poststatistics.objects.filter(postid=post).delete()
                    postcategory = Postcategory.objects.filter(postid=post).delete()
                    imagetag = Imagetag.objects.filter(postid=post).delete()
                    
                    if post.thumbnailurl:                                    
                        fileToBedelete = post.thumbnailurl
                        unlinkFile(fileToBedelete,settings.POST_MEDIA_URL)
                    else:
                        pass                 
                    post = Post.objects.get(id=postId,profileid=profile.id).delete()
                return json_response({'status':'success','msg':'Post deleted successfully'},status=200)
            except Post.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid Post id'},status=200)            
            #return json_response({'status':'error','msg':'Invalid Post id','dd':profile.id,'post':postId},status=200)         
        except Users.DoesNotExist:
            return json_response({'status':'error','msg':'Invalid User Id'}, status=200)



class getPostDetail(APIView):
    
    """
    Get post detail by id
    
    @method GET
    @access	private    
    @param	integer post_id
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,post_id,format=None):       
        if post_id.isnumeric():
            try:               
                post = Post.objects.get(id=post_id)
                mainUrl = settings.BASE_URL + settings.STATIC_URL+ settings.POST_MEDIA_URL
                thumburl = mainUrl+'thumbs/'                
                if post.thumbnailurl and post.type=='I':
                    small_thumb = thumburl+'small_'+post.thumbnailurl
                    medium_thumb = thumburl+'medium_'+post.thumbnailurl
                    original_img = mainUrl+post.thumbnailurl
                elif post.thumbnailurl and post.type=='V':
                    mainUrl1 = settings.BASE_URL + settings.STATIC_URL+ settings.VIMEO_URL
                    thumburl1 = mainUrl1+'thumbs/'                
                    small_thumb = thumburl1+'small_'+post.thumbnailurl
                    medium_thumb = thumburl1+'medium_'+post.thumbnailurl
                    original_img = mainUrl1+post.thumbnailurl
                elif post.thumbnailurl and post.type=='D':
                    small_thumb = mainUrl+post.thumbnailurl
                    medium_thumb = mainUrl+post.thumbnailurl
                    original_img = mainUrl+post.thumbnailurl
                else:
                    original_img = small_thumb = medium_thumb = ''
                
                # CategoryList
                try:
                    cat_list = []
                    categorylist = Postcategory.objects.filter(postid=post)
                    for catObj in categorylist:
                        cat_list.append(catObj.categoryid.id)                    
                    cat_id_in = ','.join(map(str, cat_list))
                except Postcategory.DoesNotExist:
                    cat_id_in = ''
                
                # Reopen remove Tags from benefit
                
                # TagList               
                try:
                    tag_list = []
                    tagList = Imagetag.objects.filter(postid=post)
                    for tagObj in tagList:
                        tag_list.append(tagObj.tagtext)                    
                    tag_id_in = ','.join(map(str, tag_list))
                except Imagetag.DoesNotExist:
                    tag_id_in = ''
                
                    
                try:
                    poststatistics = Poststatistics.objects.get(postid=post)                    
                    poststatistics.totalview += 1                                    
                    poststatistics.save()                    
                except Poststatistics.DoesNotExist:
                    Poststatistics.objects.create(postid=post,totalview=1)        
                
                return json_response({'status':'success','result':{'id':post.id,'title':post.title,'description':post.description,'scope' : post.scope, 'type' : post.type,
                                    'profileid' : post.profileid.userid.id,'category':cat_id_in,'small_thumb':small_thumb,'medium_thumb':medium_thumb,'original_img':original_img,'tagList':tag_id_in}}, status=200)
            except Post.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid Post'}, status=200) 
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Post Id'
            }, status=200)


class postLikesTotalCount(APIView):
    
    """
    Get total post like count
    
    @method GET
    @access	private    
    @param	integer post_id
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,post_id,format=None):       
        if post_id.isnumeric():
            try:               
                post = Post.objects.get(id=post_id)
                
                #like count
                cursor = connection.cursor()                
                cursor.execute("SELECT count(*) FROM postlikes WHERE postid=%s" % (post_id))                                        
                totalLikes = cursor.fetchone()[0]               
                return json_response({'status':'success','totalLikes':totalLikes}, status=200)
            except Post.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid Post'}, status=200) 
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Post Id'
            }, status=200)


class viewOtherUserProfile(APIView):
    
    """
    View other user profile
    
    @method GET
    @access	private    
    @param	integer user_id
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id,format=None):
            watcherId = request.GET.get('watcherId', None)
            isFollow = False
            isBlock = False
            try:
                user = Profiles.objects.get(userid=user_id)                
                if watcherId.isnumeric():
                    try:
                        watcherid = Profiles.objects.get(userid=watcherId)          
                        isFollow = Followings.objects.filter(profileid=watcherid,followingprofileid=user)
                        isBlock = Userblock.objects.filter(profileid=watcherid,blockedprofileid=user)
                        if isFollow:
                            isFollow = True
                        else:
                            isFollow = False
                        
                        if isBlock:
                            isBlock = True
                        else:
                            isBlock = False
                    except Profiles.DoesNotExist:
                        return json_response({'status':'error','msg':'Invalid Watcher Id'}, status=200)
                else:
                    #isFollow = False
                    return json_response({'status':'error','msg':'Invalid Watcher Id'}, status=200)
                                            
                totalFollowers = Followings.objects.filter(followingprofileid=user)                
                                                                       
                #Total Text Post
                totalText = Post.objects.filter(profileid=user.id,type='T')
                
                # total Document        
                totalDocument= Post.objects.filter(profileid=user_id,type='D')
                
                #Total Video Post
                totalVideo = Post.objects.filter(profileid=user.id,type='V')
                
                #Total Image Post
                totalImage = Post.objects.filter(profileid=user.id,type='I')
                
                #Total All Post
                totalAllPost = Post.objects.filter(profileid=user.id)
                
                #Total All Products
                totalProducts = Products.objects.filter(profileid=user.id)
                
                return json_response({'status':'success','isFollow':isFollow,'isBlock':isBlock,'totalpost':len(totalAllPost),'totalImage':len(totalImage),'totalDocument':len(totalDocument),'totalVideo':len(totalVideo),'totalText':len(totalText),'totalfollowers':len(totalFollowers),'totalProducts':len(totalProducts)}, status=200)
            
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid User Id'}, status=200)



class favoritePost(APIView):
    
    """
    Favorite post
    
    @method POST
    @access	private    
    @param	integer profileId
    @param	integer postId
    @param	string type
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):        
        postId = request.POST.get('postId', None)
        profileId = request.POST.get('profileId', None)
        type = request.POST.get('type', 'F')    
        if profileId.isnumeric() and postId.isnumeric():
            try:
                profile = Profiles.objects.get(userid=profileId)
                try:
                    post = Post.objects.get(id=postId)
                    try:
                        if type=='F':
                           deletefavorite = Favorites.objects.get(postid=post,profileid=profile,type='F').delete()
                           return json_response({'status':'success','msg':'Favorite removed favorite'}, status=200)
                        if type=='B':
                           deletefavorite = Favorites.objects.get(postid=post,profileid=profile,type='B').delete()
                           return json_response({'status':'success','msg':'Bookmark removed favorite'}, status=200)
                        if type=='I':                           
                            return inAppropriateContentReport(postId, profileId)                            
                    except Favorites.DoesNotExist:
                        if type=='F':
                            postlike = Favorites.objects.create(postid=post,profileid=profile,type='F',createdate=datetime.utcnow())                  
                            return json_response({'status':'success','msg':'Favorite added successfully'}, status=200)
                        if type=='B':
                            postlike = Favorites.objects.create(postid=post,profileid=profile,type='B',createdate=datetime.utcnow())                  
                            return json_response({'status':'success','msg':'Bookmark added successfully'}, status=200)
                        if type=='I':                            
                            return inAppropriateContentReport(postId, profileId)   
                except Post.DoesNotExist:
                    return json_response({'status':'success','msg':'Invalid Post'}, status=200)    
            except Profiles.DoesNotExist:
                return json_response({'status':'success','msg':'Invalid User'}, status=200)    
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)


class addProduct(APIView):
    
    """
    Add/Edit product
    
    @method POST
    @access	private    
    @param	string title
    @param	string description
    @param  decimal price    
    @param	string imageUrl
    @param	integer profileId
    @param  integer productId
    @param	string fileType
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):
        title = request.POST.get('title', None)
        description = request.POST.get('description', None)
        price = request.POST.get('price', None)
        imageUrl = request.POST.get('imageUrl', None)
        profileId = request.POST.get('profileId', None)
        productId = request.POST.get('productId', None)
        fileType = request.POST.get('fileType', "data:image/png;base64,")
        categoryString = request.POST.get('categoryId', None)
        extraImages = request.POST.getlist('extraImages[][imageString]', None)
        tagText = request.POST.get('tagText', None)
                    
        if categoryString:
            category = categoryString.split(',')
        else:
            category = []
        
        if tagText:
            tagList = tagText.split(',')
        else:
            tagList = []
        
        if profileId.isnumeric():
            #if title:  # Removed title validation while product add on 29th march
                if price:
                    isPrice = chekPrice(price)
                    if isPrice==False:
                        return json_response({'status':'success','msg':'Invalid Price,It should be number or decimal.'}, status=200)
                else:
                    price = 0.00
                try:
                    profile = Profiles.objects.get(userid=profileId)                    
                    # Edit Product
                    if productId:
                        if productId.isnumeric():
                            # add product
                            if category:
                                for pkid in category:                                 
                                    if pkid.isnumeric():
                                        cId = int(pkid)
                                    else:
                                        return json_response({'status':'error','msg':'Invalid category'})
                            try:
                                product = Products.objects.get(id=productId,profileid=profile)
                                if imageUrl in [None, '']:
                                    filename = ''
                                else:
                                    millis = int(round(time.time() * 1000))
                                    #filename = "product_%s_%s.png" % (millis, str(profileId))
                                    #filename = "product_%s.png" % str(profileId).replace('.','_')                      
                                    #upload_image(filename,imageUrl,settings.PRODUCT_MEDIA_URL)
                                    #make_thumbnil(filename,profileId,'product',settings.PRODUCT_MEDIA_URL,millis)                            
                                    if product.imageurl:                                    
                                        fileToBedelete = product.imageurl
                                    else:
                                        fileToBedelete = ''
                                    filename = upload_image(fileToBedelete,fileType,imageUrl,settings.PRODUCT_MEDIA_URL,profileId,millis,content='product')
                                # try:
                                #     product = Products.objects.get(~Q(id=productId),title=title,profileid=profile)
                                #     return json_response({'status':'error','msg': 'Product name already exists,please choose another name.'}, status=status.HTTP_400_BAD_REQUEST)
                                # except Products.DoesNotExist:
                                
                                if title:
                                    product.title = title
                                if description:
                                    product.description=description
                                if price:
                                    product.price=price                           
                                if filename:
                                    product.imageurl = filename                                                    
                                product.createdate=datetime.utcnow()
                                product.save()
                                
                                 # Update Product Category
                                if category:
                                    Productcategory.objects.filter(productid=product).delete()
                                    for pkid in category: 
                                        cId = int(pkid)
                                        try:                                        
                                            catid = Category.objects.get(id=cId)
                                            Productcategory.objects.create(categoryid = catid,productid = product,createdate = datetime.utcnow())
                                        except Category.DoesNotExist:
                                            pass
                                
                                # Update product's tag
                                if tagText:
                                    Producttag.objects.filter(productid=product).delete()
                                    for tag in tagList:                                     
                                        Producttag.objects.create(tagtext = tag,productid = product,createdate = datetime.utcnow())
                                        
                                # Update extra images                            
                                if len(extraImages)>0:
                                    millis = int(round(time.time() * 1000))
                                    fileToBedelete = ''
                                    index = 1
                                    ProductImgIDs = []
                                    for extraimg in extraImages:
                                        if extraimg!='':
                                            try:
                                                if "http://" in extraimg:                                                         
                                                    from urlparse import urlparse
                                                    from os.path import splitext, basename                                                                                                                
                                                    disassembled = urlparse(extraimg)
                                                    filename = basename(disassembled.path).replace("small_",'')                                                        
                                                    ProductImgInstance = Productimages.objects.filter(images=filename,productid=product)
                                                    if len(ProductImgInstance)>0:
                                                        for iObj in ProductImgInstance:                                                       
                                                            ProductImgIDs.append(iObj.id)                                                                                                                
                                                else:                                                                                                            
                                                    content = 'product_extra_%s' %(index)
                                                    fileName = upload_image(fileToBedelete,fileType,extraimg,settings.PRODUCT_MEDIA_URL,profileId,millis,content=content)                                                    
                                                    Productimages.objects.create(productid=product,images=fileName,createdate=datetime.utcnow())
                                                    recentProduct = Productimages.objects.filter(productid = product).order_by('-id')[0]
                                                    ProductImgIDs.append(recentProduct.id)     
                                                                                                                                                               
                                                index += 1
                                            except Productimages.DoesNotExist:
                                                pass
                                        else:
                                            pass
                                    if len(ProductImgIDs)>0:
                                        productList = Productimages.objects.filter(productid=product).exclude(id__in=ProductImgIDs)
                                        if len(productList)>0:
                                            for img in productList:
                                                unlinkFile(img.images,settings.PRODUCT_MEDIA_URL)
                                                Productimages.objects.get(id=img.id).delete()                                                    
                                else:
                                    productList = Productimages.objects.filter(productid=product)
                                    if len(productList)>0:
                                        for img in productList:
                                            unlinkFile(img.images,settings.PRODUCT_MEDIA_URL)
                                            Productimages.objects.get(id=img.id).delete()
                                            
                                return json_response({'status':'success','msg':'Product updated successfully'}, status=200)
                            except Products.DoesNotExist:
                                return json_response({'status':'success','msg':'Invalid Product id'}, status=200)
                        else:
                            return json_response({'status':'success','msg':'Invalid Product id'}, status=200)
                    else:                       
                        # add product
                        if category:
                            for pkid in category:                                 
                                if pkid.isnumeric():
                                    cId = int(pkid)
                                else:
                                    return json_response({'status':'error','msg':'Invalid category'})
                                                                                                
                        # try:
                        #     product = Products.objects.get(title=title,profileid=profile)
                        #     return json_response({'status':'error','msg': 'Product name already exists,please choose another name.'}, status=status.HTTP_400_BAD_REQUEST)
                        # except Products.DoesNotExist:
                        #     
                        if imageUrl in [None, '']:
                            filename = ''
                        else:
                            millis = int(round(time.time() * 1000))
                            fileToBedelete = ''
                            #filename = "product_%s_%s.png" % (millis, str(profileId))
                            #filename = "product_%s.png" % str(profileId).replace('.','_')                      
                            #upload_image(filename,imageUrl,settings.PRODUCT_MEDIA_URL)
                            #make_thumbnil(filename,profileId,'product',settings.PRODUCT_MEDIA_URL,millis)                               
                            filename = upload_image(fileToBedelete,fileType,imageUrl,settings.PRODUCT_MEDIA_URL,profileId,millis,content='product')
                        product = Products.objects.create(profileid=profile,title=title, description=description,price=price,imageurl=filename,createdate=datetime.utcnow())
                        recentProduct = Products.objects.filter(profileid = profile).order_by('-id')[0]
                        
                        # Insert product's category
                        if category:
                            for pkid in category: 
                                cId = int(pkid)
                                try:
                                    catid = Category.objects.get(id=cId)
                                    Productcategory.objects.create(categoryid = catid,productid = recentProduct,createdate = datetime.utcnow())
                                except Category.DoesNotExist:
                                    pass
                        
                        
                        # Insert product's tag
                        if tagText:
                           for tag in tagList:                                     
                                Producttag.objects.create(tagtext = tag,productid = recentProduct,createdate = datetime.utcnow())
                        
                        # Inssert extra images                            
                        if len(extraImages)>0:
                            millis = int(round(time.time() * 1000))
                            fileToBedelete = ''
                            index = 1    
                            for extraimg in extraImages:
                                if extraimg!='':
                                    try:
                                        pid = Products.objects.get(id=recentProduct.id)
                                        content = 'product_extra_%s' %(index)
                                        fileName = upload_image(fileToBedelete,fileType,extraimg,settings.PRODUCT_MEDIA_URL,profileId,millis,content=content)
                                        Productimages.objects.create(productid=recentProduct,images=fileName,createdate=datetime.utcnow())
                                        index += 1
                                    except Products.DoesNotExist:
                                        pass
                                else:
                                    pass
                                
                        return json_response({'status':'success','msg':'Product created successfully','id':product.id}, status=200)
                except Profiles.DoesNotExist:
                        return json_response({'status':'success','msg':'Invalid User'}, status=200)
            #else:
                 #return json_response({'status':'success','msg':'Product name is required'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid userid'
            }, status=400)


class addAlbum(APIView):
    
    """
    Add / edit album
    
    @method POST
    @access	private    
    @param	string title
    @param	string description   
    @param	integer profileId
    @param  integer albumId    
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):
        title = request.POST.get('title', None)
        description = request.POST.get('description', None)       
        profileId = request.POST.get('profileId', None)
        albumId = request.POST.get('albumId', None)       
        
        if profileId.isnumeric():
            if title:
                try:
                    profile = Profiles.objects.get(userid=profileId)                   
                    if albumId:
                        if albumId.isnumeric():
                            try:
                                isAlbumExist = Albums.objects.get(id=albumId)
                                try:
                                    albums = Albums.objects.get(~Q(id=albumId),title=title,profileid=profile)
                                    return json_response({'status':'error','msg': 'Album name already exists,please choose another name.'}, status=status.HTTP_400_BAD_REQUEST)
                                except Albums.DoesNotExist:
                                    isAlbumExist.title = title
                                    isAlbumExist.description = description
                                    isAlbumExist.save()
                                    return json_response({'status':'success','msg':'Album updated successfully'}, status=200)
                            except Albums.DoesNotExist:
                                return json_response({'status':'error','msg':'Invalid album id'}, status=200) 
                        else:
                           return json_response({'status':'error','msg':'Invalid album id'}, status=200) 
                    else:
                        try:
                            albums = Albums.objects.get(title=title,profileid=profile)
                            return json_response({'status':'error','msg': 'Album name already exists,please choose another name.'}, status=status.HTTP_400_BAD_REQUEST)
                        except Albums.DoesNotExist:
                            album = Albums.objects.create(profileid=profile,title=title, description=description,createdate=datetime.utcnow())
                            return json_response({'status':'success','msg':'Album created successfully'}, status=200)
                except Profiles.DoesNotExist:
                        return json_response({'status':'success','msg':'Invalid User'}, status=200)
            else:
                 return json_response({'status':'success','msg':'Album name is required'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid userid'
            }, status=400)


class getUserFavoriteContentList(APIView):
    
    """
    Get user favorite content
    
    @method GET
    @access	private       
    @param  integer user_id    
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id, format=None):                        
        if user_id.isnumeric():
            page = int (request.GET.get('page', 1))  
            recordsPerPage = int (request.GET.get('recordsPerPage', 10))
            feedType = request.GET.get('feedType', 'F')
            try:
                profile = Profiles.objects.get(userid=user_id)
                try:
                    field = []
                    favoriteList = Favorites.objects.filter(profileid=profile,type=feedType).order_by('-createdate')
                    mainUrl = settings.BASE_URL + settings.STATIC_URL+ settings.POST_MEDIA_URL
                    thumburl = mainUrl +'thumbs/'                   
                    if len(favoriteList)>0:
                        
                        count = favoriteList.count()
                        paginator = Paginator(favoriteList, recordsPerPage)
                    
                        try:
                            fevObj = paginator.page(page)
                        except PageNotAnInteger:
                            # If page is not an integer, deliver first page.
                            fevObj = paginator.page(1)
                        except EmptyPage:
                            # If page is out of range (e.g. 9999), deliver last page of results.
                            fevObj = paginator.page(paginator.num_pages)
                        
                        for fObj in fevObj:
                            if fObj.postid.thumbnailurl and fObj.postid.type=='I':
                                small_thumb = thumburl+'small_'+fObj.postid.thumbnailurl
                                medium_thumb = thumburl+'medium_'+fObj.postid.thumbnailurl
                                original_img =  mainUrl+fObj.postid.thumbnailurl
                            elif fObj.postid.thumbnailurl and fObj.postid.type=='V':                                
                                mainUrl1 = settings.BASE_URL + settings.STATIC_URL+ settings.VIMEO_URL
                                thumburl1 = mainUrl1+'thumbs/'                
                                small_thumb = thumburl1+'small_'+fObj.postid.thumbnailurl
                                medium_thumb = thumburl1+'medium_'+fObj.postid.thumbnailurl
                                original_img = mainUrl1+fObj.postid.thumbnailurl
                    
                            elif fObj.postid.thumbnailurl and fObj.postid.type=='D':
                                small_thumb = mainUrl+fObj.postid.thumbnailurl
                                medium_thumb = mainUrl+fObj.postid.thumbnailurl
                                original_img =  mainUrl+fObj.postid.thumbnailurl
                            else:
                                small_thumb = ''
                                medium_thumb = ''
                                original_img =''
                            
                            # Posted by
                            if fObj.profileid.lastname:
                                postedBy = fObj.profileid.firstname +" "+fObj.profileid.lastname
                            else:
                                postedBy = fObj.profileid.firstname
                            
                             # Total Likes
                            totalLikes = Postlikes.objects.filter(postid=fObj.postid.id)
                            myLikes = Postlikes.objects.filter(postid=fObj.postid.id,profileid=profile)
                            
                            # Total Comments
                            totalComment = Comments.objects.filter(postid=fObj.postid.id)
                            
                             # Total Favorite
                            totalFavorites = Favorites.objects.filter(postid=fObj.postid.id,type=feedType)
                            myFavorites = Favorites.objects.filter(postid=fObj.postid.id,profileid=profile,type=feedType)
                        
                            field.append({
                                'profileid':fObj.profileid.userid.id,
                                'id':fObj.postid.id,
                                'title':fObj.postid.title,
                                'description':fObj.postid.description,
                                'type':fObj.postid.type,
                                'scope':fObj.postid.scope,
                                'posturl' : fObj.postid.posturl,
                                'vimeoId' : fObj.postid.length,
                                'createdate':getDate(fObj.postid.createdate),
                                'small_thumb':small_thumb,
                                'medium_thumb':medium_thumb,
                                'original_img':original_img,
                                'firstname':fObj.profileid.firstname,
                                'lastname':fObj.profileid.lastname,
                                'companyname':fObj.profileid.companyname,
                                'postedBy': postedBy,
                                'myLikes':len(myLikes),
                                'myFavorites':len(myFavorites),
                                'totalLikes':len(totalLikes),
                                'totalComment':len(totalComment),
                                'totalFavorites':len(totalFavorites)
                            })
                        return json_response({'status':'success','result':json.dumps(field),'total':len(favoriteList)}, status=200)
                    else:
                        return json_response({'status':'success','msg':'No records found','result':'Record not found'}, status=200) 
                except Favorites.DoesNotExist:
                    return json_response({'status':'success','msg':'Empty result'}, status=200)   
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid User'}, status=200)    
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)
        

class getProductDetail(APIView):
    
    """
    Get product detail by id
    
    @method GET
    @access	private       
    @param  integer product_id    
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,product_id,format=None):
        watcherId = request.GET.get('userId', None)
        if product_id.isnumeric():
            try:
                profile = Profiles.objects.get(userid=watcherId)
                try:               
                    product = Products.objects.get(id=product_id)
                    imageUrl = settings.BASE_URL + settings.STATIC_URL+ settings.PRODUCT_MEDIA_URL
                    thumburl = imageUrl+'thumbs/'
                    if product.imageurl:
                        small_thumb = thumburl+'small_'+product.imageurl
                        medium_thumb = thumburl+'medium_'+product.imageurl
                        original_img = imageUrl+product.imageurl
                    else:
                        small_thumb = ''
                        medium_thumb = ''
                        original_img = ''
                    
                    if product.profileid.lastname:
                        productCreatedBy = product.profileid.firstname + " " + product.profileid.lastname
                    else:
                        productCreatedBy = product.profileid.firstname
                    
                    if product.createdate:                            
                        createdate = getDate(product.createdate)
                    else:                            
                        createdate = getDate(datetime.utcnow())
                        
                    try:
                        productstatistics = Productstatistics.objects.get(productid=product)                    
                        productstatistics.totalview += 1                                    
                        productstatistics.save()                    
                    except Productstatistics.DoesNotExist:
                        Productstatistics.objects.create(productid=product,totalview=1)
                    
                    
                    # CategoryList
                    cat_list = []
                    categorylist = Productcategory.objects.filter(productid=product)
                    for catObj in categorylist:
                        cat_list.append(catObj.categoryid.id)                    
                    cat_id_in = ','.join(map(str, cat_list))
                    
                    # TagList
                    try:
                        tag_list = []
                        tagList = Producttag.objects.filter(productid=product)
                        for tagObj in tagList:
                            tag_list.append(tagObj.tagtext)                    
                        tag_id_in = ','.join(map(str, tag_list))
                    except Producttag.DoesNotExist:
                        tag_id_in = ''
                        
                    # Random 3 top products list
                    field = []                
                    try:
                        blockedUsers = Userblock.objects.filter(profileid=profile)
                        blockedProduct = Products.objects.filter(profileid__in=[p.blockedprofileid for p in blockedUsers])
                        randomProducts = Productstatistics.objects.filter(~Q(id=product_id)).exclude(productid__in=[p.pk for p in blockedProduct]).order_by('-totalview','-totalsharing')[:3]    
                        #randomProducts = Productstatistics.objects.filter(~Q(id=product_id)).order_by('-totalview','-totalsharing')[:3]                    
                        for rObj in randomProducts:
                             if rObj.productid.imageurl:
                                psmall_thumb = thumburl+'small_'+rObj.productid.imageurl
                                pmedium_thumb = thumburl+'medium_'+rObj.productid.imageurl
                                poriginal_img = imageUrl+rObj.productid.imageurl
                             else:
                                poriginal_img = psmall_thumb = pmedium_thumb = ''
                                                    
                             field.append(
                                {
                                'id':rObj.productid.id,
                                'title':rObj.productid.title, 
                                'description':rObj.productid.description,
                                'small_thumb' : psmall_thumb,
                                'medium_thumb' : pmedium_thumb,
                                'poriginal_img':poriginal_img,                            
                                }
                            )                    
                    except Productstatistics.DoesNotExist:
                        pass
                    
                    
                     # Get extra products images
                    extraImages = []                
                    try:
                        productImages = Productimages.objects.filter(productid=product)                        
                        for piObj in productImages:
                             if piObj.images:
                                pismall_thumb = thumburl+'small_'+piObj.images
                                pimedium_thumb = thumburl+'medium_'+piObj.images
                                pioriginal_img = imageUrl+piObj.images
                             else:
                                poriginal_img = psmall_thumb = pmedium_thumb = ''
                                                    
                             extraImages.append(
                                {                            
                                'extra_small_thumb' : pismall_thumb,
                                'extra_medium_thumb' : pimedium_thumb,
                                'extra_poriginal_img':pioriginal_img,                            
                                }
                            )                    
                    except Productimages.DoesNotExist:
                        pass
                                                
                    return json_response({'status':'success','result':{'id':product.id,'title':product.title,'description':product.description,'price' : product.price,
                                        'profileid' : product.profileid.userid.id,'productCreatedBy' : productCreatedBy,'companyname':product.profileid.companyname,'small_thumb':small_thumb,'medium_thumb':medium_thumb, 'tagList':tag_id_in,'createdate':createdate,'categoryid':cat_id_in,'randomProducts':json.dumps(field),'extraProductImages':json.dumps(extraImages)}}, status=200)
                except Products.DoesNotExist:
                    return json_response({'status':'error','msg':'Invalid Product'}, status=200)
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid user id'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Product Id'
            }, status=200)


class deleteProduct(APIView):
    
    """
    Delete Product
    
    @method GET
    @access	private       
    @param  integer user_id
    @param  integer productId    
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self,request,user_id,format=None):
        if user_id.isnumeric():
            try:
                #user = Users.objects.get(id=user_id)
                profile = Profiles.objects.get(userid=user_id)
                productId = request.GET.get('productId', None)
                if productId:
                    if productId.isnumeric():
                        try:
                            product = Products.objects.get(id=productId) #,profileid=user.id
                            if product:
                                producttag = Producttag.objects.filter(productid=product).delete()
                                productcategory = Productcategory.objects.filter(productid=product).delete()
                                productstatistics = Productstatistics.objects.filter(productid=product).delete()
                                productimages = Productimages.objects.filter(productid=product)
                                if len(productimages)>0:                                   
                                    for i in productimages:
                                         if i.images:                                            
                                            unlinkFile(i.images,settings.PRODUCT_MEDIA_URL)
                                         else:
                                            pass
                                    productimages = Productstatistics.objects.filter(productid=product).delete()
                                
                                if product.imageurl:                                    
                                    fileToBedelete = product.imageurl
                                    unlinkFile(fileToBedelete,settings.PRODUCT_MEDIA_URL)
                                else:
                                    pass                               
                                
                                product = Products.objects.get(id=productId,profileid=profile.id).delete()
                            return json_response({'status':'success','msg':'Product deleted successfully'},status=200)
                        except Products.DoesNotExist:
                            return json_response({'status':'error','msg':'Invalid Product id'},status=200)
                    else:
                        return json_response({'status':'error','msg':'Invalid Product Id'}, status=200)
                else:
                    return json_response({
                        'status':'error',
                        'msg': 'Product id is missing'
                    }, status=200)
            except Users.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid User Id'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)
        

class addPostStatistics(APIView):
    
    """
    Add Post statistics
    
    @method POST
    @access	private       
    @param  integer postId
    @param  integer totalSharing    
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):        
        postId = request.POST.get('postId', None)
        #totalView = request.POST.get('totalView', None)
       # totalRating = request.POST.get('totalRating', None)
        totalSharing = request.POST.get('totalSharing', None)        
        if postId.isnumeric():
            try:
                post = Post.objects.get(id=postId)
                try:
                    poststatistics = Poststatistics.objects.get(postid=post)
                    #if totalView:
                        #poststatistics.totalview += 1
                    #if totalRating:
                     #   poststatistics.totalrating += 1
                    if totalSharing:
                        poststatistics.totalsharing += 1
                    poststatistics.save()
                    return json_response({'status':'success','msg':'added successfully'}, status=200)     
                except Poststatistics.DoesNotExist:
                    Poststatistics.objects.create(productid=product,totalsharing=1)
                    return json_response({'status':'success','msg':'added successfully'}, status=200)   
            except Post.DoesNotExist:
                return json_response({'status':'success','msg':'Invalid Post'}, status=200)        
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Post Id'
            }, status=200)
        

class addProductStatistics(APIView):
    
    """
    Add Product statistics
    
    @method POST
    @access	private       
    @param  integer productId
    @param  integer totalSharing    
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):        
        productId = request.POST.get('productId', None)        
        totalSharing = request.POST.get('totalSharing', None)        
        if productId.isnumeric():
            try:
                product = Products.objects.get(id=productId)
                try:
                    productstatistics = Productstatistics.objects.get(productid=product)                      
                    if totalSharing:
                        productstatistics.totalsharing += 1
                    productstatistics.save()
                    return json_response({'status':'success','msg':'added successfully'}, status=200)     
                except Productstatistics.DoesNotExist:
                    Productstatistics.objects.create(productid=product,totalsharing=1)
                    return json_response({'status':'success','msg':'added successfully'}, status=200)   
            except product.DoesNotExist:
                return json_response({'status':'success','msg':'Invalid Product'}, status=200)        
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid Product Id'
            }, status=200)

        
def inAppropriateContentReport(postId, profileId):
    reportedBy = profileId
    if postId.isnumeric() and reportedBy.isnumeric():
        try:
            user = Profiles.objects.get(userid=reportedBy)                
            try:
                post = Post.objects.get(id=postId)                    
                if user.id!=post.profileid.userid.id:
                    subject="In appropriate content"            
                    #message="In appropriate content report"
                    admin_email_id = settings.EMAIL_HOST_USER
                    fromId = user.userid.email
                    templatePath = os.path.join(settings.BASE_DIR, 'templates/admin/email')
                    baseUrl = settings.BASE_URL + settings.STATIC_URL
                    if post.createdate:
                        createdate = post.createdate.strftime('%m/%d/%Y')
                    else:
                        createdate ='N/A'
                    message = render_to_string(templatePath+'/abuse_report.html', {'post_id': post.id,'title':post.title,'content':post.description,'post_owner':post.profileid.firstname,'postcreate_date':createdate,'reported_by':user.firstname,'baseUrl':baseUrl})
                    sendmail(subject,message,admin_email_id,fromId)
                    return json_response({'status':'success','msg':'Mail send successfully','post_id': post.id,'title':post.title,'content':post.description,'post_owner':post.profileid.firstname,'postcreate_date':createdate,'reported_by':user.firstname}, status=200)
                else:
                     return json_response({'status':'success','msg':'You are reporting about own content'}, status=200)  
            except Post.DoesNotExist:
                return json_response({'status':'success','msg':'Invalid Post'}, status=200)                            
        except Profiles.DoesNotExist:
            return json_response({'status':'success','msg':'Invalid User'}, status=200)        
    else:
        return json_response({
            'status':'error',
            'msg': 'Invalid Post Or User Id'
        }, status=200)
    

class getFeedDetail(APIView):
    
    """
    Get feed detail by id
    
    @method POST
    @access	private       
    @param  integer postId    
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id,format=None):
        postId = request.GET.get('postId', None)
        if user_id.isnumeric():
            try:
                profile = Profiles.objects.get(userid=user_id)
                try:               
                    post = Post.objects.get(id=postId)
                    if post.createdate:
                        post_createdate = getDate(post.createdate)
                    else:
                        post_createdate = 'N/A'
                    
                    mainUrl = settings.BASE_URL + settings.STATIC_URL+ settings.POST_MEDIA_URL    
                    thumburl = mainUrl+'thumbs/'                   
                    if post.thumbnailurl and post.type=='I':
                        small_thumb = thumburl+'small_'+post.thumbnailurl
                        medium_thumb = thumburl+'medium_'+post.thumbnailurl
                        original_img = mainUrl+post.thumbnailurl
                    elif post.thumbnailurl and post.type=='V':                        
                        mainUrl1 = settings.BASE_URL + settings.STATIC_URL+ settings.VIMEO_URL
                        thumburl1 = mainUrl1+'thumbs/'                
                        small_thumb = thumburl1+'small_'+post.thumbnailurl
                        medium_thumb = thumburl1+'medium_'+post.thumbnailurl
                        original_img = mainUrl1+post.thumbnailurl                                
                    elif post.thumbnailurl and post.type=='D':
                        small_thumb = mainUrl+post.thumbnailurl
                        medium_thumb = mainUrl+post.thumbnailurl
                        original_img = mainUrl+post.thumbnailurl
                    else:
                        small_thumb = ''
                        medium_thumb = ''
                        original_img = ''
                    
                    # CategoryList
                    try:
                        cat_list = []
                        categorylist = Postcategory.objects.filter(postid=post)
                        for catObj in categorylist:
                            cat_list.append(catObj.categoryid.id)                    
                        cat_id_in = ','.join(map(str, cat_list))
                    except Postcategory.DoesNotExist:
                        cat_id_in = ''
                    
                    # Reopen Tags removed from benefit
                    
                    # TagList               
                    try:
                        tag_list = []
                        tagList = Imagetag.objects.filter(postid=post)
                        for tagObj in tagList:
                            tag_list.append(tagObj.tagtext)                    
                        tag_id_in = ','.join(map(str, tag_list))
                    except Imagetag.DoesNotExist:
                        tag_id_in = ''
                                    
                    
                    # Total Likes
                    totalLikes = Postlikes.objects.filter(postid=post)
                    
                    try:                                
                        isMyLike = Postlikes.objects.get(postid=post,profileid=profile)
                        isMyLike = 1
                    except Postlikes.DoesNotExist:
                        isMyLike = 0
                        
                    try:                                
                        isMyFavorites = Favorites.objects.get(postid=post,profileid=profile,type='F')
                        isMyFavorites = 1
                    except Favorites.DoesNotExist:
                        isMyFavorites = 0
                    
                    try:                                
                        isMyBookmark = Favorites.objects.get(postid=post,profileid=profile,type='B')
                        isMyBookmark = 1
                    except Favorites.DoesNotExist:
                        isMyBookmark = 0
                                                    
                    # Total Comments
                    totalComment = Comments.objects.filter(postid=post)
                    parentComment = Comments.objects.filter(postid=post,parentcommentid=0).order_by('createdate')
                    childComment = Comments.objects.filter(~Q(parentcommentid=0),postid=post).order_by('createdate')
                    field = []
                    child = []                   
                    if parentComment:
                        for cmtObj in parentComment:                            
                            if cmtObj.createdate:
                                parentcreatedate = getDate(cmtObj.createdate)
                            else:
                                parentcreatedate = getDate(datetime.utcnow())
                            if cmtObj.profileid.profilephoto:
                                mediumthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/medium_'+cmtObj.profileid.profilephoto
                                smallthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/small_'+cmtObj.profileid.profilephoto
                            else:
                                smallthumbimg = mediumthumbimg = ''
                                
                            if cmtObj.profileid.lastname:
                                commentBy = cmtObj.profileid.firstname +' '+ cmtObj.profileid.lastname
                            else:
                                commentBy = cmtObj.profileid.firstname
                                                                                                        
                            child = []
                            totalLikeComment = Commentlikes.objects.filter(commentid=cmtObj.id)
                            if childComment:
                                for chilObj in childComment:
                                    childcreatedate = getDate(chilObj.createdate)
                                    if chilObj.profileid.profilephoto:
                                        childmediumthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/medium_'+chilObj.profileid.profilephoto
                                        childsmallthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/small_'+chilObj.profileid.profilephoto
                                    else:
                                        childmediumthumbimg = childsmallthumbimg = ''
                                    
                                    if chilObj.profileid.lastname:
                                        childcommentBy = chilObj.profileid.firstname +' '+ chilObj.profileid.lastname
                                    else:
                                        childcommentBy = chilObj.profileid.firstname
                                        
                                    childtotalLikeComment = Commentlikes.objects.filter(commentid=chilObj.id)
                                        
                                    if chilObj.parentcommentid == cmtObj.id:
                                        child.append({
                                        'childid':chilObj.id,
                                        'comment':chilObj.comment,
                                        'ParentcommentId':chilObj.parentcommentid,
                                        'commentOn':childcreatedate, 
                                        'postid' : chilObj.postid.id, 
                                        'userid' : chilObj.profileid.userid.id, 
                                        'commentBy' : childcommentBy,
                                        'child_companyname' : chilObj.profileid.companyname,
                                        'user_small_img' : childsmallthumbimg,
                                        'user_medium_img' : childmediumthumbimg,
                                        'totalLikeComment':len(childtotalLikeComment),
                                    })                                    
                            field.append(
                                {
                                    'id':cmtObj.id,
                                    'comment':cmtObj.comment,
                                    'ParentcommentId':cmtObj.parentcommentid,
                                    'commentOn':parentcreatedate, 
                                    'postid' : cmtObj.postid.id, 
                                    'userid' : cmtObj.profileid.userid.id, 
                                    'commentBy' : commentBy,
                                    'companyname' : cmtObj.profileid.companyname,
                                    'user_small_img' : smallthumbimg,
                                    'user_medium_img' : mediumthumbimg,
                                    'totalLikeComment':len(totalLikeComment),                                    
                                    'replies':child
                                }
                            )                                                                            
                    return json_response({'status':'success','result':{'id':post.id,'post_createdated':post_createdate,'title':post.title,'description':post.description,'scope' : post.scope, 'type' : post.type,'post_owner_id' : post.profileid.userid.id,'post_owner_name' : post.profileid.firstname,'post_owner_companyname' : post.profileid.companyname,'category':cat_id_in,'post_small_thumb':small_thumb,'post_medium_thumb':medium_thumb,'original_img':original_img,'tagList':tag_id_in,'totalLikes':len(totalLikes),'totalComment':len(totalComment),'posturl' : post.posturl,'comments':json.dumps(field),'isMyBookmark':isMyBookmark,'isMyFavorites':isMyFavorites,'isMyLike':isMyLike}}, status=200)
                except Post.DoesNotExist:
                    return json_response({'status':'error','msg':'Invalid Post'}, status=200)
            except Users.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid User'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)
        
    
class getTrending(APIView):
    
    """
    Get Top View Post and Products
    
    @method POST
    @access	private       
    @param  string feedType    
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id,format=None):
        if user_id.isnumeric():
            feedType = request.GET.get('feedType', 'A')
            page = int (request.GET.get('page', 1))  
            recordsPerPage = int (request.GET.get('recordsPerPage', 10))
            try:
                Profile = Profiles.objects.get(userid=user_id)
                # Celebrity case
                if feedType=='C':
                    return getCelebrityFeed(user_id,page,recordsPerPage)
                    
                try:                   
                    # block user case
                    blockedUsers = Userblock.objects.filter(blockedprofileid=Profile)                    
                    if len(blockedUsers)>0:
                        if feedType=='A':
                            post = Post.objects.filter(profileid__in=[p.blockedprofileid for p in blockedUsers])                        
                            trendinglist = Poststatistics.objects.exclude(postid__in=[p.pk for p in post]).order_by('-totalview')
                            
                            product = Products.objects.filter(profileid__in=[p.blockedprofileid for p in blockedUsers])      
                            topProducts = Productstatistics.objects.exclude(productid__in=[p.pk for p in product]).order_by('-totalview')                       
                        elif feedType=='P':                                        
                            trendinglist = None
                            
                            product = Products.objects.filter(profileid__in=[p.blockedprofileid for p in blockedUsers])      
                            topProducts = Productstatistics.objects.exclude(productid__in=[p.pk for p in product]).order_by('-totalview')
                        else:
                            post = Post.objects.filter(profileid__in=[p.blockedprofileid for p in blockedUsers])                        
                            trendinglist = Poststatistics.objects.exclude(postid__in=[p.pk for p in post]).filter(postid__type=feedType)
                            topProducts = None
                    else:
                        if feedType=='A':
                            trendinglist = Poststatistics.objects.all().order_by('-totalview')
                            topProducts = Productstatistics.objects.all().order_by('-totalview')                        
                        elif feedType=='P':
                            trendinglist = None
                            topProducts = Productstatistics.objects.all().order_by('-totalview')
                        else:
                            trendinglist = Poststatistics.objects.filter(postid__type=feedType).order_by('-totalview')
                            topProducts = None
                            
                                         
                       
                    mainUrl = settings.BASE_URL + settings.STATIC_URL+ settings.POST_MEDIA_URL
                    thumburl = mainUrl+'thumbs/'                    
                    field = []
                    pfield = []
                    if trendinglist:
                        totalPost = len(trendinglist)
                        count = trendinglist.count()
                        paginator = Paginator(trendinglist, recordsPerPage)
                        try:
                            trendObj = paginator.page(page)
                        except PageNotAnInteger:
                            # If page is not an integer, deliver first page.
                            trendObj = paginator.page(1)
                        except EmptyPage:
                            # If page is out of range (e.g. 9999), deliver last page of results.
                            trendObj = paginator.page(paginator.num_pages)
                        for postobj in trendObj:
                            
                            if postobj.postid.thumbnailurl and postobj.postid.type=='I':
                                small_thumb = thumburl+'small_'+postobj.postid.thumbnailurl
                                medium_thumb = thumburl+'medium_'+postobj.postid.thumbnailurl
                                original_img = mainUrl+postobj.postid.thumbnailurl
                            elif postobj.postid.thumbnailurl and postobj.postid.type=='V':                                
                                mainUrl1 = settings.BASE_URL + settings.STATIC_URL+ settings.VIMEO_URL
                                thumburl1 = mainUrl1+'thumbs/'                
                                small_thumb = thumburl1+'small_'+postobj.postid.thumbnailurl
                                medium_thumb = thumburl1+'medium_'+postobj.postid.thumbnailurl
                                original_img = mainUrl1+postobj.postid.thumbnailurl                        
                            elif postobj.postid.thumbnailurl and postobj.postid.type=='D':
                                small_thumb = mainUrl+postobj.postid.thumbnailurl
                                medium_thumb = mainUrl+postobj.postid.thumbnailurl
                                original_img = mainUrl+postobj.postid.thumbnailurl
                            else:
                                original_img = small_thumb = medium_thumb = ''
                            if postobj.postid.createdate:                           
                                createdate = getDate(postobj.postid.createdate)
                            else:                            
                                createdate = getDate(datetime.utcnow())
                            
                            if postobj.postid.profileid.lastname:
                                postedBy = postobj.postid.profileid.firstname + " " + postobj.postid.profileid.lastname
                            else:
                                postedBy = postobj.postid.profileid.firstname
                            
                                                                           
                            profile = Profiles.objects.get(userid=postobj.postid.profileid.userid.id)
                            postid = postobj.postid.id
                                                                                                
                             # Total Likes
                            totalLikes = Postlikes.objects.filter(postid=postid)
                            myLikes = Postlikes.objects.filter(postid=postobj.postid.id,profileid=Profile)
                            
                                                                                
                            # Total Comments
                            totalComment = Comments.objects.filter(postid=postid)
                            
                             # Total Favorite
                            totalFavorites = Favorites.objects.filter(postid=postid,type='F')
                            myFavorites = Favorites.objects.filter(postid=postid,profileid=Profile,type='F')
                            try:                                
                                isMyFavorites = Favorites.objects.get(postid=postid,profileid=Profile,type='F')
                                isMyFavorites = 1
                            except Favorites.DoesNotExist:
                                isMyFavorites = 0
                            
                            totalBoomark = Favorites.objects.filter(postid=postid,type='B')
                            myBookmark = Favorites.objects.filter(postid=postid,profileid=Profile,type='B')
                            try:                                
                                isMyBookmark = Favorites.objects.get(postid=postid,profileid=Profile,type='B')
                                isMyBookmark = 1
                            except Favorites.DoesNotExist:
                                isMyBookmark = 0
                            
                            totalFavoritesRecord = Favorites.objects.filter(postid=postid)
                                                                                        
                            field.append(
                                {
                                    'id':postobj.postid.id,
                                    'title':postobj.postid.title, 
                                    'description':postobj.postid.description, 
                                    'scope' : postobj.postid.scope, 
                                    'type' : postobj.postid.type,
                                    'posturl' : postobj.postid.posturl,
                                    'vimeoId' : postobj.postid.length, 
                                    'profileid' : postobj.postid.profileid.id,
                                    'userid' : postobj.postid.profileid.userid.id,                               
                                    'totalView':postobj.totalview,
                                    'totalRating':postobj.totalrating,
                                    'totalLike':postobj.totallike,
                                    'totalSharing':postobj.totalsharing,                                
                                    'createdate' : createdate, 
                                    'small_thumb' : small_thumb,
                                    'medium_thumb' : medium_thumb,
                                    'original_img':original_img,
                                    'postedBy' :  postedBy,
                                    'companyname':postobj.postid.profileid.companyname,
                                    'myLikes':len(myLikes),
                                    'myFavorites':len(myFavorites),
                                    'totalLikes':len(totalLikes),
                                    'totalComment':len(totalComment),
                                    'totalFavorites':len(totalFavorites),
                                    'totalBoomark':len(totalBoomark),
                                    'myBookmark':len(myBookmark),
                                    'totalFavoritesRecord':len(totalFavoritesRecord),
                                    'isMyFavorites':isMyFavorites,
                                    'isMyBookmark':isMyBookmark
                                }
                            )
                    else:
                        totalPost = ''
                    if topProducts:
                        totlProducts = len(topProducts)
                        pimageUrl = settings.BASE_URL + settings.STATIC_URL+ settings.PRODUCT_MEDIA_URL
                        pthumburl = pimageUrl+'thumbs/'
                        for pobj in topProducts:
                            
                            if pobj.productid.imageurl:
                                small_thumb = pthumburl+'small_'+pobj.productid.imageurl
                                medium_thumb = pthumburl+'medium_'+pobj.productid.imageurl
                                original_img = pimageUrl+pobj.productid.imageurl       
                            else:
                                original_img = small_thumb = medium_thumb = ''
                            if pobj.productid.createdate:                           
                                createdate = getDate(pobj.productid.createdate)
                            else:                            
                                createdate = getDate(datetime.utcnow())
                            
                            if pobj.productid.profileid.lastname:
                                postedBy = pobj.productid.profileid.firstname + " " + pobj.productid.profileid.lastname
                            else:
                                postedBy = pobj.productid.profileid.firstname
                            
                            pfield.append(
                            {
                                'id':pobj.productid.id,
                                'title':pobj.productid.title, 
                                'description':pobj.productid.description, 
                                'scope' : 0, 
                                'type' : 'P',
                                'posturl' : '',
                                'vimeoId' : '', 
                                'profileid' : pobj.productid.profileid.id,
                                'userid' : pobj.productid.profileid.userid.id,                               
                                'totalView':pobj.totalview,
                                'totalRating':'',
                                'totalLike':'',
                                'totalSharing':pobj.totalsharing,                                
                                'createdate' : createdate, 
                                'small_thumb' : small_thumb,
                                'medium_thumb' : medium_thumb,
                                'original_img':original_img,
                                'postedBy' :  postedBy,
                                'companyname':pobj.productid.profileid.companyname,
                                'myLikes':'',
                                'myFavorites':'',
                                'totalLikes':'',
                                'totalComment':'',
                                'totalFavorites':'',
                                'totalBoomark':'',
                                'myBookmark':'',
                                'totalFavoritesRecord':'',
                            }
                        )
                    else:
                        totlProducts = ''
                    return json_response({'status':'success','result':json.dumps(field),'topProduct':json.dumps(pfield),'totalpost':totalPost,'totalproduct':totlProducts}, status=200)                    
                except Poststatistics.DoesNotExist:
                    return json_response({
                        'status':'error',
                        'result': 'Record not found',
                        'msg': 'No records found'
                }, status=200)
            except Profiles.DoesNotExist:
                    return json_response({
                        'status':'error',
                        'msg': 'Invalid User Id'
                }, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)
        
class commentLike(APIView):
    
    """
    Comment like
    
    @method POST
    @access	private       
    @param  integer commentId
    @param  integer profileId    
    @return	json array
    """
    @apikey_required
    @token_required
    def post(self, request, format=None):        
        commentId = request.POST.get('commentId', None)
        profileId = request.POST.get('profileId', None)        
        if profileId.isnumeric() and commentId.isnumeric():
            try:
                profile = Profiles.objects.get(userid=profileId)
                try:
                    comment = Comments.objects.get(id=commentId)
                    try:
                        commentlike = Commentlikes.objects.get(commentid=comment,profileid=profile).delete()
                        totalLikes = Commentlikes.objects.filter(commentid=comment)                       
                        return json_response({'status':'success','msg':'Removed like','totalLikes':len(totalLikes)}, status=200)
                    except Commentlikes.DoesNotExist:
                        commentlike = Commentlikes.objects.create(commentid=comment,profileid=profile,createdate=datetime.utcnow())
                        totalLikes = Commentlikes.objects.filter(commentid=comment)                                                
                        return json_response({'status':'success','msg':'added successfully','totalLikes':len(totalLikes)}, status=200)
                except Comments.DoesNotExist:
                    return json_response({'status':'success','msg':'Invalid Comment'}, status=200)    
            except Profiles.DoesNotExist:
                return json_response({'status':'success','msg':'Invalid User'}, status=200)    
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)
            
            

def getCelebrityFeed(user_id,page,recordsPerPage):   
    if user_id.isnumeric():
        try:
            Profile = Profiles.objects.get(userid=user_id)            
            postList = Post.objects.filter(profileid__iscelebrity=1).order_by('-createdate')            
            productList = Products.objects.filter(profileid__iscelebrity=1).order_by('-createdate')
            mainUrl = settings.BASE_URL + settings.STATIC_URL+ settings.POST_MEDIA_URL
            thumburl = mainUrl+'thumbs/'                    
            field = []
            pfield = []            
            if postList:                
                totalPost = len(postList)
                count = postList.count()
                paginator = Paginator(postList, recordsPerPage)
                try:
                    postListObj = paginator.page(page)
                except PageNotAnInteger:
                    # If page is not an integer, deliver first page.
                    postListObj = paginator.page(1)
                except EmptyPage:
                    # If page is out of range (e.g. 9999), deliver last page of results.
                    postListObj = paginator.page(paginator.num_pages)
                for postobj in postListObj:                    
                    if postobj.thumbnailurl and postobj.type=='I':
                        small_thumb = thumburl+'small_'+postobj.thumbnailurl
                        medium_thumb = thumburl+'medium_'+postobj.thumbnailurl
                        original_img = mainUrl+postobj.thumbnailurl
                    elif postobj.thumbnailurl and postobj.type=='V':                                
                        mainUrl1 = settings.BASE_URL + settings.STATIC_URL+ settings.VIMEO_URL
                        thumburl1 = mainUrl1+'thumbs/'                
                        small_thumb = thumburl1+'small_'+postobj.thumbnailurl
                        medium_thumb = thumburl1+'medium_'+postobj.thumbnailurl
                        original_img = mainUrl1+postobj.thumbnailurl                        
                    elif postobj.thumbnailurl and postobj.type=='D':
                        small_thumb = mainUrl+postobj.thumbnailurl
                        medium_thumb = mainUrl+postobj.thumbnailurl
                        original_img = mainUrl+postobj.thumbnailurl
                    else:
                        original_img = small_thumb = medium_thumb = ''
                    if postobj.createdate:                           
                        createdate = getDate(postobj.createdate)
                    else:                            
                        createdate = getDate(datetime.utcnow())
                                                    
                    if postobj.profileid.lastname:
                        postedBy = postobj.profileid.firstname + " " + postobj.profileid.lastname
                    else:
                        postedBy = postobj.profileid.firstname
                                                                
                    profile = Profiles.objects.get(userid=postobj.profileid.userid.id)                    
                                                                                        
                     # Total Likes
                    totalLikes = Postlikes.objects.filter(postid=postobj)
                    myLikes = Postlikes.objects.filter(postid=postobj,profileid=Profile)
                    
                                                                        
                    # Total Comments
                    totalComment = Comments.objects.filter(postid=postobj)
                    
                     # Total Favorite
                    totalFavorites = Favorites.objects.filter(postid=postobj,type='F')
                    myFavorites = Favorites.objects.filter(postid=postobj,profileid=Profile,type='F')
                    try:                                
                        isMyFavorites = Favorites.objects.get(postid=postobj,profileid=Profile,type='F')
                        isMyFavorites = 1
                    except Favorites.DoesNotExist:
                        isMyFavorites = 0
                    
                    totalBoomark = Favorites.objects.filter(postid=postobj,type='B')
                    myBookmark = Favorites.objects.filter(postid=postobj,profileid=Profile,type='B')
                    try:                                
                        isMyBookmark = Favorites.objects.get(postid=postobj,profileid=Profile,type='B')
                        isMyBookmark = 1
                    except Favorites.DoesNotExist:
                        isMyBookmark = 0
                    
                    totalFavoritesRecord = Favorites.objects.filter(postid=postobj)
                    
                    try:
                        postst = Poststatistics.objects.get(postid=postobj)
                        totalview = postst.totalview
                        totalrating = postst.totalrating
                        totallike = postst.totallike
                        totalsharing = postst.totalsharing
                    except:
                        totalview = 0
                        totalrating = 0
                        totallike = 0
                        totalsharing = 0
                                                                                
                    field.append(
                        {
                            'id':postobj.id,
                            'title':postobj.title, 
                            'description':postobj.description, 
                            'scope' : postobj.scope, 
                            'type' : postobj.type,
                            'posturl' : postobj.posturl,
                            'vimeoId' : postobj.length, 
                            'profileid' : postobj.profileid.id,
                            'userid' : postobj.profileid.userid.id,                               
                            'totalView': totalview,
                            'totalRating':totalrating,
                            'totalLike': totallike,
                            'totalSharing': totalsharing,                                
                            'createdate' : createdate, 
                            'small_thumb' : small_thumb,
                            'medium_thumb' : medium_thumb,
                            'original_img':original_img,
                            'postedBy' :  postedBy,
                            'companyname':postobj.profileid.companyname,
                            'myLikes':len(myLikes),
                            'myFavorites':len(myFavorites),
                            'totalLikes':len(totalLikes),
                            'totalComment':len(totalComment),
                            'totalFavorites':len(totalFavorites),
                            'totalBoomark':len(totalBoomark),
                            'myBookmark':len(myBookmark),
                            'totalFavoritesRecord':len(totalFavoritesRecord),
                            'isMyFavorites':isMyFavorites,
                            'isMyBookmark':isMyBookmark
                        }
                    )
            else:
                totalPost = ''
            
            
            if productList:
                productList = len(productList)
                pimageUrl = settings.BASE_URL + settings.STATIC_URL+ settings.PRODUCT_MEDIA_URL
                pthumburl = pimageUrl+'thumbs/'
                for pobj in productList:
                    
                    if pobj.imageurl:
                        small_thumb = pthumburl+'small_'+pobj.imageurl
                        medium_thumb = pthumburl+'medium_'+pobj.imageurl
                        original_img = pimageUrl+pobj.imageurl       
                    else:
                        original_img = small_thumb = medium_thumb = ''
                    if pobj.createdate:                           
                        createdate = getDate(pobj.createdate)
                    else:                            
                        createdate = getDate(datetime.utcnow())
                    
                    if pobj.profileid.lastname:
                        postedBy = pobj.profileid.firstname + " " + pobj.profileid.lastname
                    else:
                        postedBy = pobj.profileid.firstname
                                                        
                    try:
                        productst = Productstatistics.objects.get(productid=pobj)
                        totalview = productst.totalview
                        totalrating = ''
                        totallike = ''
                        totalsharing = productst.totalsharing
                    except:
                        totalview = totalrating = totallike = totalsharing= ''                        
                    
                    pfield.append(
                    {
                        'id':pobj.id,
                        'title':pobj.title, 
                        'description':pobj.description, 
                        'scope' : 0, 
                        'type' : 'P',
                        'posturl' : '',
                        'vimeoId' : '', 
                        'profileid' : pobj.profileid.id,
                        'userid' : pobj.profileid.userid.id,                               
                        'totalView':totalview,
                        'totalRating':'',
                        'totalLike':'',
                        'totalSharing':totalsharing,                                
                        'createdate' : createdate, 
                        'small_thumb' : small_thumb,
                        'medium_thumb' : medium_thumb,
                        'original_img':original_img,
                        'postedBy' :  postedBy,
                        'companyname':pobj.profileid.companyname,
                        'myLikes':'',
                        'myFavorites':'',
                        'totalLikes':'',
                        'totalComment':'',
                        'totalFavorites':'',
                        'totalBoomark':'',
                        'myBookmark':'',
                        'totalFavoritesRecord':'',
                    }
                )
            else:
                totlProducts = ''                        
            return json_response({'status':'success','result':json.dumps(field),'topProduct':json.dumps(pfield),'totalpost':totalPost,'totalproduct':totlProducts}, status=200)                    
        except Profiles.DoesNotExist:
            return json_response({'status':'error','msg':'Invalid User Id'}, status=200)
    else:
        return json_response({
            'status':'error',
            'msg': 'Invalid User Id'
        }, status=200)       
        