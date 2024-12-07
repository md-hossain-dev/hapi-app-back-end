from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MedalInfo,UserMedal
from .serializers import MedalInfoSerializer,UserMedalSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from hapi_app.models import User
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.core.files.storage import default_storage

class MedalInfoCreateAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = MedalInfoSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class MedalInfoByTypeAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        medal_type = request.query_params.get('medal_type')
        
        if not medal_type:
            return Response({'message': 'medal_type parameter is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        medals = MedalInfo.objects.filter(medal_type=medal_type)
        
        if not medals.exists():
            return Response({'message': f'No medals found for type {medal_type}'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = MedalInfoSerializer(medals, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UpdateOrCreateUserMedalAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        medal_id = request.data.get('medal_id')

        # Validate required fields
        if not user_id or not medal_id:
            return Response({
                'message': 'user_id and medal_id are required.'
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Fetch user and medal objects
            user = User.objects.get(id=user_id)
            medal = MedalInfo.objects.get(id=medal_id)

            # Check if UserMedal exists
            user_medal, created = UserMedal.objects.get_or_create(
                user=user,
                medal=medal,
                defaults={'send_count': 1}
            )

            # If already exists, increment send_count
            if not created:
                user_medal.send_count += 1
                user_medal.save()

            # Serialize and return the UserMedal
            serializer = UserMedalSerializer(user_medal)
            return Response({
                'message': 'UserMedal updated successfully.' if not created else 'UserMedal created successfully.',
                'data': serializer.data
            }, status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        except MedalInfo.DoesNotExist:
            return Response({'message': 'Medal not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





class UpdateUserMedalsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        medals = MedalInfo.objects.all()
        
        for medal in medals:
            
            user_medals = UserMedal.objects.filter(medal=medal)
            for user_medal in user_medals:
                if user_medal.send_count >= medal.medal_send_count:
                    user_medal.is_show = True
                else:
                    user_medal.is_show = False
                user_medal.save()

        return Response({
            'message': 'User medals updated based on medal_send_count.'
        }, status=status.HTTP_200_OK)



class SingleUserMedalsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({'message': 'user_id parameter is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(id=user_id)
            user_medals = UserMedal.objects.filter(user=user, is_show=True)

            data = []
            for user_medal in user_medals:
                medal_data = {
                    'medal_name': user_medal.medal.medal_name,
                    'medal_type': user_medal.medal.medal_type,
                    'send_count': user_medal.send_count,
                    'is_show': user_medal.is_show,
                    'created_at': user_medal.created_at,
                    'updated_at': user_medal.updated_at,
                }
                
                if user_medal.medal.medal_image:
                    medal_data['medal_image_url'] = user_medal.medal.medal_image.url

                data.append(medal_data)

            return Response(data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)