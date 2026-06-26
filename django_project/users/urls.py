from django.urls import path
from . import views


urlpatterns = [
    path('register/', views.UserRegisterView.as_view()),
    path('login/', views.UserLoginView.as_view()),
    path('me/', views.UserInfoView.as_view()),
    path('avatar/', views.UserAvatarView.as_view()),
]
    
