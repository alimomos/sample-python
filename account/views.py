from rest_framework import status
from django.shortcuts import render 
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny,IsAuthenticated
from .serializers import RegisterSerializer,RegisterOtpVerifySerializer,LogoutSerializer,CustomTokenObtainPairSerializer,SendOtpSerializer,ResetPasswordSerializer,UserDetailSerializer,ChangePasswordSerializer




class RegisterUserViewSet(viewsets.ViewSet):

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request):
        context={}
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            context['data']=serializer.data
            context['message'] = "user created otp send !"
            context['status']=True
            return Response(context, status=status.HTTP_201_CREATED)
        context['data']={}
        context['message'] = serializer.errors
        context['status']=False
        return Response(context, status=status.HTTP_400_BAD_REQUEST)
    
    
class RegisterOtpVerifyViewSet(viewsets.ViewSet):

    serializer_class = RegisterOtpVerifySerializer
    permission_classes = [AllowAny]

    def create(self, request):
        context={}
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            context['data']={}
            context['message'] = "otp is verified !"
            context['status']=True
            return Response(context, status=status.HTTP_201_CREATED)
        context['data']={}
        context['message'] = serializer.errors
        context['status']=False
        return Response(context, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        context={}
        serializer=LogoutSerializer(data=request.data)
        if serializer.is_valid():
            try :
                token = RefreshToken(serializer.validated_data['refresh'])
                token.blacklist()
                context['data']={}
                context['message'] = "user logout"
                context['status']=True
                return Response(context, status=status.HTTP_200_OK)
            except:
                context['data']={}
                context['message'] = "user  already Logged out "
                context['status']=False
                return Response(context, status=status.HTTP_400_BAD_REQUEST)
        context['data']={}
        context['message'] = serializer.errors
        context['status']=False
        return Response(context, status=status.HTTP_400_BAD_REQUEST)
    

class TokenObtainPairPatchedView(TokenObtainPairView):

    serializer_class = CustomTokenObtainPairSerializer


class SendOtpAPIView(APIView):

    serializer_class = SendOtpSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        context={}
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            context['data']={}
            context['message'] = "otp send to email"
            context['status']=True
            return Response(context, status=status.HTTP_200_OK)
        context['data']={}
        context['message'] =serializer.errors
        context['status']=False
        return Response(context, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):

    serializer_class = ResetPasswordSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        context={}
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            context['data']={}
            context['message'] = "password successful reset !"
            context['status']=True
            return Response(context, status=status.HTTP_200_OK)
        context['data']={}
        context['message'] = serializer.errors
        context['status']=False
        return Response(context, status=status.HTTP_400_BAD_REQUEST)
    
           
class ChangePasswordAPIView(viewsets.ViewSet):
    
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request):
        context={}
        serializer = self.serializer_class(data=request.data,context={'request': self.request.user})
        if serializer.is_valid():
            serializer.save()
            context['data']={}
            context['message'] = "password successful changed !"
            context['status']=True
            return Response(context, status=status.HTTP_200_OK)
        context['data']={}
        context['message'] = serializer.errors
        context['status']=False
        return Response(context, status=status.HTTP_400_BAD_REQUEST)
    

class UserViewSet(viewsets.ViewSet):

    serializer_class = UserDetailSerializer
    permission_classes = [IsAuthenticated]


    def retrieve(self, request):
        context={}
        try :
            serializer = self.serializer_class(request.user,context={'request': request})
            context['data']=serializer.data
            context['message'] = "user detail"
            context['status']=True
            return Response(context, status=status.HTTP_200_OK)
        except :
            context['data']={}
            context['message'] = "user detail not found !"
            context['status']=False
            return Response(context, status=status.HTTP_400_BAD_REQUEST) 
        
    def partial_update(self, request):
        context={}
        serializer = self.serializer_class(request.user,data=request.data,partial=True, context={"request":request})
        if serializer.is_valid():
            serializer.save()
            context['data']=serializer.data
            context['message'] = "user detail updated"
            context['status']=True
            return Response(context, status=status.HTTP_200_OK)
        context['data']={}
        context['message'] = serializer.errors
        context['status']=False
        return Response(context, status=status.HTTP_400_BAD_REQUEST)
        