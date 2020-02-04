# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
from __future__ import unicode_literals

from django.db import models
from datetime import datetime
from django.core.validators import MinLengthValidator



class Comments(models.Model):
    id = models.IntegerField(primary_key=True)
    postid = models.ForeignKey('Post', db_column='PostId', blank=True, null=True)  # Field name made lowercase.
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    comment = models.CharField(db_column='Comment', max_length=500, blank=True, null=True)  # Field name made lowercase.
    parentcommentid = models.IntegerField(db_column='ParentCommentId', default=0)
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'comments'


class Documents(models.Model):
    id = models.IntegerField(primary_key=True)
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=75, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=500, blank=True, null=True)  # Field name made lowercase.
    docurl = models.CharField(db_column='DocUrl', max_length=100, blank=True, null=True)  # Field name made lowercase.
    scope = models.CharField(db_column='Scope', max_length=1, blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'documents'


class Favorites(models.Model):
    id = models.IntegerField(primary_key=True)
    postid = models.ForeignKey('Post', db_column='PostId', blank=True, null=True)  # Field name made lowercase.
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=1, default='F')  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'favorites'


class Followings(models.Model):
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', blank=True, null=True, related_name='+')  # Field name made lowercase.
    followingprofileid = models.ForeignKey('Profiles', db_column='FollowingProfileId', blank=True, null=True, related_name='+')  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'followings'


class Galary(models.Model):
    id = models.IntegerField(primary_key=True)
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=45, blank=True, null=True)  # Field name made lowercase.
    imageurl = models.CharField(db_column='ImageUrl', max_length=100, blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'galary'


class Messages(models.Model):
    id = models.IntegerField(primary_key=True)
    fromprofile = models.ForeignKey('Profiles', db_column='FromProfile', blank=True, null=True, related_name='+')  # Field name made lowercase.
    toprofile = models.ForeignKey('Profiles', db_column='ToProfile', blank=True, null=True, related_name='+')  # Field name made lowercase.
    message = models.CharField(db_column='Message', max_length=500, blank=True, null=True)  # Field name made lowercase.
    readdate = models.DateTimeField(db_column='ReadDate', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.
    messagecol = models.CharField(db_column='Messagecol', max_length=45, blank=True, null=True)  # Field name made lowercase.
    groupid = models.IntegerField(db_column='Groupid')  # Field name made lowercase.    
    todelete = models.CharField(db_column='Todelete', max_length=3, default='N')  # Field name made lowercase.
    fromdelete = models.CharField(db_column='Fromdelete', max_length=3, default='N')  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'messages'      


class Post(models.Model):
    id = models.IntegerField(primary_key=True)    
    profileid = models.ForeignKey('Profiles', db_column='ProfileId')  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=100, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=250, blank=True, null=True)  # Field name made lowercase.
    scope = models.CharField(db_column='Scope', max_length=1)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=1)  # Field name made lowercase.
    posturl = models.CharField(db_column='PostUrl', max_length=100, blank=True, null=True)  # Field name made lowercase.
    thumbnailurl = models.CharField(db_column='ThumbnailUrl', max_length=100, blank=True, null=True)  # Field name made lowercase.
    length = models.CharField(db_column='Length', max_length=20, blank=True, null=True)  # Field name made lowercase.
    poststatus = models.IntegerField(db_column='PostStatus',default=0)
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'post'
        verbose_name = 'post'


class Postlikes(models.Model):
    id = models.IntegerField(primary_key=True)
    postid = models.ForeignKey(Post, db_column='PostId', blank=True, null=True)  # Field name made lowercase.
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    #is_like = models.CharField(db_column='is_like', max_length=1)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'postlikes'


