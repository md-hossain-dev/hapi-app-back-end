from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .models import CreateFamily, FamilyMember
from .serializers import CreateFamilySerializer, FamilyMemberSerializer
from django.shortcuts import get_object_or_404
from hapi_app.models import User,Wallet,WalletLog
from django.utils.timezone import now, timedelta
from .utils import calculate_family_contribution
from django.db import models

class CreateFamilyAPIView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CreateFamilySerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.query_params.get("user_id")
            user = get_object_or_404(User, id=user_id)

            if CreateFamily.objects.filter(created_by=user).exists():
	            return Response(
	                {"error": f"User already Create Family"},
	                status=status.HTTP_400_BAD_REQUEST
	            )

            # Check if user is VIP
            if user.is_svip:
                serializer.save(created_by=user)
            else:
                # Deduct coins for non-VIP users
                if user.wallet.gold_coins >= 10000:
                    user.wallet.gold_coins -= 10000
                    user.save()
                    serializer.save(created_by=user)
                    WalletLog.objects.create(
                        user=user,
                        action='debit',
                        coins_amount=10000,
                        wallet_description="Create Family"
                    )
                else:
                    return Response(
                        {"error": "Not enough coins to create a family."},
                        status=status.HTTP_400_BAD_REQUEST
                    )


            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FamilyMemberAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        family_id = request.data.get("family_id")
        user_id = request.data.get("user_id")

        if not family_id or not user_id:
            return Response(
                {"error": "Both 'family_id' and 'user_id' are required."},
                status=status.HTTP_400_BAD_REQUEST
            )


        user = get_object_or_404(User, id=user_id)
        family = get_object_or_404(CreateFamily, id=family_id)


        if FamilyMember.objects.filter(user=user).exists():
            return Response(
                {"error": "You are already in a family."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if family.members.count() >= 50:
            return Response(
                {"error": "Family is full. Cannot join more members."},
                status=status.HTTP_400_BAD_REQUEST
            )

        family_min_level = family.level  
        print("family_min_level",family_min_level)
        user_level = user.level 
        print("user_level",user_level) 

        if not user_level or user_level.id < family_min_level.id:
            return Response(
                {"error": f"You need to be at least level {family_min_level.level_name} to join this family."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if user.country != family.created_by.country:
            return Response(
                {"error": "You can only join families in your country."},
                status=status.HTTP_400_BAD_REQUEST
            )

        family_member = FamilyMember.objects.create(user=user, family=family)

        return Response(
            {
                "message": f"You have successfully joined the family '{family.name}'.",
                "family_member_id": family_member.id,
            },
            status=status.HTTP_201_CREATED
        )



class ManageFamilyMemberAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]  

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        created_id = request.data.get("created_id")
        family_id = request.data.get("family_id")
        action = request.data.get("action") 


        if not all([user_id, family_id, action]):
            return Response(
                {"error": "user_id, family_id, and action are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = get_object_or_404(User, id=created_id)


        family = get_object_or_404(CreateFamily, id=family_id)

        if family.created_by != user:
            return Response(
                {"error": "You are not the owner of this family."},
                status=status.HTTP_403_FORBIDDEN
            )


        family_member = get_object_or_404(FamilyMember, user__id=user_id, family=family)

        if action == "accept":
            # Accept the member
            family_member.is_join = True
            family_member.save()
            return Response(
                {"message": f"User {family_member.user.username} has been accepted into the family '{family.name}'."},
                status=status.HTTP_200_OK
            )

        elif action == "decline":
            # Decline the member and delete their data
            family_member.delete()
            return Response(
                {"message": f"User {user_id} has been declined and removed from the family '{family.name}'."},
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"error": "Invalid action. Use 'accept' or 'decline'."},
                status=status.HTTP_400_BAD_REQUEST
            )



class LeaveFamilyAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny] 

    def post(self, request, *args, **kwargs):
        user_id = request.data.get("user_id")
        user = get_object_or_404(User, id=user_id)

        try:
            family_member = FamilyMember.objects.get(user=user)
        except FamilyMember.DoesNotExist:
            return Response(
                {"error": "You are not part of any family."},
                status=status.HTTP_400_BAD_REQUEST
            )

        family = family_member.family

        family_member.delete()

        return Response(
            {"message": f"You have successfully left the family '{family.name}'."},
            status=status.HTTP_200_OK
        )



class DeleteInactiveFamiliesAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny] 

    def delete(self, request, *args, **kwargs):
        # seven_days_ago = now() - timedelta(days=7)
        seven_days_ago = now() - timedelta(minutes=1)
        families_to_delete = []


        for family in CreateFamily.objects.all():
            if family.members.count() == 1:
                # Check if the family was created 7 or more days ago
                if family.created_at <= seven_days_ago:
                    families_to_delete.append(family)

        for family in families_to_delete:
            # Delete the single member
            FamilyMember.objects.filter(family=family).delete()
            # Delete the family
            family.delete()

        return Response(
            {"message": f"{len(families_to_delete)} families have been deleted."},
            status=status.HTTP_200_OK
        )



class FamilyContributionAPI(APIView):

    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny] 

    def get(self, request):
        try:
            family_id = request.data.get("family_id")
            family = CreateFamily.objects.get(id=family_id)
            total_contribution = calculate_family_contribution(family)
            data = {
                "family_name": family.name,
                "total_contribution": total_contribution,
                "bonus_level": family.bonus_level,
                "members": [
                    {
                        "username": member.user.username,
                        "contribution": member.contribution,
                        "is_leader": member.is_leader,
                        "reward": member.reward
                    } for member in family.members.all()
                ]
            }
            return Response(data, status=status.HTTP_200_OK)
        except CreateFamily.DoesNotExist:
            return Response({"error": "Family not found"}, status=status.HTTP_404_NOT_FOUND)
