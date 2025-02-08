from django.urls import path
from . import views

urlpatterns = [
    path('posts/get/all/', views.get_all_posts_view, name='get_posts_collection'),
    path('posts/get/user/<int:user_id>/', views.get_user_posts_view, name='user_posts'),
    path('posts/create/', views.create_post_view, name='create_post'),
    path('posts/get/<int:post_id>/', views.get_post_view, name='get_post'),

    path('users/get/me/', views.get_user_self_view, name='user'),
    path('users/get/<int:user_id>/', views.get_user_view, name='user'),
    path('users/auth/login/', views.user_login_view, name='login'),
    path('users/auth/logout/', views.user_logout_view, name='logout'),
    path('users/get/<int:user_id>/friends-count/', views.user_friend_count_view, name='friend_count'),
    path('users/get/<int:user_id>/friends/', views.user_friends_view, name='friends'),
    path('users/get/me/friends-requests/', views.user_friends_requests_view, name='friends-requests'),
    path('users/get/me/friends-requests-send/', views.user_friends_requests_send_view, name='friends-requests-send'),
    path('users/make-friend/', views.make_friend_view, name='make-friend'),
    path('users/accept-friend/', views.accept_friend_view, name='accept-friend'),
]
