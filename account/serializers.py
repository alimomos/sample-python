from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from voice_chat.utility.common_function import otp_generator
from voice_chat.utility.email_utils import send_email_to_user
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User,Otp
from .models import Otp,User
from chat.models import Topic, TopicMembership, TopicLike
from chat.serializers import TopicSerializer, TopicMembershipSerializer, TopicLikeSerializer


    
    
class RegisterSerializer(serializers.ModelSerializer):
    
    
    email = serializers.EmailField(
                                required=True,
                                validators=[UniqueValidator(queryset=User.objects.all(),message='This email already exists!')]
                                )
    password = serializers.CharField(write_only=True, required=True)

    
    class Meta:
        model = User
        fields = ('id','email', 'password','first_name' ,'last_name')

    def create(self, validated_data):
        user_email=[]
        user = User.objects.create_user(**validated_data)
        otp_obj=Otp.objects.create(user=user,otp_type='Register',otp=otp_generator())
        try:
            user_email.append(validated_data['email'])
            send_email_to_user(otp_obj.otp,user_email,'Registration')
            otp_obj.save()
        except :
            pass
        return user


class RegisterOtpVerifySerializer(serializers.Serializer):

    email=serializers.EmailField(required=True) 
    otp=serializers.CharField(required=True)

    def validate(self, data):
        
        try:
            user=User.objects.get(email=data['email'])
        except:
            raise serializers.ValidationError("This email not exists !")
        try:
            user_otp=user.otp_user.filter(otp_type="Register").latest('id').otp
        except:
            raise serializers.ValidationError(" otp not found !")
        if user_otp != data['otp']:
            raise serializers.ValidationError(" invalid otp ! ")  
        return data
    

    def create(self, validated_data):
        user=User.objects.get(email=validated_data['email'])
        user.is_active = True
        user.save()
        user.otp_user.filter(otp_type="Register").delete()
        return user
    

class UserDetailSerializer(serializers.ModelSerializer):
     class Meta:
        model = User
        fields = ('id','email','first_name' ,'last_name',)
        

class LogoutSerializer(serializers.Serializer):

    refresh=serializers.CharField(write_only=True, required=True)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'Username or Password does not matched.'
    }

    def validate(self, attrs):
            data = super().validate(attrs)
            data["user_data"] = UserDetailSerializer(self.user).data
            return data
    
   
class SendOtpSerializer(serializers.Serializer):
     
     
    email=serializers.EmailField(required=True)
     
    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This user not exists!")
        return value
     

    def create(self, validated_data):
        user_email=[]
        otp_obj=Otp.objects.create(user=User.objects.get(email=validated_data['email']),otp=otp_generator(),otp_type='ResetPassword')
        try:
            user_email.append(validated_data['email'])
            send_email_to_user(otp_obj.otp,user_email,'Reset Password')
            otp_obj.save()
        except :
            pass

        return otp_obj


class ResetPasswordSerializer(serializers.Serializer):

    email=serializers.EmailField(required=True) 
    otp=serializers.CharField(required=True)
    password=serializers.CharField(required=True)
    confirm_password=serializers.CharField(required=True)

    def validate(self, data):
        try:
            user=User.objects.get(email=data['email'])
        except:
            raise serializers.ValidationError("This email not exists!")
        try:
            user_otp=user.otp_user.filter(otp_type="ResetPassword").latest('id').otp
        except:
            raise serializers.ValidationError(" otp notfound ! ")
        if user_otp != data['otp']:
            raise serializers.ValidationError(" invalid otp ! ")  
        
        # if User.objects.get(email=data['email']).otp_user.all().latest('id').otp != data['otp']:
        #     raise serializers.ValidationError(" invalid otp ! ")


        if data['password']!=data['confirm_password']:

            raise serializers.ValidationError("password and confirm_password does not match !")
        
        return data
    

    def create(self, validated_data):
        user=User.objects.get(email=validated_data['email'])
        user.set_password(validated_data['password'])
        user.save()
        user.otp_user.filter(otp_type="ResetPassword").delete()
        return user
    

class ChangePasswordSerializer(serializers.Serializer):
    
    old_password=serializers.CharField(required=True) 
    new_password=serializers.CharField(required=True)

    def validate_old_password(self, value):
        auth_user=self.context['request']        
        if not auth_user.check_password(value):
            raise serializers.ValidationError("old password incorrect ")
        
        return value

    def create(self, validated_data):
        auth_user=self.context['request']
        auth_user.set_password(validated_data.get('new_password'))
        auth_user.save()
        return auth_user
    

class UserDetailSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ('id','email','first_name' ,'last_name', "phone", "profile_pic")
        extra_kwargs = {"email": {"read_only": True}}
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['my_topic'] = TopicSerializer(Topic.objects.filter(moderate=instance), many=True).data
        
        joined = TopicMembership.objects.filter(user=instance)
        liked = TopicLike.objects.filter(user=instance, is_active=True)


        representation['joined_topic'] = TopicMembershipSerializer(joined, many=True).data
        representation['liked_topic'] = TopicLikeSerializer(liked, many=True).data
        return representation
