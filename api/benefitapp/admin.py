from django.contrib import admin
from django import forms
from django.forms import ModelForm, Textarea
from rest_framework.response import Response
from benefitapp.models import Category,Users,Profiles,Followings,Post,Comments,Postlikes,Postratings,Favorites,Products,Albums,Postcategory,Imagetag,Poststatistics,Profilecategory,Productstatistics,Purchaseproduct
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
from rest_framework.views import APIView
import json
from django.db.models import Q
from benefitapp.utils import json_response, token_required, apikey_required,sendmail,decode_base64,make_thumbnil,upload_image,getDate
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse


admin.site.unregister(User)
admin.site.unregister(Group)
admin.site.unregister(Token)

class ProfileDetailView_NotUsed(TemplateView):   
    template_name = "admin/user_detail.html"    
    def get_context_data(self, **kwargs):        
        context = super(ProfileDetailView, self).get_context_data(**kwargs)        
        userId = self.kwargs['user_id']
        catfield = []  
        if userId:            
            try:
                profile = Profiles.objects.get(userid=userId)                  
                profilecategory = Profilecategory.objects.filter(profileid=profile)                
                profileimg = mediumthumbimg = smallthumbimg = ''                    
                if profile.profilephoto:
                    profileimg = settings.BASE_URL + settings.STATIC_URL+ settings.MEDIA_URL + profile.profilephoto                        
                    mediumthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/medium_'+profile.profilephoto
                    smallthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/small_'+profile.profilephoto
                
                # Total followers
                totalFollowers = Followings.objects.filter(followingprofileid=profile)                
                                                            
                #Total Text Post
                totalText = Post.objects.filter(profileid=profile,type='T')
                
                #Total Video Post
                totalVideo = Post.objects.filter(profileid=profile,type='V')
                
                #Total Image Post
                totalImage = Post.objects.filter(profileid=profile,type='I')
                
                #Total All Post
                totalAllPost = Post.objects.filter(profileid=profile)
                
                if profilecategory:
                    for pCat in profilecategory:
                        catfield.append({
                            'catId':pCat.categoryid.id,
                            'catName':pCat.categoryid.name,                           
                        })     
                
                context['userid'] = profile.userid.id
                context['profileid'] = profile.id
                context['email'] = profile.userid.email
                context['firstname'] = profile.firstname
                context['lastname'] = profile.lastname                
                context['gender'] = profile.gender
                context['age'] = profile.age                
                context['location'] = profile.location
                context['about'] = profile.bio                
                context['image'] = profileimg
                context['mediumthumb'] = mediumthumbimg
                context['smallthumb'] = smallthumbimg
                context['categorylist'] = catfield                
                #context['profilecategory'] = profilecatdata
                context['totalFollowers'] = len(totalFollowers)            
                context['totalText'] = len(totalText)
                context['totalVideo'] = len(totalVideo)
                context['totalImage'] = len(totalImage)
                context['totalAllPost'] = len(totalAllPost)                                        
            except Profiles.DoesNotExist:
                context['result'] = 'Invalid user id'
        else:
            context['result'] = 'Invalid Userid'
        return context