class Postratings(models.Model):
    id = models.IntegerField(primary_key=True)
    postid = models.ForeignKey(Post, db_column='PostId', blank=True, null=True)  # Field name made lowercase.
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    rating = models.DecimalField(db_column='Rating', max_digits=2, decimal_places=1, blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'postratings'


class Postsharings(models.Model):
    id = models.IntegerField(primary_key=True)
    postid = models.ForeignKey(Post, db_column='PostId', blank=True, null=True)  # Field name made lowercase.
    profileid = models.IntegerField(db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    sharedto = models.CharField(db_column='SharedTo', max_length=50, blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'postsharings'


class Poststatistics(models.Model):
    id = models.IntegerField(primary_key=True)
    postid = models.ForeignKey(Post, db_column='PostId', blank=True, null=True)  # Field name made lowercase.
    totalview = models.IntegerField(db_column='TotalView', default=0)  # Field name made lowercase.
    totalrating = models.IntegerField(db_column='TotalRating', default=0)  # Field name made lowercase.
    totallike = models.IntegerField(db_column='TotalLike', default=0)  # Field name made lowercase.
    totalsharing = models.IntegerField(db_column='TotalSharing', default=0)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'poststatistics'


class Products(models.Model):
    id = models.IntegerField(primary_key=True)
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=50, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=500, blank=True, null=True)  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=11, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    imageurl = models.CharField(db_column='ImageUrl', max_length=100, blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'products'
        verbose_name = 'Product'


class Productstatistics(models.Model):
    id = models.IntegerField(primary_key=True)
    productid = models.ForeignKey(Products, db_column='ProductId', blank=True, null=True)  # Field name made lowercase.
    totalview = models.IntegerField(db_column='TotalView', default=0)  # Field name made lowercase.
    totalsharing = models.IntegerField(db_column='TotalSharing', default=0)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'productstatistics'
        
class Productimages(models.Model):
    id = models.IntegerField(primary_key=True)
    productid = models.ForeignKey(Products, db_column='ProductId', blank=True, null=True)  # Field name made lowercase.
    images = models.CharField(db_column='Images',max_length=100, blank=True, null=True)  # Field name made lowercase.    
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.
    class Meta:
        #managed = False
        db_table = 'productimages'        


class Profileanswers(models.Model):
    id = models.IntegerField(primary_key=True)
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    questionid = models.ForeignKey('Questions', db_column='QuestionId', blank=True, null=True)  # Field name made lowercase.
    answer = models.CharField(db_column='Answer', max_length=500, blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'profileanswers'


class Profiles(models.Model):
    userid = models.ForeignKey('Users', db_column='UserId')  # Field name made lowercase.
    firstname = models.CharField(db_column='FirstName', max_length=45, null=True)  # Field name made lowercase.
    lastname = models.CharField(db_column='LastName', max_length=45, blank=True, null=True)  # Field name made lowercase.
    companyname = models.CharField(db_column='CompanyName', max_length=255, null=True)  # Field name made lowercase.
    gender = models.CharField(db_column='Gender', max_length=1, blank=True, null=True)  # Field name made lowercase.
    age = models.CharField(db_column='Age', max_length=10, blank=True, null=True)  # Field name made lowercase.
    profilephoto = models.CharField(db_column='ProfilePhoto', max_length=50, blank=True, null=True)  # Field name made lowercase.    
    banner = models.CharField(db_column='Banner', max_length=50, blank=True, null=True)  # Field name made lowercase.
    website = models.CharField(db_column='Website', max_length=50, blank=True, null=True)  # Field name made lowercase.    
    bio = models.TextField(db_column='Bio', blank=True, null=True)  # Field name made lowercase.
    type = models.CharField(db_column='Type', max_length=1, blank=True, null=True)  # Field name made lowercase.
    location = models.CharField(db_column='Location', max_length=45, blank=True, null=True)  # Field name made lowercase.
    referalcode = models.CharField(db_column='ReferalCode', max_length=10, blank=True, null=True)  # Field name made lowercase.
    defaultpage = models.CharField(db_column='DefaultPage', max_length=75, blank=True, null=True)  # Field name made lowercase.
    updatedate = models.DateTimeField(db_column='UpdateDate', blank=True, null=True)  # Field name made lowercase.
    iscelebrity = models.IntegerField(db_column='isCelebrity',default=0)
    
    def __unicode__(self):
        return self.firstname
    
    class Meta:
        #managed = False
        db_table = 'profiles'
        verbose_name = 'Profile'


class Profilestatistics(models.Model):
    id = models.IntegerField(primary_key=True)
    profileid = models.ForeignKey(Profiles, db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    totalfollowers = models.IntegerField(db_column='TotalFollowers', blank=True, null=True)  # Field name made lowercase.
    totallikes = models.IntegerField(db_column='TotalLikes', blank=True, null=True)  # Field name made lowercase.
    totalpost = models.IntegerField(db_column='TotalPost', blank=True, null=True)  # Field name made lowercase.
    totalrating = models.IntegerField(db_column='TotalRating', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'profilestatistics'


class Questions(models.Model):
    id = models.IntegerField(primary_key=True)
    question = models.CharField(db_column='Question', max_length=500, blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'questions'


class Users(models.Model):
    id = models.IntegerField(primary_key=True)
    email = models.EmailField(db_column='Email', max_length=100)  # Field name made lowercase.
    password = models.CharField(db_column='Password',max_length=255, blank=True, null=True)  # Field name made lowercase.
    logintype = models.CharField(db_column='LoginType', max_length=1, blank=True, null=True)  # Field name made lowercase.
    ssotoken = models.CharField(db_column='SSOToken', max_length=255)  # Field name made lowercase.        
    hash = models.CharField(db_column='hash',max_length=100)
    is_active = models.IntegerField(db_column='is_active',default=0)
    isfirsttimelogin = models.IntegerField(db_column='isFirstTimeLogin',default=0)
    usercode = models.CharField(db_column='usercode',max_length=30)
    blockuser = models.IntegerField(db_column='BlockUser',default=0)
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.
    lastlogindate = models.DateTimeField(db_column='LastLoginDate', blank=True, null=True)  # Field name made lowercase.    
    deviceid = models.CharField(db_column='deviceId', max_length=100, blank=True, null=True)  # Field name made lowercase.
    devicetoken = models.CharField(db_column='deviceToken', max_length=255, blank=True, null=True)  # Field name made lowercase.
    notification = models.CharField(db_column='Notification', max_length=1, blank=True, null=True)  # Field name made lowercase.
    
    def __unicode__(self):
       return self.email
    class Meta:
        #managed = False
        db_table = 'users'
        verbose_name = 'User'


class Videoviewhistory(models.Model):
    id = models.IntegerField(primary_key=True)
    videoid = models.ForeignKey(Post, db_column='VideoId', blank=True, null=True)  # Field name made lowercase.
    profileid = models.ForeignKey(Profiles, db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'videoviewhistory'


class Category(models.Model):
    id = models.IntegerField(primary_key=True)    
    name = models.CharField(db_column='name', max_length=50)  # Field name made lowercase.
    description = models.CharField(db_column='description', max_length=255, blank=True, null=True)  # Field name made lowercase.
    create_date = models.DateTimeField(db_column='create_date', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'category'
        verbose_name = 'Category'


class Profilecategory(models.Model):
    id = models.IntegerField(primary_key=True)
    categoryid = models.ForeignKey(Category, db_column='CategoryId', blank=True, null=True)  # Field name made lowercase.
    profileid = models.ForeignKey(Profiles, db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'profilecategory'


class userSocailProfile(models.Model):
    id = models.IntegerField(primary_key=True)
    userid = models.ForeignKey(Users,db_column='userId', blank=True, null=True)  # Field name made lowercase.
    profiletype = models.CharField(db_column='profileType', max_length=1, blank=True, null=True)  # Field name made lowercase.
    profileid = models.CharField(db_column='profileId', max_length=255, blank=True, null=True)  # Field name made lowercase.   

    class Meta:
        #managed = False
        db_table = 'userSocailProfile'


class Albums(models.Model):
    id = models.IntegerField(primary_key=True)
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.
    title = models.CharField(db_column='Title', max_length=50, blank=True, null=True)  # Field name made lowercase.
    description = models.CharField(db_column='Description', max_length=500, blank=True, null=True)  # Field name made lowercase.    
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'albums'


class Postcategory(models.Model):
    id = models.IntegerField(primary_key=True)
    categoryid = models.ForeignKey(Category, db_column='CategoryId', blank=True, null=True)  # Field name made lowercase.
    postid = models.ForeignKey(Post, db_column='PostId', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'postcategory'

class Imagetag(models.Model):
    id = models.IntegerField(primary_key=True)
    tagtext = models.CharField(db_column='TagText', max_length=255)  # Field name made lowercase.
    postid = models.ForeignKey(Post, db_column='PostId', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'imagetag'


class Commentlikes(models.Model):
    id = models.IntegerField(primary_key=True)
    commentid = models.ForeignKey(Comments, db_column='CommentId', blank=True, null=True)  # Field name made lowercase.
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', blank=True, null=True)  # Field name made lowercase.  
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'commentlikes'


class Userblock(models.Model):
    id = models.IntegerField(primary_key=True)
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', related_name='+')  # Field name made lowercase.
    blockedprofileid = models.ForeignKey('Profiles', db_column='BlockedProfileId', related_name='+')  # Field name made lowercase.    
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'userblock'


class Notificationmsg(models.Model):
    id = models.IntegerField(primary_key=True)
    title = models.CharField(db_column='Title', max_length=100, blank=True, null=True)  # Field name made lowercase.
    message = models.CharField(db_column='Message', max_length=250, blank=True, null=True)  # Field name made lowercase.   
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'notificationmsg'


class Usernotification(models.Model):
    id = models.IntegerField(primary_key=True)
    push = models.ForeignKey('Notificationmsg',db_column='Push')  # Field name made lowercase.
    userid = models.ForeignKey('Users', db_column='UserId')  # Field name made lowercase.
    is_send = models.CharField(db_column='is_send', max_length=1, blank=True, null=True)  # Field name made lowercase.
    is_read = models.CharField(db_column='is_read', max_length=1, blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'usernotification'


class Purchaseproduct(models.Model):
    id = models.IntegerField(primary_key=True)
    profileid = models.ForeignKey('Profiles', db_column='ProfileId', related_name='+')  # Field name made lowercase.
    productid = models.ForeignKey(Products, db_column='ProductId', blank=True, null=True)  # Field name made lowercase.
    price = models.DecimalField(db_column='Price', max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    shipping = models.CharField(db_column='Shipping', max_length=100, blank=True, null=True)  # Field name made lowercase.
    tax = models.DecimalField(db_column='Tax', max_digits=6, decimal_places=2, blank=True, null=True)  # Field name made lowercase.
    transactionid = models.CharField(db_column='TransactionId', max_length=50, blank=True, null=True)  # Field name made lowercase.
    paymentstatus = models.CharField(db_column='PaymentStatus', max_length=50, blank=True, null=True)  # Field name made lowercase.
    platform = models.CharField(db_column='Platform', max_length=50, blank=True, null=True)  # Field name made lowercase.
    environment = models.CharField(db_column='Environment', max_length=50, blank=True, null=True)  # Field name made lowercase.
    paypalsdkversion = models.CharField(db_column='PaypalSdkVersion', max_length=50, blank=True, null=True)  # Field name made lowercase.
    intent = models.CharField(db_column='Intent', max_length=50, blank=True, null=True)  # Field name made lowercase.
    paymenttime = models.CharField(db_column='PaymentTime', max_length=50, blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'purchaseproduct'
        

class Productcategory(models.Model):
    id = models.IntegerField(primary_key=True)
    categoryid = models.ForeignKey(Category, db_column='CategoryId', blank=True, null=True)  # Field name made lowercase.
    productid = models.ForeignKey(Products, db_column='ProductId', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'productcategory'
        
        
class Pushnotification(models.Model):
    id = models.IntegerField(primary_key=True)
    message = models.CharField(db_column='Message', max_length=255, blank=True, null=True)  
    receiverprofileid = models.ForeignKey('Profiles', db_column='ReceiverProfileId',related_name='+')  
    is_post_read = models.CharField(db_column='isPostRead', max_length=1, blank=True, null=True)  
    is_push_read = models.CharField(db_column='isPushRead', max_length=1, blank=True, null=True)  
    is_deliver = models.CharField(db_column='isDeliver', max_length=1, blank=True, null=True) 
    action_id = models.IntegerField(db_column='ActionId')  
    action_type = models.CharField(db_column='ActionType', max_length=50, blank=True, null=True)
    senderprofileid = models.ForeignKey('Profiles', db_column='SenderProfileId',related_name='+')  
    status = models.CharField(db_column='Status', max_length=1, blank=True, null=True)  
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  

    class Meta:
        #managed = False
        db_table = 'pushnotification'
        

class Producttag(models.Model):
    id = models.IntegerField(primary_key=True)
    tagtext = models.CharField(db_column='TagText', max_length=255)  # Field name made lowercase.
    productid = models.ForeignKey(Products, db_column='ProductId', blank=True, null=True)  # Field name made lowercase.
    createdate = models.DateTimeField(db_column='CreateDate', blank=True, null=True)  # Field name made lowercase.

    class Meta:
        #managed = False
        db_table = 'producttag'        
