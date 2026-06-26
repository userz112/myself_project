from django.shortcuts import render
from .serializers import UserRegisterSerializer,UserLoginSerializer,UserUpdateSerializer,UserAvatarSerializer
from .models import User,UserLoginLog
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

class UserRegisterView(APIView):

    def post(self, request):
        data = request.data
        print(data)
        serializer = UserRegisterSerializer(data=data)
        print(serializer.is_valid())
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'msg': '注册成功'}, status=201)
        else:
            print('serializer.errors:', serializer.errors)
            return JsonResponse(serializer.errors, status=400)
        

class UserLoginView(APIView):
    
    def post(self, request):
        data = request.data
        print(data)
        serializer = UserLoginSerializer(data=data)
        print(serializer.is_valid())
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            access_token_str = str(access)
            refresh_token_str = str(refresh)
            print('username:', user.username)
            return JsonResponse({
                'msg': '登录成功',
                'token': {
                    'access': access_token_str,
                    'refresh': refresh_token_str,
                },
                'username': user.username,
            }, status=200)
        else:
            print('serializer.errors:', serializer.errors)
            return JsonResponse(serializer.errors, status=400)


class UserInfoView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return JsonResponse({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone,
            'gender': user.gender,
            'avatar': user.avatar.url if user.avatar else settings.MEDIA_URL + 'avatar/default_avatar.png',
        })
        
    def put(self, request):
        serializer = UserUpdateSerializer(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'msg': '更新成功'}, status=200)
        else:
            return JsonResponse(serializer.errors, status=400)
        
class UserAvatarView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserAvatarSerializer(instance=request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse({'msg': '头像上传成功', 'avatar': request.user.avatar.url}, status=200)
        else:
            return JsonResponse(serializer.errors, status=400)

class UserLoginView(APIView):
    
    def post(self, request):
        data = request.data
        # 序列化中进行了一些校验，如用户名或密码错误等
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid():
            user = serializer.validated_data
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            access_token_str = str(access)
            refresh_token_str = str(refresh)

            return JsonResponse({'msg': '登录成功',
                'token':{
                    'access':access_token_str,
                    'refresh':refresh_token_str,
                },
                'username': user.username
            }, status=200)
        else:
            print('这是else语句')
            print('serializer.errors:', serializer.errors)
            return JsonResponse(serializer.errors, status=400)







