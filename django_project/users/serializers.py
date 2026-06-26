from rest_framework import serializers
from .models import User
import django.conf as settings

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        username = data['username'].strip()
        password = data['password'].strip()
        if not username:
            raise serializers.ValidationError({'username': '用户名不能为空'})
        if not password:
            raise serializers.ValidationError({'password': '密码不能为空'})
        user = User.objects.filter(username=username).first()
        if user is None:
            raise serializers.ValidationError({'username': '用户不存在'})
        if not user.check_password(password):
            raise serializers.ValidationError({'password': '密码错误'})
        return user
    

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'gender']

    def validate_username(self, value):
        if User.objects.filter(username=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('用户名已存在')
        return value

    def validate_phone(self, value):
        if User.objects.filter(phone=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('手机号已存在')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(id=self.instance.id).exists():
            raise serializers.ValidationError('邮箱已存在')
        return value



class UserRegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'phone', 'gender']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self,data):
        password = data['password'].strip()
        confirm_password = data['confirm_password'].strip()
        if password != confirm_password:
            raise serializers.ValidationError({'confirm_password': '密码不一致'})

        if len(password) < 8:
            raise serializers.ValidationError({'password': '密码长度不能小于8位'})

        if User.objects.filter(phone=data['phone']).exists():
            raise serializers.ValidationError({'phone': '手机号已存在'})

        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError({'email': '邮箱已存在'})

        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError({'username': '用户名已存在'})

        return data

    def create(self,validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user

class UserAvatarSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['avatar']

    def validate_avatar(self,avatar):
        if avatar.size > 1024 * 1024 * 5:
            raise serializers.ValidationError('头像大小不能超过5MB')

        if avatar.name.split('.')[-1].lower() not in ['jpg', 'jpeg', 'png']:
            raise serializers.ValidationError('头像格式必须为jpg、jpeg或png')
        
        return avatar
    
    # def update(self,user_avatar,validated_data):
    #     user_avatar.avatar = validated_data.get('avatar', user_avatar.avatar)
    #     with open(settings.MEDIA_ROOT + 'avatar/' + user_avatar.avatar.name, 'wb+') as f:
    #         f.write(user_avatar.avatar.read())
    #     user_avatar.save()
    #     return user_avatar


        