class PostDetailView(TemplateView):
    template_name = "admin/post_detail.html"
    model = Post    

    def get_context_data(self, **kwargs):        
        context = super(PostDetailView, self).get_context_data(**kwargs)
        #context['book_list'] = self.post_id
        postId = self.kwargs['post_id']
        if postId:
            context['postid'] = postId
            try:
                post = Post.objects.get(id=postId)
                if post.createdate:
                    post_createdate = getDate(post.createdate)
                else:
                    post_createdate = 'N/A'
                thumburl = settings.BASE_URL + settings.STATIC_URL+ settings.POST_MEDIA_URL+'thumbs/'
                                
                if post.thumbnailurl:
                    small_thumb = thumburl+'small_'+post.thumbnailurl
                    medium_thumb = thumburl+'medium_'+post.thumbnailurl
                else:
                    small_thumb = ''
                    medium_thumb = ''
                
                # CategoryList
                try:
                    cat_list = []
                    categorylist = Postcategory.objects.filter(postid=post)
                    for catObj in categorylist:
                        cat_list.append({'id':catObj.categoryid.id,'title':catObj.categoryid.name})                                       
                except Postcategory.DoesNotExist:
                    cat_id_in = ''
                    
                # TagList               
                try:
                    tag_list = []
                    tagList = Imagetag.objects.filter(postid=post)
                    for tagObj in tagList:
                        tag_list.append({'id':tagObj.id,'tagtext':tagObj.tagtext})                                        
                except Imagetag.DoesNotExist:
                    tag_id_in = ''
                
                # Total Likes
                totalLikes = Postlikes.objects.filter(postid=postId)
                
                # Total Comments
                totalComment = Comments.objects.filter(postid=postId)
                field = []
                if totalComment:
                    for cmtObj in totalComment:
                        createdate = getDate(cmtObj.createdate)
                        if cmtObj.profileid.profilephoto:
                            mediumthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/medium_'+cmtObj.profileid.profilephoto
                            smallthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/small_'+cmtObj.profileid.profilephoto
                        else:
                            smallthumbimg = mediumthumbimg = ''                        
                        field.append(
                            {
                                'id':cmtObj.id,
                                'comment':cmtObj.comment,
                                'commentOn':createdate, 
                                'postid' : cmtObj.postid.id, 
                                'userid' : cmtObj.profileid.userid.id, 
                                'commentBy' : cmtObj.profileid.firstname,
                                'user_small_img' : smallthumbimg,
                                'user_medium_img' : mediumthumbimg,                                     
                            }
                        )  
                
                context['title'] = post.title
                context['description'] = post.description
                context['createdate'] = post_createdate
                context['scope'] = post.scope
                context['type'] = post.type
                context['post_owner_id'] = post.profileid.userid.id
                context['category'] = cat_list
                context['post_small_thumb'] = small_thumb
                context['post_medium_thumb'] = medium_thumb
                context['tagList'] = tag_list
                context['totalLikes'] = len(totalLikes)                
                context['totalComment'] = len(totalComment)
                context['comments'] = field               
            except Post.DoesNotExist:
                context['result'] = 'Invalid'
        else:
            context['result'] = 'Invalid'
        return context
    
class UserView(TemplateView):  #APIView
            
    def post(self, request,format=None):
        searchText = request.POST.get("search[value]")
        orderval = request.POST.get("order[0][column]")        
        filterByStatus = request.POST.get("columns[6][search][value]")        
        array ={'0':'firstname','1':'location','2':'age','3':'firstname','4':'firstname','5':'firstname','6':'userid__is_active'}
        orderWith = request.POST.get("order[0][dir]")       
        if orderval in array:
            if orderWith=='desc':
                orderBy = '-%s' %(str(array[orderval]))
            else:
                orderBy = array[orderval]            
        else:
            orderBy = '-createdate'
        if searchText:
            if filterByStatus:
                usersList = Profiles.objects.filter((Q(firstname__icontains=searchText) | Q(lastname__icontains=searchText)),userid__is_active=filterByStatus).order_by(orderBy)
            else:
                usersList = Profiles.objects.filter(Q(firstname__icontains=searchText) | Q(lastname__icontains=searchText)).order_by(orderBy)
        else:
            if filterByStatus:                
                usersList = Profiles.objects.filter(userid__is_active=filterByStatus).order_by(orderBy)
            else:
                usersList = Profiles.objects.all().order_by(orderBy)
        draw = int (request.POST.get('draw', 1))
        page = int (request.POST.get('start'))
        recordsPerPage = int (request.POST.get('length', 10))
        if int(request.POST.get('start'))>0:
            page = (int (request.POST.get('start'))/recordsPerPage)+1
        else:
            page = 1
            
        field = []
        paginator = Paginator(usersList, recordsPerPage)
        try:
            userObj = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            userObj = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            userObj = paginator.page(paginator.num_pages)
            
        for pObj in userObj:
            if pObj.lastname:
                postedBy = pObj.firstname + " " + pObj.lastname
            else:
                postedBy = pObj.firstname
                
            #postedBy = format_html("<a href='userdetail/"+str(pObj.id)+"'>"+postedBy+"</a>")  # This link redirect to a new saparate page with this function ProfileDetailView_NotUsed
            
            postedBy = format_html("<a href='#' onclick='getUserDetailPopUp("+str(pObj.userid.id)+")'>"+postedBy+"</a>")
            
            if pObj.userid.is_active==1:
                action = format_html("<a href='javascript:void(0)' onclick='setUserStatus("+str(pObj.userid.id)+",0)' id='s"+str(pObj.userid.id)+"' class='active_user'>Deactive</a>")
            elif pObj.userid.is_active==0:
                action = format_html("<a href='javascript:void(0)' onclick='setUserStatus("+str(pObj.userid.id)+",1)' id='s"+str(pObj.userid.id)+"' class='deactive_user'>Active</a>")
            else:
                action = format_html("<a href='javascript:void(0)' onclick='setUserStatus("+str(pObj.userid.id)+",1)' id='s"+str(pObj.userid.id)+"' class='active_user'>Deactive</a>")
             
             
            # Is celebrity               
            if pObj.iscelebrity==1:
                iscelebrity = format_html("<a href='javascript:void(0)' onclick='setCelebrityStatus("+str(pObj.id)+",0)' id='c"+str(pObj.id)+"' class='active_user'>No</a>")
            elif pObj.iscelebrity==0:
                iscelebrity = format_html("<a href='javascript:void(0)' onclick='setCelebrityStatus("+str(pObj.id)+",1)' id='c"+str(pObj.id)+"' class='deactive_user'>Yes</a>")
            else:
                iscelebrity = format_html("<a href='javascript:void(0)' onclick='setCelebrityStatus("+str(pObj.id)+",1)' id='c"+str(pObj.id)+"' class='active_user'>No</a>")
                
            # Total followers
            totalFollowers = Followings.objects.filter(followingprofileid=pObj.id)                
                                                                            
            #Total Video Post
            totalVideo = Post.objects.filter(profileid=pObj.id,type='V')
            userPost = format_html("<a href='post?userid="+str(pObj.id)+"'>"+str(len(totalVideo))+"</a>")
            
            #Total Products Post
            totalProducts = Products.objects.filter(profileid=pObj.id)
            userProduct = format_html("<a href='product?userid="+str(pObj.id)+"'>"+str(len(totalProducts))+"</a>")
        
            field.append({                          
                       'name':postedBy,                     
                       'location':pObj.location,
                       'age':pObj.age,
                       'follower':len(totalFollowers),
                       'video':userPost,
                       'products':userProduct,
                       'iscelebrity':iscelebrity,
                       'action':action, 
                    })                
        return JsonResponse({'draw':draw,'recordsTotal':len(usersList),'search':searchText,'orderBy':orderBy,'page':page,'recordsPerPage':recordsPerPage,'recordsFiltered':len(usersList),'data':field})        
        
