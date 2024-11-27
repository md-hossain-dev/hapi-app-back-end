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


class CustomObtainTokenView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        fcm_token = request.data.get('fcm_token') 

        if not username or not password:
            return Response({
                'message': 'Username and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_active:
            # FCM Token save
            if fcm_token:
                user.fcm_token = fcm_token
                user.save()

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            return Response({
                'message': 'Login successful',
                'user_id': user.id,
                'access_token': access_token,
                'refresh_token': refresh_token
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'Login failed: Invalid credentials or inactive user'
        }, status=status.HTTP_400_BAD_REQUEST)




class CustomRegisterUserView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        
        if not username:
            return Response({'message': 'Username is required'}, status=status.HTTP_400_BAD_REQUEST)

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
            user = User.objects.create_user(
                username=username,
                email=email,
                phone_number=phone_number,
                password=password
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



class UserWithFollowersCountAPIView(APIView):
    def get(self, request, user_id, *args, **kwargs):
        try:
            user = User.objects.get(id=user_id)


            followers_count = user.followers.count()
            following_count = user.following.count()

            data = {
                'user': {
                    'id': user.id,
                    'username': user.username,
                },
                'followers_count': followers_count,
                'following_count': following_count,
            }
            return Response(data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)



class ProfileVisitCountAPIView(APIView):
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











