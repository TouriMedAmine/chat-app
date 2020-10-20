from django.urls import path, re_path
from . import views
from .views import ThreadView
urlpatterns = [
    path('', views.essai_index, name='essai_index'),
    path('login/', views.login_page, name='login'),
    path('register/', views.register_page, name='register'),
    path('logout/', views.logout_page, name='logout'),
    path('search/', views.search_page, name='search'),
    path('add-friend/<int:id>/', views.send_friend_request, name='send'),
    path('accept-friend/<int:id>/', views.accept_friend_request, name='accept'),
    path('delete-friend_request/<int:id>/', views.delete_friend_request, name='delete'),
    #re_path(r"^(?P<username>[\w.@+-]+)", views.ThreadView, name='Thread'),
    re_path(r"^messages/(?P<username>[\w.@+-]+)/$", ThreadView.as_view(), name='messages'),
]