class setStatus(APIView):
    def post(self, request,user_id,statusval,format=None):
        if user_id.isnumeric():            
            user = Users.objects.get(id=user_id)           
            user.is_active = statusval
            user.save()
            return json_response({'msg':'changes','status':statusval})
        else:
            return json_response({'failed'})
        
class setCelebrity(APIView):
    def post(self, request,profile_id,statusval,format=None):
        if profile_id.isnumeric():            
            profile = Profiles.objects.get(id=profile_id)           
            profile.iscelebrity = statusval
            profile.save()
            return json_response({'msg':'changes','status':statusval})
        else:
            return json_response({'failed'})

class setPostStatus(APIView):
    def post(self, request,post_id,statusval,format=None):        
        if post_id.isnumeric():            
            post = Post.objects.get(id=post_id)           
            post.poststatus = statusval
            post.save()
            return json_response({'msg':'changes','status':statusval})
        else:
            return json_response({'failed'})
        

class ProductView(ListView):
    model = Products
    template_name = "admin/product_list.html"    
    def post(self, request,format=None):                   
        mainUrl = settings.BASE_URL + settings.STATIC_URL+ settings.PRODUCT_MEDIA_URL    
        thumburl = mainUrl+'thumbs/'
        field = []                
        draw = int (request.POST.get('draw', 1))
        page = int (request.POST.get('start'))
        recordsPerPage = int (request.POST.get('length', 10))
        if int(request.POST.get('start'))>0:
            page = (int (request.POST.get('start'))/recordsPerPage)+1
        else:
            page = 1
        
        searchText = request.POST.get("search[value]")
        userId = request.POST.get("userid")
        if userId=='all':
            if searchText:
                productList = Products.objects.filter(Q(title__icontains=searchText) | Q(description__icontains=searchText) | Q(profileid__firstname__icontains=searchText) | Q(profileid__lastname__icontains=searchText))
            else:
                productList = Products.objects.all()
        else:
            if searchText:
                productList = Products.objects.filter(Q(title__icontains=searchText) | Q(description__icontains=searchText) | Q(profileid__firstname__icontains=searchText) | Q(profileid__lastname__icontains=searchText),profileid=userId)
            else:
                productList = Products.objects.filter(profileid=userId)
        
        paginator = Paginator(productList, recordsPerPage)
        try:
            productObj = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            productObj = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            productObj = paginator.page(paginator.num_pages)
            
        for pObj in productObj:
            if pObj.profileid.lastname:
                postedBy = pObj.profileid.firstname + " " + pObj.profileid.lastname
            else:
                postedBy = pObj.profileid.firstname
            
            if pObj.profileid.userid.is_active==1:
                action = format_html("<a href='javascript:void(0)' onclick='setUserStatus("+str(pObj.profileid.userid.id)+",0)' id='s"+str(pObj.profileid.userid.id)+"'>Deactive</a>")
            elif pObj.profileid.userid.is_active==0:
                action = format_html("<a href='javascript:void(0)' onclick='setUserStatus("+str(pObj.profileid.userid.id)+",1)' id='s"+str(pObj.profileid.userid.id)+"'>Active</a>")
            else:
                action = format_html("<a href='javascript:void(0)' onclick='setUserStatus("+str(pObj.profileid.userid.id)+",0)' id='s"+str(pObj.profileid.userid.id)+"'>Deactive</a>")
                
                    
            if pObj.createdate:
                createdate = datetime.strftime(pObj.createdate, "%m/%d/%Y") 
            else:
                createdate =  datetime.strftime(datetime.now(),"%m/%d/%Y")
            
            
            if pObj.profileid.profilephoto:
                mediumthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/medium_'+pObj.profileid.profilephoto
                smallthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/small_'+pObj.profileid.profilephoto
            else:
                smallthumbimg = mediumthumbimg = ''
                
            
            if pObj.imageurl:
                small_thumb = thumburl+'small_'+pObj.imageurl
                medium_thumb = thumburl+'medium_'+pObj.imageurl
                original_img = mainUrl+pObj.imageurl            
            else:
                small_thumb = ''
                medium_thumb = ''
                original_img = ''
                                
            # Total followers
            totalFollowers = Followings.objects.filter(followingprofileid=pObj.profileid.id)
            
            #Total Video Post
            totalVideo = Post.objects.filter(profileid=pObj.profileid.id,type='V')
            
             #Total Text Post
            totalText = Post.objects.filter(profileid=pObj.profileid.id,type='T')
            
             #Total Products Post
            totalProducts = Products.objects.filter(profileid=pObj.profileid.id)
            
             #Total Products Post
            totalProductsSold = Purchaseproduct.objects.filter(profileid=pObj.profileid.id)
            
             # Total comments
            totalComment = Comments.objects.filter(postid=pObj.id)
            
             # Total likes
            totalLikes = Postlikes.objects.filter(postid=pObj.id)
            
             # Total View
            try:
                pstatistics = Productstatistics.objects.get(productid=pObj.id)
                totalView = pstatistics.totalview
            except Productstatistics.DoesNotExist:
                totalView = 0
            
                    
            field.append({                          
                'title':pObj.title,                     
                'description':pObj.description,
                'price':pObj.price,
                'postedBy':postedBy,                     
                'action':action,
                'totalFollowers':len(totalFollowers),                     
                'totalVideo':len(totalVideo),
                'totalText':len(totalText),
                'totalProducts':len(totalProducts),
                'totalComment':len(totalComment),
                'totalLikes':len(totalLikes),
                'totalProductsSold':len(totalProductsSold),
                'productimg_small':small_thumb,
                'productimg_meidum':medium_thumb,
                'productimg_original':original_img,
                'smallthumbimg':smallthumbimg,
                'mediumthumbimg':mediumthumbimg,
                'createdate':createdate,               
                'totalView':totalView,
            })       
        return JsonResponse({'draw':draw,'recordsTotal':len(productList),'recordsFiltered':len(productList),'page':page,'recordsPerPage':recordsPerPage,'data':field})     

