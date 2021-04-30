from django.urls import path
from django.conf.urls import url
from . import views
                    
urlpatterns = [
    path('', views.show_login),
    path('login', views.show_login),
    path('register_user',views.register_user),
    path('process_login', views.process_login),
    path('home', views.show_success),
    path('logout',views.logout),
    path('email_exists',views.email_exists),
    path('ajax/validate_email',views.email_exists,name='validate_email'),
    path('wall',views.wall),
    path('wall/post_message', views.post_message),
    path('wall/post_comment', views.post_comment),
    path('wall/delete_comment', views.delete_comment),
    path('wall/delete_message', views.delete_message),
    path('weather',views.weather),
    path('youtube', views.youtube),

    path('youtube/video_pref_info',views.get_video_pref_info),

    path('youtube/favorite/add',views.add_favorite_video),
    path('youtube/favorite/remove', views.delete_favorite_video),

    path('youtube/rating/update', views.update_video_rating),
]