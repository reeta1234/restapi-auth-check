from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from benefitapp.admin import PostDetailView,UserView,PostView,ProductView,setStatus,setPostStatus,ProfileDetailView,setCelebrity
from benefitapp import views,category,messages,cronjob,post, push_notification
from django.contrib.admin.views.decorators import staff_member_required
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'backend.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    
    url(r'^admin/', include(admin.site.urls)),
    url(r'^admin/benefitapp/post/(?P<post_id>\d+)', staff_member_required(PostDetailView.as_view())),
    url(r'^admin/users', staff_member_required(UserView.as_view())),
    #url(r'^admin/post', PostView.as_view()),
    url(r'^admin/product', staff_member_required(ProductView.as_view())),
    url(r'^admin/status/(?P<user_id>\d+)/(?P<statusval>\d+)', staff_member_required(setStatus.as_view())),
    url(r'^admin/status2/(?P<post_id>\d+)/(?P<statusval>\d+)', staff_member_required(setPostStatus.as_view())),
    url(r'^admin/celebrity/(?P<profile_id>\d+)/(?P<statusval>\d+)', staff_member_required(setCelebrity.as_view())),
    #url(r'^admin/test', TestView.as_view()),
    url(r'^admin/post', staff_member_required(PostView.as_view())),
    url(r'^admin/userdetail/(?P<user_id>\d+)', staff_member_required(ProfileDetailView.as_view())),
     
    #TEST  API ROUTES
    #url(r'^api/test/', views.test.as_view()),   
    #url(r'^api/sendmailtset/', views.sendmailtset.as_view()),
    
    #User API Routes
    url(r'^api/signup/', views.UserSignUp.as_view()),
    url(r'^api/auth/', views.UserAuthSignUp.as_view()),
    url(r'^api/signin/', views.UserSignIn.as_view()),
    url(r'^api/logout/', views.Logout.as_view()),
    url(r'^api/changepassword/', views.UserChangePassword.as_view()),
    url(r'^api/referralcode/', views.updateReferralCode.as_view()),
    url(r'^api/forgetpassword/', views.UserForgetPassword.as_view()),
    url(r'^api/emailverification/', views.UserEmailVerification.as_view()),
    url(r'^api/updateprofile/', views.UpdateUserProfile.as_view()),
    url(r'^api/updateprofilestep2/', views.UpdateUserProfileStep2.as_view()),    
    url(r'^api/list/', views.getUserList.as_view()),
    #url(r'^api/user/(?P<user_id>\d+)/$', views.getUserDetail.as_view()),
    url(r'^api/userdetail/(?P<user_id>\d+)', views.getUserDetail.as_view()),
    url(r'^api/userstatus/(?P<user_id>\d+)$', views.setUserStatus.as_view()),
    url(r'^api/userbanner/', views.UpdateUserBanner.as_view()),
    url(r'^api/userreport/', views.reportAdminAboutUser.as_view()),
    url(r'^api/blockuser/', views.blockUser.as_view()),
    
    #Category API Routes  
    url(r'^api/viewreferralcode/(?P<user_id>\d+)', category.viewMyReferalCode.as_view()),
    #url(r'^api/uploadvideo/', views.uploadvideo.as_view()),
    url(r'^api/category/', category.category.as_view()),
    url(r'^api/categorylist/', category.getCategoryList.as_view()),
    url(r'^api/follow/', category.followProducer.as_view()),
    #url(r'^api/unfollow/', category.unfollowProducer.as_view()),
    url(r'^api/addpost/', category.addPost.as_view()),
    url(r'^api/addcomment/', category.putComment.as_view()),
    url(r'^api/addfavorite/', category.favoritePost.as_view()),
    url(r'^api/likepost/', category.postLike.as_view()),
    url(r'^api/likecomment/', category.commentLike.as_view()),
    url(r'^api/addproduct/', category.addProduct.as_view()),
    url(r'^api/addalbum/', category.addAlbum.as_view()),
    url(r'^api/totalLikes/(?P<post_id>\d+)', category.postLikesTotalCount.as_view()),
    url(r'^api/ratepost/', category.ratePost.as_view()),
    #url(r'^api/followerpost/(?P<user_id>\d+)', category.getPostContent.as_view()),
    
    
    #url(r'^api/feed/(?P<user_id>\d+)', category.getFeedList.as_view()), # changed on 5feb16
    url(r'^api/feed/(?P<user_id>\d+)', post.getFeedList.as_view()),
    
    #url(r'^api/getuserpost/(?P<user_id>\d+)', category.getUserOwnPost.as_view()),  changed on 5feb16
    url(r'^api/getuserpost/(?P<user_id>\d+)', post.getUserOwnPost.as_view()),
    url(r'^api/viewotheruserprofile/(?P<user_id>\d+)', category.viewOtherUserProfile.as_view()),
    url(r'^api/editpost/', category.addPost.as_view()),
    url(r'^api/deletepost/(?P<user_id>\d+)', category.deletePost.as_view()),
    url(r'^api/deleteproduct/(?P<user_id>\d+)', category.deleteProduct.as_view()),
    url(r'^api/getpostdetail/(?P<post_id>\d+)', category.getPostDetail.as_view()),
    url(r'^api/getproductdetail/(?P<product_id>\d+)', category.getProductDetail.as_view()),
    url(r'^api/getuserfavoritelist/(?P<user_id>\d+)', category.getUserFavoriteContentList.as_view()),
    url(r'^api/poststatistics/', category.addPostStatistics.as_view()),
    url(r'^api/productstatistics/', category.addProductStatistics.as_view()),
    url(r'^api/feeddetail/(?P<user_id>\d+)', category.getFeedDetail.as_view()),
    url(r'^api/trending/(?P<user_id>\d+)', category.getTrending.as_view()),
    url(r'^api/purchaseproduct', post.purchaseProduct.as_view()),
    url(r'^api/carouselfeed/(?P<user_id>\d+)', post.getCarouselFeedList.as_view()),
    
    
    
    # messages
    url(r'^api/getfollowerslist/(?P<user_id>\d+)', messages.getFollowersList.as_view()),
    url(r'^api/compose/', messages.composeMails.as_view()),
    url(r'^api/inbox/(?P<user_id>\d+)', messages.inboxList.as_view()),
    url(r'^api/sent/(?P<user_id>\d+)', messages.sentList.as_view()),
    url(r'^api/messagedetail/(?P<message_id>\d+)', messages.getMessageDetail.as_view()),
    url(r'^api/deletemessage/', messages.deleteMessage.as_view()),
    url(r'^api/getallusers/(?P<user_id>\d+)', messages.getAllUsersList.as_view()),
    url(r'^api/inviteusers/', messages.inviteUsers.as_view()),
    url(r'^api/contact/', messages.contact.as_view()),
    
    
    # push notification
    url(r'^api/pushTest/', push_notification.pushTest.as_view()),
    url(r'^api/getPushNotificationCount/', push_notification.getPushNotificationCount.as_view()),
    url(r'^api/getPushNotificationList/', push_notification.getPushNotificationList.as_view()),
    url(r'^api/markAsRead/', push_notification.markAsRead.as_view()),
    
    #cronjob
    url(r'^updatevideothumb/cron$', cronjob.updateVideoThumb, name='cronjob'),
    url(r'^pushnotification/cron$', cronjob.userPushNotification, name='cronjob'),
    
    
    
    #Admin API Routes
    url(r'^admin/', include(admin.site.urls)),
)