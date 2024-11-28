from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
from .models import CreateFamily, FamilyMember,BonusLevel
from .serializers import CreateFamilySerializer,CreateFamilyNEWSerializer, FamilyMemberSerializer
from django.shortcuts import get_object_or_404
from hapi_app.models import User,Wallet,WalletLog
from django.utils.timezone import now, timedelta
from .utils import calculate_family_contribution
from django.db import models
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta

class CreateFamilyAPIView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = CreateFamilyNEWSerializer(data=request.data)
        if serializer.is_valid():
            user_id = request.query_params.get("user_id")
            print('user_id', user_id)
            user = get_object_or_404(User, id=user_id)
            print('user', user)

            if CreateFamily.objects.filter(created_by=user).exists():
	            return Response(
	                {"error": f"User already Create Family"},
	                status=status.HTTP_400_BAD_REQUEST
	            )

            # created_by=request.get(user)

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



from rest_framework.exceptions import ValidationError
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone

from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum
from datetime import timedelta
from django.utils import timezone

class WeeklyFamilyAndMemberContributionAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny] 
    def post(self, request, *args, **kwargs):
        try:
            now = timezone.now()
            last_week = now - timedelta(days=7)

            families = CreateFamily.objects.all()

            for family in families:
                total_family_contribution = 0  # Initialize family contribution tracking
                members = family.members.filter(is_join=True)

                for member in members:
                    wallet_logs = WalletLog.objects.filter(
                        user=member.user, created_at__gte=last_week, action='debit'
                    )

                    credit_sum = wallet_logs.aggregate(total=Sum('coins_amount'))['total'] or 0


                    member.contribution = credit_sum
                    member.save()

                    total_family_contribution += credit_sum

                family.contribution = total_family_contribution
                family.save()

            return Response({"message": "Weekly family and member contributions updated successfully!"}, status=200)

        except Exception as e:
            return Response({"error": str(e)}, status=500)



class WeeklyBonusDistributionAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny] 
    def post(self, request, *args, **kwargs):
        families = CreateFamily.objects.all()

        for family in families:
            # Calculate the total contribution for the family
            total_contribution = family.members.aggregate(total=Sum('contribution'))['total'] or 0

            # Find the current bonus level
            current_bonus_level = BonusLevel.objects.filter(target_contribution__lte=total_contribution).order_by('-level').first()
            print('current_bonus_level',current_bonus_level)
            # Skip if the bonus level is already up-to-date
            if current_bonus_level and family.bonus_level == current_bonus_level.level:
                continue  # Skip to the next family

            # Update the family's bonus level
            if current_bonus_level:
                family.bonus_level = current_bonus_level.level
                family.save()

                # Rank members based on their contributions
                members = family.members.order_by('-contribution')

                # Assign leader and top ranks
                leader = members.first()
                top_members = members[1:4]  # Top 1, Top 2, Top 3 (excluding the leader)

                # Update coins in the wallet and save logs for the leader
                if leader:
                    self.save_bonus(leader.user, current_bonus_level.leader_coins, "Leader Bonus")

                # Update coins for Top1, Top2, and Top3
                for idx, member in enumerate(top_members):
                    coins = [current_bonus_level.top1_coins, current_bonus_level.top2_coins, current_bonus_level.top3_coins]
                    if idx < len(coins):  # Ensure index is within range
                        bonus_type = f"Top {idx + 1} Bonus"
                        self.save_bonus(member.user, coins[idx], bonus_type)

        return Response({"message": "Weekly bonus distribution completed successfully!"}, status=status.HTTP_200_OK)

    def save_bonus(self, user, coins, bonus_type):
        """
        Save coins to Wallet and log to WalletLog for a specific user.
        """
        # Update Wallet
        wallet, created = Wallet.objects.get_or_create(user=user)
        wallet.gold_coins += coins
        wallet.save()

        # Save Log
        WalletLog.objects.create(
            user=user,
            coins_amount=coins,
            action="credit",
            wallet_description=bonus_type
        )



class WeeklyFamilyRankingAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny] 
    def get(self, request, *args, **kwargs):
        # Get the start and end of the current week (from last Sunday to today)
        today = datetime.today()
        start_of_week = today - timedelta(days=today.weekday())  # Monday of the current week
        end_of_week = start_of_week + timedelta(days=7)  # Sunday of the current week

        # Filter families based on the current week's contribution
        families = CreateFamily.objects.annotate(
            total_contribution=Sum('members__contribution')
        ).filter(
            created_at__gte=start_of_week, created_at__lte=end_of_week
        ).order_by('-total_contribution')  # Sorting by total contribution in descending order

        # Prepare the data to return
        family_data = []
        for family in families:
            family_data.append({
                'family_name': family.name,
                'total_contribution': family.total_contribution,
                'created_at': family.created_at,
            })

        return Response(family_data, status=status.HTTP_200_OK)



class LastWeekFamilyRankingAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny] 
    def get(self, request, *args, **kwargs):
        # Get the start and end of the last week (from last Monday to last Sunday)
        today = datetime.today()
        start_of_last_week = today - timedelta(days=today.weekday() + 7)  # Last Monday
        end_of_last_week = start_of_last_week + timedelta(days=7)  # Last Sunday

        # Filter families based on the last week's contribution
        families = CreateFamily.objects.annotate(
            total_contribution=Sum('members__contribution')
        ).filter(
            created_at__gte=start_of_last_week, created_at__lte=end_of_last_week
        ).order_by('-total_contribution')  # Sorting by total contribution in descending order

        # Prepare the data to return
        family_data = []
        for family in families:
            family_data.append({
                'family_name': family.name,
                'total_contribution': family.total_contribution,
                'created_at': family.created_at,
            })

        return Response(family_data, status=status.HTTP_200_OK)