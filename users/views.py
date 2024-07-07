from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import *
from .models import CustomUser, Organisation
from django.contrib.auth import login, logout
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import permissions
from django.db import transaction
from django.shortcuts import get_object_or_404

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            try:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                user = serializer.save()

                refresh = RefreshToken.for_user(user)
                access_token = str(refresh.access_token)
                response_data = Response({
                    "status": "success",
                    "message": "Registration successful",
                    "data": {
                        "accessToken": access_token,
                        "user": {
                            "userId": user.userId,
                            "firstName": user.firstName,
                            "lastName": user.lastName,
                            "email": user.email,
                            "phone": user.phone,
                        }
                    }
                }, status=status.HTTP_201_CREATED
                )
                return response_data

            except serializers.ValidationError as e:
                errors = [{"field": k, "message": v} for k, v in e.detail.items()]   
                return Response({
                    "errors": errors
                }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)  

            except Exception as e:
                return Response(
                    {
                        "status": "Bad request",
                        "message": "Registration unsuccessful",
                        "statusCode": status.HTTP_400_BAD_REQUEST
                    }, status=status.HTTP_400_BAD_REQUEST
                )


class LoginView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.AllowAny]
    def post(self, request):
        try:
            email = request.data['email']
            password = request.data['password']

            user = CustomUser.objects.filter(email=email).first()

            if user is None:
                raise AuthenticationFailed("User not found")

            if not user.check_password(password):
                raise AuthenticationFailed("password is Incorrect")

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            login(request, user)
            response_data = Response({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": access_token,
                    "user": {
                        "userId": user.userId,
                        "firstName": user.firstName,
                        "lastName": user.lastName,
                        "email": user.email,
                        "phone": user.phone,
                    }
                }
            }, status=status.HTTP_200_OK
            )
            return response_data

        except serializers.ValidationError as e:
            errors = [{"field": k, "message": v} for k, v in e.detail.items()]   
            return Response({
                "errors": errors
            }, status=status.HTTP_422_UNPROCESSABLE_ENTITY)   

        except Exception as e:
            return Response(
                {
                    "status": "Bad request",
                    "message": "Authentication Failed",
                    "statusCode": status.HTTP_401_UNAUTHORIZED
                }, status= status.HTTP_401_UNAUTHORIZED
            )


class GetUserView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, userId):
        logged_user = request.user
        try:
            user = get_object_or_404(CustomUser, userId=userId)
            # Assuming the Organisation model has a field like `users` which is a ManyToManyField or ForeignKey
            user_organisations = Organisation.objects.filter(users=logged_user)

            if user_organisations.filter(users=user).exists():
                serializer = RegistrationSerializer(user)
                return Response(
                    {
                        "status": "success",
                        "message": "User Found",
                        "data": serializer.data
                    }, status=status.HTTP_200_OK
                )
            else:
                 return Response(
                    {
                        "status": "Error",
                        "message": "You do not have permission to view user data",
                    }, status=status.HTTP_403_FORBIDDEN
                )               
        except Exception as e:
            return Response(
                {
                    "status": "Bad request",
                    "message": "Client error",
                    "statusCode": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST
            )

class GetOrganisationView(generics.ListCreateAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            organisations = request.user.organisations.all()

            data = []
            for organisation in organisations:
                data.append({
                    "orgId": organisation.orgId,
                    "name": organisation.name,
                    "description": organisation.description,
                })

            if request.user in organisation.users.all():
                return Response(
                    {
                        "status": "success",
                        "message": "Organisations retrieved successfully",
                        "data": data
                    }, status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response(
            {
                "status": "Bad request",
                "message": "Client error",
                "statusCode": status.HTTP_400_BAD_REQUEST
            }, status=status.HTTP_400_BAD_REQUEST
            )

    def post(self, request):
        data = request.data
        try:
            organisation = Organisation.objects.create(
                name = data["name"],
                description = data["description"],
            )
            organisation.users.add(request.user)
            return Response(
                {
                    "status": "success",
                    "message": "Organisation created successfully",
                    "data": {
                        "orgId": organisation.orgId,
                        "name": organisation.name,
                        "description": organisation.description
                    }
                }, status=status.HTTP_201_CREATED
        )

        except Exception as e:
            return Response(
                {
                    "status": "Bad Request",
                    "message": "Client error",
                    "statusCode": status.HTTP_400_BAD_REQUEST
                }, status=status.HTTP_400_BAD_REQUEST
            )

class GetAnOrganisationView(generics.GenericAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, orgId):
        try:
            organisation = Organisation.objects.get(orgId=orgId)
            serializer = OrganisationSerializer(organisation)
            return Response(
                {
                "status": "success",
                "message": "Organisation Found",
                "data": serializer.data
                }, status= status.HTTP_200_OK
            )           
        except Exception:
            return Response(
                {
                    "status": "Bad Request",
                    "message": "Client error",
                    "statusCode": 400
                }, status= status.HTTP_400_BAD_REQUEST
                )               

class AddUserToOrganisation(generics.GenericAPIView):
    serializer_class = OrganisationSerializer
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, orgId):
        data = request.data        
        try:
            organisation = Organisation.objects.get(orgId=orgId)
            if request.user in organisation.users.all():
                user =  CustomUser.objects.get(userId=data["userId"])
                organisation.users.add(user)
                return Response(
                    {
                        "status": "success", 
                        "message": "User Added to organisation Successfully"
                    }, status= status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "status": "error", 
                        "message": "You do not have permission to add user"
                    }, status= status.HTTP_403_FORBIDDEN
                )                
        except:
            return Response(
                {
                    "status": "Bad Request",
                    "message": "Client error",
                    "statusCode": 400
                }, status= status.HTTP_400_BAD_REQUEST
                )                   