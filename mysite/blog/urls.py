from django.contrib import admin
from django.urls import path, include
from . import views
#from mysite.mysite.sitemaps import PostSitemap

app_name = 'blog'

urlpatterns = [

    path('map_detail', views.map_detail, name='map_detail'),
    path('', views.map_calculating, name='map_calculating'),
     path('city/<str:city_name>/', views.print_city),

    
]