class PostView(ListView):
    model = Post
    template_name = "admin/post_list.html"
    def post(self, request,format=None):
        
        searchText = request.POST.get("search[value]")
        userId = request.POST.get("userid")
        if userId=='all':
            if searchText:
                postList = Post.objects.filter(Q(title__icontains=searchText) | Q(description__icontains=searchText) | Q(profileid__firstname__icontains=searchText) | Q(profileid__lastname__icontains=searchText))
            else:
                postList = Post.objects.all()
        else:
            if searchText:
                postList = Post.objects.filter((Q(title__icontains=searchText) | Q(description__icontains=searchText) | Q(profileid__firstname__icontains=searchText) | Q(profileid__lastname__icontains=searchText)),profileid=userId,type='V')
            else:
                postList = Post.objects.filter(profileid=userId,type='V')
                                
        mainUrl = settings.BASE_URL + settings.STATIC_URL+ settings.POST_MEDIA_URL    
        thumburl = mainUrl+'thumbs/'    
        recordsPerPage = int (request.POST.get('length', 10))                
        draw = int (request.POST.get('draw', 1))
        page = int (request.POST.get('start'))
        recordsPerPage = int (request.POST.get('length', 10))
        if int(request.POST.get('start'))>0:
            page = (int (request.POST.get('start'))/recordsPerPage)+1
        else:
            page = 1
            
        field = []
        paginator = Paginator(postList, recordsPerPage)
        try:
            postObj = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            postObj = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            postObj = paginator.page(paginator.num_pages)        
            
        for pObj in postObj:
            if pObj.profileid.lastname:
                postedBy = pObj.profileid.firstname + " " + pObj.profileid.lastname
            else:
                postedBy = pObj.profileid.firstname
            
            if pObj.profileid.userid.is_active==1:
                action = format_html("<a href='javascript:void(0)' onclick='setUserStatus("+str(pObj.profileid.userid.id)+",0)' id='s"+str(pObj.profileid.userid.id)+"'>Deactive</a>")
            elif pObj.profileid.userid.is_active==0:
                action = format_html("<a href='javascript:void(0)' onclick='setUserStatus("+str(pObj.profileid.userid.id)+",1)' id='s"+str(pObj.profileid.userid.id)+"'>Active</a>")
            else:
                action = format_html("<a href='javascript:void(0)' onclick='setUserStatus("+str(pObj.profileid.userid.id)+",0)' id='s"+str(pObj.profileid.userid.id)+"'>Deactive</a>")
                
            
            if pObj.poststatus==1:
                poststatus = format_html("<span id='blockpost'><a href='javascript:void(0)' onclick='setPostStatus("+str(pObj.id)+",0)' id='p"+str(pObj.id)+"'>Block Post</a></span>")
            elif pObj.poststatus==0:
                poststatus = format_html("<span id='unblockpost'><a href='javascript:void(0)' onclick='setPostStatus("+str(pObj.id)+",1)' id='p"+str(pObj.id)+"'>Unblock Post</a></span>")
            else:
                poststatus = format_html("<span id='blockpost'><a href='javascript:void(0)' onclick='setPostStatus("+str(pObj.id)+",0)' id='p"+str(pObj.id)+"'>Block Post</a></span>")
            
            if pObj.createdate:
                createdate = datetime.strftime(pObj.createdate, "%m/%d/%Y") #postobj[10].strftime('%m/%d/%Y')
            else:
                createdate =  datetime.strftime(datetime.now(),"%m/%d/%Y")
            
            
            if pObj.profileid.profilephoto:
                mediumthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/medium_'+pObj.profileid.profilephoto
                smallthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/small_'+pObj.profileid.profilephoto
            else:
                smallthumbimg = mediumthumbimg = ''
                
            
            if pObj.thumbnailurl and pObj.type=='I':
                small_thumb = thumburl+'small_'+pObj.thumbnailurl
                medium_thumb = thumburl+'medium_'+pObj.thumbnailurl
                original_img = mainUrl+pObj.thumbnailurl
            elif pObj.thumbnailurl and pObj.type=='V':
                mainUrl1 = settings.BASE_URL + settings.STATIC_URL+ settings.VIMEO_URL
                thumburl1 = mainUrl1+'thumbs/'                
                small_thumb = thumburl1+'small_'+pObj.thumbnailurl
                medium_thumb = thumburl1+'medium_'+pObj.thumbnailurl
                original_img = mainUrl1+pObj.thumbnailurl                                
                #small_thumb = pObj.thumbnailurl
                #medium_thumb = pObj.thumbnailurl
                #original_img = pObj.thumbnailurl
            elif pObj.thumbnailurl and pObj.type=='D':
                small_thumb = mainUrl+pObj.thumbnailurl
                medium_thumb = mainUrl+pObj.thumbnailurl
                original_img = mainUrl+pObj.thumbnailurl
            else:
                small_thumb = ''
                medium_thumb = ''
                original_img = ''
                                
            # Total followers
            totalFollowers = Followings.objects.filter(followingprofileid=pObj.profileid.id)
            
            #Total Video Post
            totalVideo = Post.objects.filter(profileid=pObj.profileid.id,type='V')
            
             #Total Text Post
            totalText = Post.objects.filter(profileid=pObj.profileid.id,type='T')
            
             #Total Products Post
            totalProducts = Products.objects.filter(profileid=pObj.profileid.id)
            
             # Total comments
            totalComment = Comments.objects.filter(postid=pObj.id)
            
             # Total likes
            totalLikes = Postlikes.objects.filter(postid=pObj.id)
            
             # Total View
            try:
                poststatistics = Poststatistics.objects.get(postid=pObj.id)
                totalView = poststatistics.totalview
            except Poststatistics.DoesNotExist:
                totalView = 0
            
            # CategoryList
            cat_list = []
            categorylist = Postcategory.objects.filter(postid=pObj.id)
            if len(categorylist)>0:
                for catObj in categorylist:
                    cat_list.append(catObj.categoryid.name)                    
                cat_id_in = ','.join(map(str, cat_list))
            else:
                cat_id_in = 'N/A'
            
             # TagList
            tag_list = []
            tagList = Imagetag.objects.filter(postid=pObj.id)
            if len(tagList)>0:
                for tagObj in tagList:
                    tag_list.append(tagObj.tagtext)                    
                tag_id_in = ','.join(map(str, tag_list))
            else:
                tag_id_in = 'N/A'
            
            field.append({                          
                'title':pObj.title,                     
                'description':pObj.description,
                'postedBy':postedBy,                     
                'action':action,
                'totalFollowers':len(totalFollowers),                     
                'totalVideo':len(totalVideo),
                'totalText':len(totalText),
                'totalProducts':len(totalProducts),
                'totalComment':len(totalComment),
                'totalLikes':len(totalLikes),
                'categoryList':cat_id_in,
                'tagList':tag_id_in,
                'postimg_small':small_thumb,
                'postimg_meidum':medium_thumb,
                'postimg_original':original_img,
                'smallthumbimg':smallthumbimg,
                'mediumthumbimg':mediumthumbimg,
                'createdate':createdate,
                'poststatus':poststatus,
                'totalView':totalView,
            })  
        return JsonResponse({'draw':draw,'start':page,'recordsTotal':len(postList),'recordsFiltered':len(postList),'data':field})
    
    
