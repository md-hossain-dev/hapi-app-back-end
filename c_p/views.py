from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CoupleRelationship, CPLevel, RelationshipLog
from .serializers import CPLevelCreateSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from hapi_app.models import User,Wallet,WalletLog
from .serializers import SimpleInviteSerializer
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from django.db import models
from django.db import transaction

class CPLevelCreateAPIView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]
    def post(self, request, *args, **kwargs):
        serializer = CPLevelCreateSerializer(data=request.data)
        
        # Serializer validation
        if serializer.is_valid():
            # Save the new CPLevel instance
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        # If validation fails
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CreateRelationshipInviteView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]

    def post(self, request, user1_id, *args, **kwargs):
        # Parse incoming data using serializer
        serializer = SimpleInviteSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user2_id = serializer.validated_data['user2_id']
        cp_level_id = 1

        # Fetch related objects
        user1 = get_object_or_404(User, id=user1_id)  # Fetch user1 from URL parameter
        user2 = get_object_or_404(User, id=user2_id)  # Fetch user2 from request data
        cp_level = get_object_or_404(CPLevel, id=cp_level_id)  # Fetch CPLevel

        if CoupleRelationship.objects.filter(user1=user1, is_active=False).exists():
            return Response({'message': 'Invite is already Send'}, status=status.HTTP_400_BAD_REQUEST)
        
        if CoupleRelationship.objects.filter(user2=user2, is_active=False).exists():
            return Response({'message': 'Invite is already Send'}, status=status.HTTP_400_BAD_REQUEST)
        

        # Validation: user1 and user2 cannot be the same
        if user1 == user2:
            return Response(
                {"error": "A user cannot create a relationship with themselves."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validation: Check if user1 or user2 is already in an active relationship
        if CoupleRelationship.objects.filter(user1=user1, is_active=True).exists() or \
           CoupleRelationship.objects.filter(user2=user1, is_active=True).exists():
            return Response(
                {"error": f"{user1.username} is already in an active relationship."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if CoupleRelationship.objects.filter(user1=user2, is_active=True).exists() or \
           CoupleRelationship.objects.filter(user2=user2, is_active=True).exists():
            return Response(
                {"error": f"{user2.username} is already in an active relationship."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Validation: Check if user1 has enough coins in wallet
        if user1.wallet.gold_coins < cp_level.level_up_coins:
            return Response(
                {"error": "Insufficient coins in wallet to send invitation."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Deduct coins from user1's wallet
        user1.wallet.gold_coins -= cp_level.level_up_coins
        user1.wallet.save()

        # Create CoupleRelationship instance with is_active=False
        relationship = CoupleRelationship.objects.create(
            user1=user1,
            user2=user2,
            cp_level=cp_level,
            is_active=False  # Relationship becomes active only after acceptance
        )

        # Log the creation action
        RelationshipLog.objects.create(
            relationship=relationship.id,
            action='created',
            coins_transferred=cp_level.level_up_coins,
            description=f"Relationship invitation sent by {user1.username} to {user2.username}."
        )

        # WalletLog  creation
        # print('user_id', user1)
        WalletLog.objects.create(
            user=user1,
            action='debit',
            coins_amount=cp_level.level_up_coins,
            wallet_description=f"Relationship invitation sent by {user1.username}."
        )

        return Response({
            "message": "Relationship invitation sent successfully.",
            "relationship_id": relationship.id
        }, status=status.HTTP_201_CREATED)



class AcceptOrDeclineRelationshipView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]


    def post(self, request, relationship_id, *args, **kwargs):
        # Extract the action (yes or no) from the form data
        action = request.data.get('action')  # 'yes' or 'no'

        if action not in ['yes', 'no']:
            return Response({"error": "Invalid action. Please send 'yes' or 'no'."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the relationship by ID
        relationship = get_object_or_404(CoupleRelationship, id=relationship_id)


        user2 = request.data.get('user2')
        user2 = get_object_or_404(User, id=user2)
        if user2 != relationship.user2:
            return Response({"error": "You are not authorized to take this action."}, status=status.HTTP_403_FORBIDDEN)

        # If action is "yes", accept the relationship
        if action == 'yes':
            
            cp_level = relationship.cp_level
            user2.wallet.gold_coins += cp_level.level_up_coins
            user2.wallet.save()

            # Update the relationship status to active
            relationship.is_active = True
            relationship.save()

            # Log the acceptance action
            RelationshipLog.objects.create(
                relationship=relationship.id,
                action='accepted',
                coins_transferred=cp_level.level_up_coins,
                description=f"Relationship accepted by {user2.username}."
            )

            WalletLog.objects.create(

	            user=user2,
	            action='credit',
	            coins_amount=cp_level.level_up_coins,
	            wallet_description=f"Relationship accepted by {user2.username}."
	        )


            return Response({"message": "Relationship accepted successfully."}, status=status.HTTP_200_OK)

        if action == 'no':
            # Refund coins to user1's wallet
            cp_level = relationship.cp_level
            user1 = relationship.user1
            user1.wallet.gold_coins += cp_level.level_up_coins
            user1.wallet.save()

            # Delete the relationship (or mark as cancelled)
            relationship_delete = get_object_or_404(CoupleRelationship, id=relationship_id)
            relationship_delete.delete()

            # Log the decline action
            RelationshipLog.objects.create(
                relationship=relationship.id,
                action='declined',
                coins_transferred=cp_level.level_up_coins,
                description=f"Relationship declined by {user2.username}."
            )

            WalletLog.objects.create(
            	
	            user=user1,
	            action='credit',
	            coins_amount=cp_level.level_up_coins,
	            wallet_description=f"Relationship declined by {user2.username}."
	        )

            return Response({"message": "Relationship invitation declined."}, status=status.HTTP_200_OK)



class CheckAndCancelExpiredRelationships(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]
    def get(self, request, *args, **kwargs):
        # Set the expiration time
        # expiration_time = timedelta(days=7)
        expiration_time = timedelta(minutes=1)
        now = timezone.now()

        # Find all inactive relationships that are older than the expiration time
        expired_relationships = CoupleRelationship.objects.filter(
            is_active=False,
            created_at__lte=now - expiration_time
        )

        # Cancel each expired relationship and refund coins to user1
        for relationship in expired_relationships:
            # Refund coins to user1's wallet
            cp_level = relationship.cp_level
            user1 = relationship.user1

            # Refund the level_up_coins to user1's wallet if the relationship is expired
            user1.wallet.gold_coins += cp_level.level_up_coins
            user1.wallet.save()

            # Log the cancellation and coin refund
            RelationshipLog.objects.create(
                relationship=relationship.id,
                action='expired',
                coins_transferred=cp_level.level_up_coins,
                description=f"Relationship with ID {relationship.id} expired and cancelled. Coins refunded to {user1.username}."
            )
            WalletLog.objects.create(
	            user=user1,
	            action='credit',
	            coins_amount=cp_level.level_up_coins,
	            wallet_description=f"Relationship with ID {relationship.id} expired and cancelled. Coins refunded to {user1.username}."
	        )


            # Mark relationship as delete
            relationship.delete()

        return Response({
            "message": f"{expired_relationships.count()} expired relationships cancelled"
        }, status=status.HTTP_200_OK) 




class LevelUpGiftAPIView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        # User who will be debited comes from URL parameters
        user1_id = kwargs.get('user_id')
        # User who will be credited comes from request data
        user2_id = request.data.get('user2_id')

        # Retrieve users by ID
        user1 = get_object_or_404(User, id=user1_id)  # Debit user
        user2 = get_object_or_404(User, id=user2_id)  # Credit user

        # Check for the current active relationship
        relationship = CoupleRelationship.objects.filter(
            (models.Q(user1=user1) & models.Q(user2=user2)) |
            (models.Q(user1=user2) & models.Q(user2=user1)),
            is_active=True
        ).last()

        if not relationship:
            return Response({"error": "Users are not in an active relationship."},
                            status=status.HTTP_400_BAD_REQUEST)

        # Retrieve the current cp_level
        current_cp_level = relationship.cp_level
        print('current_cp_level', current_cp_level)

        # # Check if the debit user has enough coins
        # if user1.wallet.gold_coins < current_cp_level.level_up_coins:
        #     return Response({"error": f"{user1.username} does not have enough coins to gift."},
        #                     status=status.HTTP_400_BAD_REQUEST)

        # # Deduct coins from the debit user
        # user1.wallet.gold_coins -= current_cp_level.level_up_coins
        # user1.wallet.save()

        # # Add coins to the credit user
        # user2.wallet.gold_coins += current_cp_level.level_up_coins
        # user2.wallet.save()

        # Determine the next level
        next_cp_level = None

        if relationship.is_active and current_cp_level.id == 1:
            next_cp_level = CPLevel.objects.get(id=2)
            print('next_cp_level 2', next_cp_level)

            if user1.wallet.gold_coins < next_cp_level.level_up_coins:
                return Response({"error": f"{user1.username} does not have enough coins to gift."},
                                status=status.HTTP_400_BAD_REQUEST)

            user1.wallet.gold_coins -= next_cp_level.level_up_coins
            user1.wallet.save()

            user2.wallet.gold_coins += next_cp_level.level_up_coins
            user2.wallet.save()

        elif relationship.is_active and relationship.level_up and current_cp_level.id == 2:
            next_cp_level = CPLevel.objects.get(id=3)
            print('next_cp_level 3', next_cp_level)

            if user1.wallet.gold_coins < next_cp_level.level_up_coins:
                return Response({"error": f"{user1.username} does not have enough coins to gift."},
                                status=status.HTTP_400_BAD_REQUEST)

            user1.wallet.gold_coins -= next_cp_level.level_up_coins
            user1.wallet.save()

            user2.wallet.gold_coins += next_cp_level.level_up_coins
            user2.wallet.save()

        elif relationship.is_active and relationship.level_up and current_cp_level.id == 3:
            next_cp_level = CPLevel.objects.get(id=4)
            print('next_cp_level 4', next_cp_level)

            if user1.wallet.gold_coins < next_cp_level.level_up_coins:
                return Response({"error": f"{user1.username} does not have enough coins to gift."},
                                status=status.HTTP_400_BAD_REQUEST)

            user1.wallet.gold_coins -= next_cp_level.level_up_coins
            user1.wallet.save()

            user2.wallet.gold_coins += next_cp_level.level_up_coins
            user2.wallet.save()

        elif relationship.is_active and relationship.level_up and current_cp_level.id == 4:
            next_cp_level = CPLevel.objects.get(id=5)
            print('next_cp_level 5', next_cp_level)

            if user1.wallet.gold_coins < next_cp_level.level_up_coins:
                return Response({"error": f"{user1.username} does not have enough coins to gift."},
                                status=status.HTTP_400_BAD_REQUEST)

            user1.wallet.gold_coins -= next_cp_level.level_up_coins
            user1.wallet.save()

            user2.wallet.gold_coins += next_cp_level.level_up_coins
            user2.wallet.save()
        elif relationship.is_active and relationship.level_up and current_cp_level.id == 5:
            next_cp_level = CPLevel.objects.get(id=6)
            print('next_cp_level 6', next_cp_level)

            if user1.wallet.gold_coins < next_cp_level.level_up_coins:
                return Response({"error": f"{user1.username} does not have enough coins to gift."},
                                status=status.HTTP_400_BAD_REQUEST)

            user1.wallet.gold_coins -= next_cp_level.level_up_coins
            user1.wallet.save()

            user2.wallet.gold_coins += next_cp_level.level_up_coins
            user2.wallet.save()

        if next_cp_level:
            # Create new CoupleRelationship for the next level
            new_relationship = CoupleRelationship.objects.create(
                user1=user1,
                user2=user2,
                cp_level=next_cp_level,
                is_active=True,
                level_up=True
            )

            # Log the action
            RelationshipLog.objects.create(
                relationship=new_relationship.id,
                action='level_up',
                coins_transferred=current_cp_level.level_up_coins,
                description=f"{user1.username} gifted {user2.username} and leveled up to {next_cp_level.level_name}."
            )

            # Log wallet transactions
            WalletLog.objects.create(
                user=user1,
                action='debit',
                coins_amount=current_cp_level.level_up_coins,
                wallet_description=f"Coins used for leveling up to {next_cp_level.level_name}."
            )

            WalletLog.objects.create(
                user=user2,
                action='credit',
                coins_amount=current_cp_level.level_up_coins,
                wallet_description=f"Coins received from {user1.username} for leveling up to {next_cp_level.level_name}."
            )

            return Response({
                "message": f"Level Up successful to {next_cp_level.level_name}. Coins deducted and relationship updated.",
                "new_relationship_id": new_relationship.id,
                "new_cp_level": next_cp_level.level_name
            }, status=status.HTTP_200_OK)

        return Response({"error": "Level up not possible or already at the maximum level."},
                        status=status.HTTP_400_BAD_REQUEST)





class CancelAllRelationshipsAPIView(APIView):

    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)

        relationships = CoupleRelationship.objects.filter(
            models.Q(user1=user) | models.Q(user2=user)
        )

        if not relationships.exists():
            return Response(
                {"error": "No active relationships found for this user."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.wallet.gold_coins < 50000:
            return Response(
                {"error": "Insufficient coins to cancel all relationships."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            with transaction.atomic():
                # relationships.delete()

                for relationship in relationships:
                    RelationshipLog.objects.create(
                        relationship=relationship.id,
                        action='cancel',
                        coins_transferred=50000,
                        description=f"Relationship canceled by {user.username}."
                    )

                relationships.delete()

                user.wallet.gold_coins -= 50000
                user.wallet.save()

                WalletLog.objects.create(
                    user=user,
                    action='debit',
                    coins_amount=50000,
                    wallet_description="Coins deducted for canceling all relationships."
                )

                return Response(
                    {"message": "All relationships canceled successfully. 50000 coins deducted."},
                    status=status.HTTP_200_OK
                )
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
