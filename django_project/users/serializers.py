from rest_framework import serializers
from .models import User

class UserMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'phone', 'avatar', 'create_time', 'update_time']

class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'confirm_password', 'phone', 'avatar', 'gender']

    def validate(self,validated_data):
        # 校验密码是否一致
        password = validated_data['password'].strip()
        confirm_password = validated_data['confirm_password'].strip()
        if password != confirm_password:
            raise serializers.ValidationError({'confirm_password': '密码不一致'})
        
        if len(password) < 8:
            raise serializers.ValidationError({'password': '密码长度不能小于8位'})
        
        # 校验手机号是否已存在
        if User.objects.filter(phone=validated_data['phone']).exists():
            raise serializers.ValidationError({'phone': '手机号已存在'})

        # 校验邮箱是否已存在
        if User.objects.filter(email=validated_data['email']).exists():
            raise serializers.ValidationError({'email': '邮箱已存在'})
        
        # 校验用户名是否已存在
        if User.objects.filter(username=validated_data['username']).exists():
            raise serializers.ValidationError({'username': '用户名已存在'})
        
        # 校验性别是否有效
        if validated_data['gender'] not in [0,1]:
            raise serializers.ValidationError({'gender': '性别无效'})
        
        #

        return validated_data
    
    def create(self,validated_data):
        validated_data['confirm_password'] = None
        user = super().create(validated_data)
        return user