class ProfileDetailView(TemplateView):
    def get(self, request,user_id,format=None):
        if user_id:            
            try:
                profile = Profiles.objects.get(userid=user_id)                  
                profilecategory = Profilecategory.objects.filter(profileid=profile)                
                profileimg = mediumthumbimg = smallthumbimg = ''                    
                if profile.profilephoto:
                    profileimg = settings.BASE_URL + settings.STATIC_URL+ settings.MEDIA_URL + profile.profilephoto                        
                    mediumthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/medium_'+profile.profilephoto
                    smallthumbimg = settings.BASE_URL + settings.STATIC_URL+settings.MEDIA_URL+'thumbs/small_'+profile.profilephoto
                
                # Total followers
                totalFollowers = Followings.objects.filter(followingprofileid=profile)                
                                                            
                #Total Text Post
                totalText = Post.objects.filter(profileid=profile,type='T')
                
                #Total Video Post
                totalVideo = Post.objects.filter(profileid=profile,type='V')
                
                #Total Image Post
                totalImage = Post.objects.filter(profileid=profile,type='I')
                
                #Total All Post
                totalAllPost = Post.objects.filter(profileid=profile)
                
                     
                return JsonResponse({'userid':profile.userid.id,'profileid':profile.id,'email':profile.userid.email,'referalcode':profile.referalcode,'firstname':profile.firstname,'lastname':profile.lastname,'gender':profile.gender,'age':profile.age,'location':profile.location,'about':profile.bio,'image':profileimg,'mediumthumb':mediumthumbimg,'smallthumb':smallthumbimg,'totalFollowers':len(totalFollowers),'totalText':len(totalText),'totalVideo':len(totalVideo),'totalImage':len(totalImage),'totalAllPost':len(totalAllPost)})                                       
            except Profiles.DoesNotExist:
                return JsonResponse({'status':'error','msg':'Invalid User Id'})
        else:
            return JsonResponse({'status':'error','msg':'Invalid User Id'})    
        



