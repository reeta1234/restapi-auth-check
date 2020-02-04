from django.urls import path,re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^external-api', views.external_api_view,name='external-api-view'),
    re_path(r'^postdata', views.view,name='view'),
    re_path(r'^test/', views.Test.as_view()),
    re_path(r'^test2', views.external_api_view2, name='external-api-view2'),
    re_path(r'^test3', views.testIndex, name='Test-Index'),
    re_path(r'^test4', views.getBase64Data, name='Base64-Index'),
    re_path(r'^test5/', views.Base64Test.as_view()),
    re_path(r'^test6/', views.extractPDFContent, name='Base64Index'),
    re_path(r'^test7/', views.PDFIndex.as_view()),
    re_path(r'^simpletest/(?P<id>\d+)/$', views.SimpleTest.as_view()),
    #path(r'^users/(?P<id>\d+)/$', views.SimpleTest.as_view())
]