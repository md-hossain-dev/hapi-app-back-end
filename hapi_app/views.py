from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
# from .models import User,Follower,UserProfileVisit,Invitation,Wallet
from .models import *
from rest_framework import status
from django.core.exceptions import ValidationError
import re
from django.core.mail import send_mail
import uuid
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from .serializers import ImageSerializer,WalletSerializer,CountrySerializer,UserUpdateSerializer,UserUpdateImageSerializer
from django.shortcuts import get_object_or_404
from datetime import timedelta

from .utils import send_firebase_notification
from google.auth.transport.requests import Request

from .models import Notification
from django.db import transaction
from django.core.files.base import ContentFile
import requests
class CustomObtainTokenView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        fcm_token = request.data.get('fcm_token')  
        if not email or not password:
            return Response({
                'message': 'email and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        
        if user is not None and user.is_active:
            # Save the FCM token
            if fcm_token:
                user.fcm_token = fcm_token
                user.save()

            # Token creation
            refresh = RefreshToken.for_user(user)
            
            # Customizing access token expiration
            custom_lifetime = timedelta(days=365)
            access_token = refresh.access_token
            access_token.set_exp(lifetime=custom_lifetime)

            # Send Welcome Notification
            if user.fcm_token:
                title = "Welcome!"
                body = f"Hello {user.username}, you have successfully logged in."
                notification_response = send_firebase_notification(user.fcm_token, title, body)
                print("Firebase Response:", notification_response)

                # Save the notification in the database
                notification = Notification(
                    user=user,
                    title=title,
                    message=body,
                    is_sent=True  # Indicating the notification was sent successfully
                )
                notification.save()

            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'access_token': str(access_token),
                'refresh_token': str(refresh),
                'notification_status': 'Notification sent successfully' if user.fcm_token else 'No FCM token available'
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Login failed: Invalid credentials or inactive user'
        }, status=status.HTTP_400_BAD_REQUEST)




class GoogleAuthAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        required_fields = ['google_token', 'unique_id', 'auth_type', 'access_token_google', 
                           'password', 'email', 'nick_name', 'profile_image_url']
        data = request.data

        # Validate required fields
        if not all(field in data and data[field] for field in required_fields):
            return Response({'message': 'All fields are required.'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        google_token = data.get('google_token')
        unique_id = data.get('unique_id')
        auth_type = data.get('auth_type')
        access_token_google = data.get('access_token_google')
        password = data.get('password')
        email = data.get('email')
        nick_name = data.get('nick_name')
        profile_image_url = data.get('profile_image_url')

        try:
            # Check if user already exists
            user = User.objects.filter(email=email).first()

            if user:
                # User exists, check password
                if not user.check_password(password):
                    return Response({'message': 'Invalid password.'}, 
                                    status=status.HTTP_401_UNAUTHORIZED)

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)

                return Response({
                    'message': 'Login successful',
                    'user_id': user.id,
                    'email': user.email,
                    'nick_name': user.first_name,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }, status=status.HTTP_200_OK)
            else:
                # Create a new user
                user = User(
                    google_token=google_token,
                    unique_id=unique_id,
                    auth_type=auth_type,
                    access_token_google=access_token_google,
                    password=password,
                    email=email,
                    nick_name=nick_name
                )
                user.set_password(password)
                
                # Save user to generate primary key
                user.save()

                # Download and save profile image
                if profile_image_url:

                    try:
                        response = requests.get(profile_image_url, stream=True)
                        if response.status_code == 200:
                            # Extract the filename from the URL or use a custom name
                            filename = f"{unique_id}_profile.jpg"
                            
                            # Save the image to the profile field
                            user.profile.save(filename, ContentFile(response.content), save=True)
                        else:
                            return Response({
                                'message': 'Failed to download image from the provided URL.',
                                'status_code': response.status_code
                            }, status=status.HTTP_400_BAD_REQUEST)
                    except requests.exceptions.RequestException as e:
                        return Response({
                            'message': 'Error occurred while downloading the profile image.',
                            'error': str(e)
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # Generate JWT tokens
                refresh = RefreshToken.for_user(user)

                return Response({
                    'message': 'User created and logged in successfully',
                    'user_id': user.id,
                    'email': user.email,
                    'nick_name': user.nick_name,
                    'profile_image': user.profile.url if user.profile else None,
                    'access_token': str(refresh.access_token),
                    'refresh_token': str(refresh),
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'message': 'Something went wrong', 'error': str(e)}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class CustomObtainTokenView(APIView):
#     permission_classes = [AllowAny]
    
#     def post(self, request, *args, **kwargs):
#         email = request.data.get('email')
#         password = request.data.get('password')
#         fcm_token = request.data.get('fcm_token')  
#         if not email or not password:
#             return Response({
#                 'message': 'email and password are required.'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         user = authenticate(request, email=email, password=password)
        
#         if user is not None and user.is_active:
#             # Save the FCM token
#             if fcm_token:
#                 user.fcm_token = fcm_token
#                 user.save()

#             # Token creation
#             refresh = RefreshToken.for_user(user)
            
#             # Customizing access token expiration
#             custom_lifetime = timedelta(minutes=15)
#             access_token = refresh.access_token
#             access_token.set_exp(lifetime=custom_lifetime)

#             # Send Welcome Notification
#             if user.fcm_token:
#                 title = "Welcome!"
#                 body = f"Hello {user.username}, you have successfully logged in."
#                 notification_response = send_firebase_notification(user.fcm_token, title, body)
#                 print("Firebase Response:", notification_response)

#                 # Save the notification in the database
#                 notification = Notification(
#                     user=user,
#                     title=title,
#                     message=body,
#                     is_sent=True  # Indicating the notification was sent successfully
#                 )
#                 notification.save()

#             return Response({
#                 'message': 'Login successful',
#                 'user_id': user.id,
#                 'access_token': str(access_token),
#                 'refresh_token': str(refresh),
#                 'notification_status': 'Notification sent successfully' if user.fcm_token else 'No FCM token available'
#             }, status=status.HTTP_200_OK)
        
#         return Response({
#             'message': 'Login failed: Invalid credentials or inactive user'
#         }, status=status.HTTP_400_BAD_REQUEST)





# class CustomObtainTokenView(APIView):
#     permission_classes = [AllowAny]
    
#     def post(self, request, *args, **kwargs):
#         username = request.data.get('username')
#         password = request.data.get('password')
#         fcm_token = request.data.get('fcm_token') 

#         if not username or not password:
#             return Response({
#                 'message': 'Username and password are required.'
#             }, status=status.HTTP_400_BAD_REQUEST)

#         user = authenticate(request, username=username, password=password)
        
#         if user is not None and user.is_active:
#             # FCM Token save
#             if fcm_token:
#                 user.fcm_token = fcm_token
#                 user.save()

#             # Token creation
#             refresh = RefreshToken.for_user(user)
            
#             # Customizing access token expiration
#             custom_lifetime = timedelta(minutes=15)
#             access_token = refresh.access_token
#             access_token.set_exp(lifetime=custom_lifetime)
#             # Print the access_token and its expiration time
#             print(f"Access Token: {str(access_token)}")
#             print(f"Access Token Expiration: {access_token['exp']}")
            
            
#             return Response({
#                 'message': 'Login successful',
#                 'user_id': user.id,
#                 'access_token': str(access_token),
#                 'refresh_token': str(refresh)
#             }, status=status.HTTP_200_OK)
        
#         return Response({
#             'message': 'Login failed: Invalid credentials or inactive user'
#         }, status=status.HTTP_400_BAD_REQUEST)





class CustomRegisterUserView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        first_name = request.data.get('first_name')
        last_name = request.data.get('last_name')
        username = request.data.get('username')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        if not first_name:
            return Response({'message': 'First name is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not last_name:
            return Response({'message': 'Last name is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not username:
            return Response({'message': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'message': 'username is already in use'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not email:
            return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return Response({'message': 'Invalid email format'}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(email=email).exists():
            return Response({'message': 'Email is already in use'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not phone_number:
            return Response({'message': 'Phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone_number=phone_number).exists():
            return Response({'message': 'Phone number is already in use'}, status=status.HTTP_400_BAD_REQUEST)

        if not password:
            return Response({'message': 'Password is required'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 8 or not re.search(r'[A-Za-z]', password) or not re.search(r'[0-9]', password):
            return Response({'message': 'Password must be at least 8 characters long and contain both letters and numbers'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Nick name 
            nick_name = f"{first_name} {last_name}"
            print('nick_name',nick_name)

            
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                phone_number=phone_number,
                password=password,
                nick_name=nick_name
            )
            return Response({
                'message': 'User registered successfully',
                'user_id': user.id,
                'username': user.username,
            }, status=status.HTTP_201_CREATED)
        
        except ValidationError as e:
            return Response({
                'message': 'User registration failed',
                'errors': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)




class FollowUserAPIView(APIView):
    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')
        user_to_follow_id = request.data.get('user_to_follow')

        try:
            user = User.objects.get(id=user_id)
            user_to_follow = User.objects.get(id=user_to_follow_id)

            if user == user_to_follow:
                return Response({'message': 'You cannot follow yourself'}, status=status.HTTP_400_BAD_REQUEST)

            if Follower.objects.filter(user=user, followed_user=user_to_follow).exists():
                return Response({'message': 'You are already following this user'}, status=status.HTTP_400_BAD_REQUEST)

            Follower.objects.create(user=user, followed_user=user_to_follow)
            return Response({'message': f'User {user.username} is now following {user_to_follow.username}'}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



# class UserWithFollowersCountAPIView(APIView):
#     permission_classes = [AllowAny]
#     def get(self, request, user_id, *args, **kwargs):
#         try:
#             user = User.objects.get(id=user_id)


#             followers_count = user.followers.count()
#             following_count = user.following.count()
#             visitor_count = UserProfileVisit.objects.get(user=user)
            

#             data = {
#                 'user': {
#                     'id': user.id,
#                     'username': user.username,
#                 },
#                 'followers_count': followers_count,
#                 'following_count': following_count,
#                 'visitor_count': visitor_count.visit_count
#             }
#             return Response(data, status=status.HTTP_200_OK)

#         except User.DoesNotExist:
#             return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class UserWithFollowersCountAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)

            with transaction.atomic():
                if not hasattr(user, 'followers'):
                    user.followers.create()  
                if not hasattr(user, 'following'):
                    user.following.create()

            user_profile_visit, created = UserProfileVisit.objects.get_or_create(user=user, defaults={'visit_count': 0})

            followers_count = user.followers.count()
            following_count = user.following.count()

            data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                },
                'followers_count': followers_count,
                'following_count': following_count,
                'visitor_count': user_profile_visit.visit_count
            }

            return Response(data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class ProfileVisitCountAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)
            profile_visit, created = UserProfileVisit.objects.get_or_create(user=user)

            profile_visit.visit_count += 1
            profile_visit.save()

            data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                },
                'visit_count': profile_visit.visit_count,
            }
            return Response(data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)





# class SendInviteAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         inviter_id = kwargs.get('inviter_id') 
#         email = request.data.get('email')  
#         phone = request.data.get('phone')

#         if not email and not phone:
#             return Response({'message': 'Either email or phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             inviter = User.objects.get(id=inviter_id)


#             if email and Invitation.objects.filter(email=email, inviter=inviter).exists():
#                 return Response({'message': 'Invitation already sent to this email'}, status=status.HTTP_400_BAD_REQUEST)

#             if phone and Invitation.objects.filter(phone=phone, inviter=inviter).exists():
#                 return Response({'message': 'Invitation already sent to this phone number'}, status=status.HTTP_400_BAD_REQUEST)


#             invitation = Invitation.objects.create(
#                 inviter=inviter,
#                 email=email,
#                 phone=phone
#             )

#             if email:
#                 invite_link = f"http://example.com/register?token={invitation.token}"
#                 send_mail(
#                     'You are invited!',
#                     f"Hello! You have been invited by {inviter.username}. Click the link to register: {invite_link}",
#                     'noreply@example.com',
#                     [email],
#                     fail_silently=False,
#                 )
#                 message = f'Invitation sent to {email}'


#             elif phone:

#                 invite_link = f"http://example.com/register?token={invitation.token}"
#                 message = f'Invitation sent to {phone}'

#             return Response({'message': message}, status=status.HTTP_201_CREATED)

#         except User.DoesNotExist:
#             return Response({'message': 'Inviter not found'}, status=status.HTTP_404_NOT_FOUND)


class SendInviteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        inviter_id = kwargs.get('inviter_id') 
        email = request.data.get('email')  
        phone = request.data.get('phone')

        if not email and not phone:
            return Response({'message': 'Either email or phone number is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            inviter = User.objects.get(id=inviter_id)

            # Check if the wallet for the inviter exists, if not, create it
            wallet, created = Wallet.objects.get_or_create(user=inviter)


            if email and Invitation.objects.filter(email=email, inviter=inviter).exists():
                return Response({'message': 'Invitation already sent to this email'}, status=status.HTTP_400_BAD_REQUEST)


            if phone and Invitation.objects.filter(phone=phone, inviter=inviter).exists():
                return Response({'message': 'Invitation already sent to this phone number'}, status=status.HTTP_400_BAD_REQUEST)


            invitation = Invitation.objects.create(
                inviter=inviter,
                email=email,
                phone=phone
            )

            message = 'Invitation created successfully'
            if email:
                message += f' to {email}'
            if phone:
                message += f' to {phone}'

            return Response({'message': message}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'message': 'Inviter not found'}, status=status.HTTP_404_NOT_FOUND)



# class AcceptInviteAPIView(APIView):
#     def post(self, request, *args, **kwargs):
#         token = request.data.get('token') 

#         try:
#             invitation = Invitation.objects.get(token=token)

#             if invitation.is_accepted:
#                 return Response({'message': 'Invitation already accepted'}, status=status.HTTP_400_BAD_REQUEST)


#             invitation.is_accepted = True
#             invitation.save()


#             inviter_wallet = Wallet.objects.get(user=invitation.inviter)
#             inviter_wallet.gold_coins += 10 
#             inviter_wallet.save()

#             return Response({'message': 'Invitation accepted and coins added'}, status=status.HTTP_200_OK)

#         except Invitation.DoesNotExist:
#             return Response({'message': 'Invalid token'}, status=status.HTTP_404_NOT_FOUND)



class AcceptInviteAPIView(APIView):
    def post(self, request, *args, **kwargs):
        inviter_id = request.data.get('inviter_id')  
        gold_coins = request.data.get('gold_coins', 0)  
        diamond_coins = request.data.get('diamond_coins', 0)

        if not inviter_id:
            return Response({'message': 'Inviter ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        
        if not self.is_valid_coin_value(gold_coins) or not self.is_valid_coin_value(diamond_coins):
            return Response({'message': 'Invalid coin values provided. They must be integers.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            inviter = User.objects.get(id=inviter_id)
            inviter_wallet = Wallet.objects.get(user=inviter)


            gold_coins = int(gold_coins) if gold_coins else 0
            diamond_coins = int(diamond_coins) if diamond_coins else 0


            if gold_coins:
                inviter_wallet.gold_coins += gold_coins
            if diamond_coins:
                inviter_wallet.diamond_coins += diamond_coins

            inviter_wallet.save()

            return Response({'message': 'Invitation accepted and coins added'}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': 'Inviter not found'}, status=status.HTTP_404_NOT_FOUND)
        except Wallet.DoesNotExist:
            return Response({'message': 'Wallet not found for the inviter'}, status=status.HTTP_404_NOT_FOUND)

    def is_valid_coin_value(self, value):

        if value == '' or value is None:  
            return True
        try:
            int(value) 
            return True
        except ValueError:
            return False



class SingleInviteStatusAPIView(APIView):
    def get(self, request, *args, **kwargs):
        # Get email or phone from request query parameters
        email = request.query_params.get('email')
        phone = request.query_params.get('phone')

        if not email and not phone:
            return Response({'message': 'Either email or phone number is required to check invite status'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            if email:
                invitation = Invitation.objects.get(email=email)
            elif phone:
                invitation = Invitation.objects.get(phone=phone)

            status_message = 'Accepted' if invitation.is_accepted else 'Not Accepted'

            return Response({
                'email': invitation.email,
                'phone': invitation.phone,
                'inviter': invitation.inviter.username,
                'status': status_message
            }, status=status.HTTP_200_OK)

        except Invitation.DoesNotExist:
            return Response({'message': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)




class InviteStatusAPIView(APIView):
    def get(self, request, *args, **kwargs):
        inviter_id = request.query_params.get('inviter_id')

        if not inviter_id:
            return Response({'message': 'Inviter ID is required to check invitation status'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            inviter = User.objects.get(id=inviter_id)
            invitations = Invitation.objects.filter(inviter=inviter)

            accepted_count = invitations.filter(is_accepted=True).count()
            not_accepted_count = invitations.filter(is_accepted=False).count()

            total_invitations = invitations.count()

            return Response({
                'inviter': inviter.username,
                'total_invitations': total_invitations,
                'accepted_count': accepted_count,
                'not_accepted_count': not_accepted_count
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': 'Inviter not found'}, status=status.HTTP_404_NOT_FOUND)



class GetCoinsAPIView(APIView):
    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({'message': 'User ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            wallet = Wallet.objects.get(user=user)

            return Response({
                'username': user.username,
                'gold_coins': wallet.gold_coins,
                'diamond_coins': wallet.diamond_coins
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Wallet.DoesNotExist:
            return Response({'message': 'Wallet not found for the user'}, status=status.HTTP_404_NOT_FOUND)





class UploadMultipleImagesAPIView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]  

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('user_id')

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        images = request.FILES.getlist('image')
        print('request.FILES',request.FILES)
        # print('images',images)
        if not images:
            return Response({'message': 'No images provided'}, status=status.HTTP_400_BAD_REQUEST)

        uploaded_images = []
        for image in images:
            image_instance = Image(user=user, image=image)
            image_instance.save()
            uploaded_images.append({
                'id': image_instance.id,
                'image_url': image_instance.image.url
            })

        return Response({
            'message': 'Images uploaded successfully',
            'images': uploaded_images
        }, status=status.HTTP_201_CREATED)



class CreateOrUpdateWalletAPIView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user')
        gold_coins = int(request.data.get('gold_coins', 0))

        wallet = Wallet.objects.filter(user_id=user_id).first()

        if wallet:
            wallet.gold_coins += gold_coins
            wallet.save()
            serializer = WalletSerializer(wallet)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            wallet_data = {
                'user': user_id,
                'gold_coins': gold_coins,
            }
            serializer = WalletSerializer(data=wallet_data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class CountryListAPIView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        countries = Country.objects.all()
        serializer = CountrySerializer(countries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)





class UserUpdateAPIView(APIView):
    # permission_classes = [IsAuthenticated]  
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user') 
        if not user_id:
            return Response({
                'message': 'User ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, id=user_id)
        serializer = UserUpdateImageSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({
                'message': 'User ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = get_object_or_404(User, id=user_id)
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)

        # Custom validation for fields
        nick_name = request.data.get('nick_name')
        if nick_name and len(nick_name) < 3:
            return Response({
                'message': 'Nick name must be at least 3 characters long.'
            }, status=status.HTTP_400_BAD_REQUEST)

        bio = request.data.get('bio')
        gender = request.data.get('gender')
        country = request.data.get('country')
        birthday = request.data.get('birthday')


        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'User information updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileImageUpdateAPIView(APIView):
    permission_classes = [AllowAny]

    def put(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')  
        user = get_object_or_404(User, id=user_id)
        
        profile_image = request.FILES.get('profile')

        if not profile_image:
            return Response({
                'message': 'Profile image is required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user.profile = profile_image
        user.save()

        return Response({
            'message': 'Profile image updated successfully',
            'profile_url': user.profile.url if user.profile else None
        }, status=status.HTTP_200_OK)






class UserWalletCountAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'message': 'user_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            user_wallet = Wallet.objects.get(user=user)

            data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                },
                'user_wallet_gold_coins': user_wallet.gold_coins,
                'user_wallet_diamond_coins': user_wallet.diamond_coins
            }
            return Response(data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        except Wallet.DoesNotExist:
            return Response({'message': 'Wallet not found for the user'}, status=status.HTTP_404_NOT_FOUND)


