from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

from benefitapp.serializers import UserSerializer
from benefitapp.models import Category,Users,Profiles,Followings,Post,Comments,Postlikes,Postratings,Favorites,Products,Albums,Postcategory,Imagetag,Poststatistics,Commentlikes,Userblock,Productstatistics,Purchaseproduct
from django.db import IntegrityError
from django.core import serializers
from django.db.models import Q
from benefitapp.utils import json_response, token_required, apikey_required,sendmail,decode_base64,make_thumbnil,upload_image,getDate,documentsUpload,chekPrice
from datetime import datetime
from django.db import connection
import vimeo
import json
import base64
import time
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
import os
from itertools import chain
from operator import attrgetter
    

class getFeedList(APIView):
    
    """
    Get feed page list
    
    @method GET
    @access	private
    @param	integer user_id
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id,format=None):
            page = int (request.GET.get('page', 1))  
            recordsPerPage = int (request.GET.get('recordsPerPage', 10))
            feedType = request.GET.get('feedType', 'A')
            searchText = request.GET.get('searchText', None)            
            isFollow = isFavorite = isSaveForLater = False                              
            field = []            
            if user_id.isnumeric():
                try:
                    user = Profiles.objects.get(userid=user_id)
                    followingUsers = Followings.objects.filter(profileid=user)
                    """
                    if len(followingUsers)>0:
                        if searchText:
                            if feedType!='A':
                                if feedType=='P':
                                    productList = Products.objects.filter(profileid__in=[p.followingprofileid for p in followingUsers],title__icontains=searchText).order_by('-createdate')
                                    postList = ''
                                else:
                                    postList = Post.objects.filter(profileid__in=[p.followingprofileid for p in followingUsers],type=feedType,title__icontains=searchText).order_by('-createdate')
                                    productList = ''
                            else:
                                postList = Post.objects.filter(profileid__in=[p.followingprofileid for p in followingUsers],title__icontains=searchText) .order_by('-createdate')                   
                                productList = Products.objects.filter(profileid__in=[p.followingprofileid for p in followingUsers],title__icontains=searchText).order_by('-createdate')
                        else:
                            if feedType!='A':
                                if feedType=='P':
                                    productList = Products.objects.filter(profileid__in=[p.followingprofileid for p in followingUsers]).order_by('-createdate')
                                    postList = ''
                                else:
                                    postList = Post.objects.filter(profileid__in=[p.followingprofileid for p in followingUsers],type=feedType).order_by('-createdate')
                                    productList = ''
                            else:
                                postList = Post.objects.filter(profileid__in=[p.followingprofileid for p in followingUsers]) .order_by('-createdate')                   
                                productList = Products.objects.filter(profileid__in=[p.followingprofileid for p in followingUsers]).order_by('-createdate')
                    else:
                        if searchText:
                            if feedType!='A':
                                if feedType=='P':
                                    productList = Products.objects.filter(title__icontains=searchText).order_by('-createdate')                                
                                    postList = ''
                                else:
                                    postList = Post.objects.filter(type=feedType,title__icontains=searchText).order_by('-createdate')
                                    productList = ''                        
                            else:
                                postList = Post.objects.filter(title__icontains=searchText).order_by('-createdate')
                                productList = Products.objects.filter(title__icontains=searchText).order_by('-createdate')
                        else:
                            if feedType!='A':
                                if feedType=='P':
                                    productList = Products.objects.all().order_by('-createdate')
                                    postList = ''
                                else:
                                    postList = Post.objects.filter(type=feedType).order_by('-createdate')
                                    productList = ''                        
                            else:
                                postList = Post.objects.all().order_by('-createdate')
                                productList = Products.objects.all().order_by('-createdate')
                    """
                    
                    blockedUsers = Userblock.objects.filter(profileid=user)
                    if len(blockedUsers)>0:
                        product = Products.objects.filter(profileid__in=[p.blockedprofileid for p in blockedUsers])
                        post = Post.objects.filter(profileid__in=[p.blockedprofileid for p in blockedUsers])  
                        if searchText:
                            if feedType!='A':
                                if feedType=='P':                                    
                                    productList = Products.objects.filter(title__icontains=searchText).exclude(id__in=[p.pk for p in product]).order_by('-createdate')                                
                                    postList = ''
                                else:                                        
                                    postList = Post.objects.filter(poststatus=1,type=feedType,title__icontains=searchText).exclude(id__in=[p.pk for p in post]).order_by('-createdate')
                                    productList = ''                        
                            else:                            
                                postList = Post.objects.filter(~Q(type='D'),poststatus=1,title__icontains=searchText).exclude(id__in=[p.pk for p in post]).order_by('-createdate')                            
                                productList = Products.objects.filter(title__icontains=searchText).exclude(id__in=[p.pk for p in product]).order_by('-createdate')
                        else:
                            if feedType!='A':
                                if feedType=='P':
                                    productList = Products.objects.exclude(id__in=[p.pk for p in product]).order_by('-createdate')
                                    postList = ''
                                else:
                                    postList = Post.objects.filter(poststatus=1,type=feedType).exclude(id__in=[p.pk for p in post]).order_by('-createdate')                            
                                    productList = ''                        
                            else:
                                postList = Post.objects.filter(~Q(type='D'),poststatus=1).exclude(id__in=[p.pk for p in post]).order_by('-createdate')
                                productList = Products.objects.exclude(id__in=[p.pk for p in product]).order_by('-createdate')
                    else:
                        if searchText:
                            if feedType!='A':
                                if feedType=='P':
                                    productList = Products.objects.filter(title__icontains=searchText).order_by('-createdate')                                
                                    postList = ''
                                else:
                                    postList = Post.objects.filter(poststatus=1,type=feedType,title__icontains=searchText).order_by('-createdate')
                                    productList = ''                        
                            else:
                                postList = Post.objects.filter(poststatus=1,title__icontains=searchText).exclude(type='D').order_by('-createdate')
                                productList = Products.objects.filter(title__icontains=searchText).order_by('-createdate')
                        else:
                            if feedType!='A':
                                if feedType=='P':
                                    productList = Products.objects.all().order_by('-createdate')
                                    postList = ''
                                else:
                                    postList = Post.objects.filter(poststatus=1,type=feedType).order_by('-createdate')                            
                                    productList = ''                        
                            else:
                                postList = Post.objects.filter(poststatus=1).exclude(type='D').order_by('-createdate')
                                productList = Products.objects.all().order_by('-createdate')
                                    
                    result_list = sorted(chain(productList, postList),key=attrgetter('createdate'),reverse=True)               
                    #result_list = list(chain(productList, postList))
                    
                    if len(result_list)>0:
                        count = len(result_list)
                        paginator = Paginator(result_list, recordsPerPage)
                        try:
                            postObj = paginator.page(page)
                        except PageNotAnInteger:                       
                            postObj = paginator.page(1)
                        except EmptyPage:                       
                            postObj = paginator.page(paginator.num_pages)
                                            
                        for pObj in postObj:
                            
                            if hasattr(pObj, 'thumbnailurl'):
                                mainUrl = settings.BASE_URL + settings.STATIC_URL+ settings.POST_MEDIA_URL
                                thumburl = mainUrl+'thumbs/'                            
                                if pObj.thumbnailurl and pObj.type=='I':
                                    small_thumb = thumburl+'small_'+pObj.thumbnailurl
                                    medium_thumb = thumburl+'medium_'+pObj.thumbnailurl
                                    original_img = mainUrl+pObj.thumbnailurl
                                elif pObj.thumbnailurl and pObj.type=='V':
                                    small_thumb = pObj.thumbnailurl
                                    medium_thumb = pObj.thumbnailurl
                                    original_img = pObj.thumbnailurl
                                elif pObj.thumbnailurl and pObj.type=='D':
                                    small_thumb = mainUrl+pObj.thumbnailurl
                                    medium_thumb = mainUrl+pObj.thumbnailurl
                                    original_img = mainUrl+pObj.thumbnailurl
                                else:
                                    original_img = small_thumb = medium_thumb = ''
                                
                                tableName = 'Post'
                            else:
                                pimageUrl = settings.BASE_URL + settings.STATIC_URL+ settings.PRODUCT_MEDIA_URL
                                pthumburl = pimageUrl+'thumbs/'          
                                if pObj.imageurl:
                                    small_thumb = pthumburl+'small_'+pObj.imageurl
                                    medium_thumb = pthumburl+'medium_'+pObj.imageurl
                                    original_img = pimageUrl+pObj.imageurl
                                else:
                                    original_img = small_thumb = medium_thumb = ''
                                
                                tableName = 'Products'
                            
                            
                            if hasattr(pObj, 'scope'):
                                scopeVal = pObj.scope
                            else:
                                scopeVal = 0
                                
                            if hasattr(pObj, 'type'):
                                typeVal = pObj.type
                            else:
                                typeVal = 'P'
                            
                            if hasattr(pObj, 'posturl'):
                                postUrl = pObj.posturl
                            else:
                                postUrl = ''
                            
                            if hasattr(pObj, 'length'):
                                vimeoId = pObj.length
                            else:
                                vimeoId = ''
                            
                            if pObj.createdate:                            
                                createdate = getDate(pObj.createdate)
                            else:                            
                                createdate = getDate(settings.CURRENTDATE)
                                
                            if pObj.profileid.lastname:
                                postedBy = pObj.profileid.firstname + " " + pObj.profileid.lastname
                            else:
                                postedBy = pObj.profileid.firstname
                            
                            
                            # Total Likes
                            totalLikes = Postlikes.objects.filter(postid=pObj.id)
                            myLikes = Postlikes.objects.filter(postid=pObj.id,profileid=user)
                            
                            # Total Comments
                            totalComment = Comments.objects.filter(postid=pObj.id)
                            
                             # Total Favorite
                            totalFavorites = Favorites.objects.filter(postid=pObj.id,type='F')
                            myFavorites = Favorites.objects.filter(postid=pObj.id,profileid=user,type='F')
                            
                            totalBoomark = Favorites.objects.filter(postid=pObj.id,type='B')
                            myBookmark = Favorites.objects.filter(postid=pObj.id,profileid=user,type='B')
                            
                            totalFavoritesRecord = Favorites.objects.filter(postid=pObj.id)
                            
                            if myFavorites:
                                isFavorite = True
                            else:
                                isFavorite = False
                            
                            if myBookmark:
                                isSaveForLater = True
                            else:
                                isSaveForLater = False
                                
                            field.append(
                                {
                                    'id':pObj.id,
                                    'title':pObj.title, 
                                    'description':pObj.description,                                
                                    'scope' : scopeVal,
                                    'type' : typeVal,
                                    'posturl' : postUrl,
                                    'vimeoId' : vimeoId,                                 
                                    'profileid' : pObj.profileid.id,
                                    'userid' : pObj.profileid.userid.id,
                                    'categoryid' : '',
                                    'createdate' : createdate,
                                    'small_thumb' : small_thumb,
                                    'medium_thumb' : medium_thumb,
                                    'original_img':original_img,                               
                                    'postedBy' :  postedBy,
                                    'myLikes':len(myLikes),
                                    'myFavorites':len(myFavorites),
                                    'totalLikes':len(totalLikes),
                                    'totalComment':len(totalComment),
                                    'totalFavorites':len(totalFavorites),
                                    'totalBoomark':len(totalBoomark),
                                    'myBookmark':len(myBookmark),
                                    'totalFavoritesRecord':len(totalFavoritesRecord),
                                    'isFavorite':isFavorite,
                                    'isSaveForLater':isSaveForLater,
                                    'tableName':tableName,
                                    
                                }
                            )
                        return json_response({'status':'success','result':json.dumps(field),'total':len(result_list),'count':count}, status=200)
                    else:
                        return json_response({'status':'error','msg':'No records found','result':'Record not found'}, status=200)
                except Profiles.DoesNotExist:
                    return json_response({'status':'error','msg':'Invalid User Id'}, status=200)
            else:
                return json_response({
                    'status':'error',
                    'msg': 'Invalid User Id'
                }, status=200)


class getUserOwnPost(APIView):
    
    """
    Get own post content
    
    @method GET
    @access	private
    @param	string feedType
    @param	string searchText
    @param	integer watcherId
    @return	json array
    """
    @apikey_required
    @token_required
    def get(self, request,user_id,format=None):            
        feedType = request.GET.get('feedType', 'A')
        page = int (request.GET.get('page', 1))  
        recordsPerPage = int(request.GET.get('recordsPerPage', 10))
        searchText = request.GET.get('searchText', None)
        watcherId = request.GET.get('watcherId', None)
        isFollow = isFavorite = isSaveForLater = False                      
        field = []
        if user_id.isnumeric():                
            try:
                user = Profiles.objects.get(userid=user_id)                                                                           
                if searchText:
                    if feedType!='A':
                        if feedType=='P':
                            productList = Products.objects.filter(profileid=user,title__icontains=searchText).order_by('-createdate')                                
                            postList = ''
                        else:
                            postList = Post.objects.filter(profileid=user,type=feedType,title__icontains=searchText).order_by('-createdate')
                            productList = ''                        
                    else:
                        postList = Post.objects.filter(profileid=user,title__icontains=searchText).order_by('-createdate')
                        productList = Products.objects.filter(profileid=user,title__icontains=searchText).order_by('-createdate')
                else:
                    if feedType!='A':
                        if feedType=='P':
                            productList = Products.objects.filter(profileid=user).order_by('-createdate')
                            postList = ''
                        else:
                            postList = Post.objects.filter(profileid=user,type=feedType).order_by('-createdate')
                            productList = ''                        
                    else:
                        postList = Post.objects.filter(profileid=user.id).order_by('-createdate')                    
                        productList = Products.objects.filter(profileid=user.id).order_by('-createdate')
                
                result_list = sorted(chain(productList, postList),key=attrgetter('createdate'),reverse=True)
                #result_list = list(chain(productList, postList))
                
                #Total followers
                totalFollowers = Followings.objects.filter(followingprofileid=user)
                
                # Total Text Post
                totalText = Post.objects.filter(profileid=user,type='T')
                
                # Total Video Post
                totalVideo = Post.objects.filter(profileid=user,type='V')
                
                # total Document        
                totalDocument= Post.objects.filter(profileid=user,type='D')
                
                # Total Image Post
                totalImage = Post.objects.filter(profileid=user,type='I')
                
                #Total Product
                totalProduct = Products.objects.filter(profileid=user)
                                            
                #Total All Post
                totalAllPost = Post.objects.filter(profileid=user.id)
                                                       
                if len(result_list)>0:               
                    count = len(result_list)
                    paginator = Paginator(result_list, recordsPerPage)
                    try:
                        postObj = paginator.page(page)
                    except PageNotAnInteger:                       
                        postObj = paginator.page(1)
                    except EmptyPage:                       
                        postObj = paginator.page(paginator.num_pages)
                        
                    for pObj in postObj:
                        if hasattr(pObj, 'thumbnailurl'):
                            mainUrl = settings.BASE_URL + settings.STATIC_URL+ settings.POST_MEDIA_URL
                            thumburl = mainUrl+'thumbs/'                            
                            if pObj.thumbnailurl and pObj.type=='I':
                                small_thumb = thumburl+'small_'+pObj.thumbnailurl
                                medium_thumb = thumburl+'medium_'+pObj.thumbnailurl
                                original_img = mainUrl+pObj.thumbnailurl
                            elif pObj.thumbnailurl and pObj.type=='V':
                                small_thumb = pObj.thumbnailurl
                                medium_thumb = pObj.thumbnailurl
                                original_img = pObj.thumbnailurl
                            elif pObj.thumbnailurl and pObj.type=='D':
                                small_thumb = mainUrl+pObj.thumbnailurl
                                medium_thumb = mainUrl+pObj.thumbnailurl
                                original_img = mainUrl+pObj.thumbnailurl
                            else:
                                original_img = small_thumb = medium_thumb = ''
                            
                            tableName = 'Post'
                        else:
                            pimageUrl = settings.BASE_URL + settings.STATIC_URL+ settings.PRODUCT_MEDIA_URL
                            pthumburl = pimageUrl+'thumbs/'          
                            if pObj.imageurl:
                                small_thumb = pthumburl+'small_'+pObj.imageurl
                                medium_thumb = pthumburl+'medium_'+pObj.imageurl
                                original_img = pimageUrl+pObj.imageurl
                            else:
                                original_img = small_thumb = medium_thumb = ''
                            
                            tableName = 'Products'
                        
                        
                        if hasattr(pObj, 'scope'):
                            scopeVal = pObj.scope
                        else:
                            scopeVal = 0
                            
                        if hasattr(pObj, 'type'):
                            typeVal = pObj.type
                        else:
                            typeVal = 'P'
                        
                        if hasattr(pObj, 'posturl'):
                            postUrl = pObj.posturl
                        else:
                            postUrl = ''
                        
                        if hasattr(pObj, 'length'):
                            vimeoId = pObj.length
                        else:
                            vimeoId = ''
                        
                        if pObj.createdate:                            
                            createdate = getDate(pObj.createdate)
                        else:                            
                            createdate = getDate(settings.CURRENTDATE)
                            
                        if pObj.profileid.lastname:
                            postedBy = pObj.profileid.firstname + " " + pObj.profileid.lastname
                        else:
                            postedBy = pObj.profileid.firstname
                    
                        # CategoryList
                        cat_list = []
                        categorylist = Postcategory.objects.filter(postid=pObj.id)
                        for catObj in categorylist:
                            cat_list.append(catObj.categoryid.id)                    
                        cat_id_in = ','.join(map(str, cat_list))
                        
                        
                        # Tags removed from benefit
                        """
                        # TagList
                        tag_list = []
                        tagList = Imagetag.objects.filter(postid=pObj.id)
                        for tagObj in tagList:
                            tag_list.append(tagObj.tagtext)                    
                        tag_id_in = ','.join(map(str, tag_list))
                        """
                        tag_id_in = ''
                    
                        # Total Likes
                        totalLikes = Postlikes.objects.filter(postid=pObj.id)                       
                        
                        # Total Comments
                        totalComment = Comments.objects.filter(postid=pObj.id)
                    
                        if watcherId:                       
                            watcherid = Profiles.objects.get(userid=watcherId)          
                            myFavorite = Favorites.objects.filter(postid=pObj.id,profileid=watcherid,type='F')
                            mySaveForLater = Favorites.objects.filter(postid=pObj.id,profileid=watcherid,type='B')  
                            if myFavorite:
                                isFavorite = 1
                            else:
                                isFavorite = 0
                            
                            if mySaveForLater:
                                isSaveForLater = 1
                            else:
                                isSaveForLater = 0
            
            
                        field.append(
                            {                        
                            'id':pObj.id,
                            'title':pObj.title, 
                            'description':pObj.description,                                
                            'scope' : scopeVal,
                            'type' : typeVal,
                            'posturl' : postUrl,
                            'vimeoId' : vimeoId,                                 
                            'profileid' : pObj.profileid.id,
                            'userid' : pObj.profileid.userid.id,                                            
                            'categoryid' : cat_id_in,
                            'tagList' : tag_id_in,
                            'createdate' : createdate, 
                            'small_thumb' : small_thumb,
                            'medium_thumb' : medium_thumb,
                            'original_img':original_img,
                            'totalComment':len(totalComment),
                            'totalLikes':len(totalLikes),
                            'isFavorite':isFavorite,
                            'isSaveForLater':isSaveForLater,
                            'tableName':tableName,
                            }
                        )
                    return json_response({'status':'success','result':json.dumps(field),'totalpost':len(totalAllPost),'totalfollowers':len(totalFollowers),
                                          'totalText':len(totalText),'totalVideo':len(totalVideo),'totalImage':len(totalImage),'totalDocument':len(totalDocument),'totalrows':len(result_list),'totalProduct':len(totalProduct)}, status=200)                   
                else:
                    return json_response({'status':'success','result':'Record not found','msg':'No records found','isFollow':isFollow,'totalpost':len(totalAllPost),'totalfollowers':len(totalFollowers),
                                          'totalText':len(totalText),'totalVideo':len(totalVideo),'totalImage':len(totalImage),'totalDocument':len(totalDocument),'totalrows':0,'totalProduct':len(totalProduct)}, status=200)
            except Profiles.DoesNotExist:
                return json_response({'status':'error','msg':'Invalid User Id'}, status=200)
        else:
            return json_response({
                'status':'error',
                'msg': 'Invalid User Id'
            }, status=200)
        




class purchaseProduct(APIView):
    
    """
    Insert category into master category table
    
    @method POST
    @access	private
    @param	integer userId
    @param  integer productId
    @param  integer price
    @param  string shipping
    @param	string description    
    @param  string tax
    @param	integer transactionId    
    @param  string paymentStatus
    @param	string platform    
    @param  string environment
    @param	string paypalSdkVersion
    @param  string intent
    @param	string paymentTime 
    @return	json array
    """
    #@apikey_required
    #@token_required
    def post(self, request, format=None):
        userId = request.POST.get('userId', None)
        productId = request.POST.get('productId', None)        
        price = request.POST.get('price', None)
        shipping = request.POST.get('shipping', None)        
        tax = request.POST.get('tax', None)
        transactionId = request.POST.get('transactionId', None)        
        paymentStatus = request.POST.get('paymentStatus', None)
        platform = request.POST.get('platform', None)        
        environment = request.POST.get('environment', None)
        paypalSdkVersion = request.POST.get('paypalSdkVersion', None)        
        intent = request.POST.get('intent', None)
        paymentTime = request.POST.get('paymentTime', None)
        subject = 'Product Purchase'
        templatePath = os.path.join(settings.BASE_DIR, 'templates/admin/email')
       
        if userId.isnumeric() and productId.isnumeric():
                if price:
                    isPrice = chekPrice(price)
                    if isPrice==False:
                        return json_response({'status':'success','msg':'Invalid Price,It should be number or decimal.'}, status=200)
                else:
                    price = 0.00
                
                if tax:
                    isTax = chekPrice(tax)
                    if isTax==False:
                        return json_response({'status':'success','msg':'Invalid Tax,It should be number or decimal.'}, status=200)
                else:
                    tax = 0.00
                try:
                    profile = Profiles.objects.get(userid=userId)
                    try:
                        product = Products.objects.get(id=productId)
                        try:
                            purchaseprd = Purchaseproduct.objects.get(transactionid=transactionId)                        
                            return json_response({'error':'error','msg':'transactionId already exist'}, status=200)      
                        except Purchaseproduct.DoesNotExist:
                            post = Purchaseproduct.objects.create(profileid=profile,productid=product,price=price,shipping=shipping,tax=tax,transactionid=transactionId,paymentstatus=paymentStatus,platform=platform,environment=environment,paypalsdkversion=paypalSdkVersion,intent=intent,paymenttime=paymentTime,createdate=settings.CURRENTDATE)
                            
                            # send notification to seller about product purchase
                            sellerMessage = render_to_string(templatePath+'/product_seller_notification.html', {'profileid': profile.id,'userid':profile.userid.id,'firstname':profile.firstname,'lastname':profile.lastname})                            
                            toProductOwner = product.profileid.userid.email
                            sendStatus = sendmail(subject,message,toProductOwner)
                            
                            # send notification to buyer about product purchase
                            buyerMessage = render_to_string(templatePath+'/product_buyer_notification.html', {'profileid': profile.id,'userid':profile.userid.id,'firstname':profile.firstname,'lastname':profile.lastname})
                            toProductBuyer = profile.userid.email
                            sendStatus = sendmail(subject,message,toProductBuyer)
                            
                            return json_response({'status':'success','msg':'Payment detail added successfully'}, status=200)
                    except Products.DoesNotExist:                    
                        return json_response({'error':'error','msg':'Invalid product id'}, status=200)
                except Profiles.DoesNotExist:
                    return json_response({'error':'error','msg':'Invalid user id'}, status=200)
        else:
            return json_response({
                'status':'error',
                 'msg': 'Invalid user id or product id'
            }, status=400)        
                