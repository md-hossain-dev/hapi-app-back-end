from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import RechargeCoin, ExchangeDiamondToCoin
from .serializers import RechargeCoinSerializer, ExchangeDiamondToCoinSerializer,CoinPurchaseRequestSerializer
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from hapi_app.models import User,Wallet,WalletLog
from walletusers.models import CoinPurchaseRequest

from hapi_app.utils import send_firebase_notification
from google.auth.transport.requests import Request

from hapi_app.models import Notification

class RechargeCoinAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        coins = RechargeCoin.objects.all()
        serializer = RechargeCoinSerializer(coins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateRechargeCoinAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = RechargeCoinSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ExchangeDiamondToCoinAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        exchanges = ExchangeDiamondToCoin.objects.all()
        serializer = ExchangeDiamondToCoinSerializer(exchanges, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CreateExchangeDiamondToCoinAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = ExchangeDiamondToCoinSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class CoinPurchaseRequestCreateView(APIView):
    permission_classes = [AllowAny]
    # permission_classes = [IsAuthenticated]  

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.data.get('user_id')
            if not user_id:
                return Response(
                    {"error": "User ID is required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return Response(
                    {"error": "User not found."},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = CoinPurchaseRequestSerializer(data=request.data)
            if serializer.is_valid():
                recharge_coin = RechargeCoin.objects.get(id=request.data['recharge_coin'])
                purchase_request = CoinPurchaseRequest.objects.create(
                    user=user,
                    recharge_coin=recharge_coin
                )
                return Response(
                    {
                        "message": "Purchase request created successfully!",
                        "data": CoinPurchaseRequestSerializer(purchase_request).data
                    },
                    status=status.HTTP_201_CREATED
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except RechargeCoin.DoesNotExist:
            return Response(
                {"error": "Recharge coin package not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class CoinPurchaseRequestUpdateView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            request_id = request.data.get("request_id")
            action = request.data.get("action")

            if not request_id or action not in ["accepted", "rejected"]:
                return Response(
                    {"error": "Request ID and valid action (accepted/rejected) are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            try:
                purchase_request = CoinPurchaseRequest.objects.get(id=request_id, status="pending")
            except CoinPurchaseRequest.DoesNotExist:
                return Response(
                    {"error": "Purchase request not found or already processed."},
                    status=status.HTTP_404_NOT_FOUND
                )

            if action == "accepted":
                # Update wallet with the total coins
                user_wallet, created = Wallet.objects.get_or_create(user=purchase_request.user)
                total_coins = purchase_request.recharge_coin.total_coins
                user_wallet.gold_coins += total_coins
                user_wallet.save()
                # Send notification if the user has an FCM token
                if purchase_request.user.fcm_token:
                    title = "Congratulations!"
                    body = f"{purchase_request.user.username}, you purchased {purchase_request.recharge_coin.total_coins} gold coins."
                    notification_response = send_firebase_notification(purchase_request.user.fcm_token, title, body)
                    print("Firebase Response:", notification_response)

                    # Save the notification in the database
                    Notification.objects.create(
                        user=purchase_request.user,
                        title=title,
                        message=body,
                        is_sent=True  # Indicating the notification was sent successfully
                    )

                # Log the wallet action (debit for coin purchase)
                WalletLog.objects.create(
                    user=purchase_request.user,
                    action='debit',
                    coins_amount=total_coins,
                    wallet_description=f"Buy Coin by {purchase_request.user.username}."
                )

                # Update request status to accepted
                purchase_request.status = "accepted"
                purchase_request.save()

                

                return Response(
                    {"message": "Purchase request accepted and coins added to user's wallet."},
                    status=status.HTTP_200_OK
                )

            elif action == "rejected":
                # Update the request status to rejected
                purchase_request.status = "rejected"
                purchase_request.save()

                # Send rejection notification if the user has an FCM token
                if purchase_request.user.fcm_token:
                    title = "Sorry!"
                    body = f"{purchase_request.user.username}, your coin purchase request has been rejected."
                    notification_response = send_firebase_notification(purchase_request.user.fcm_token, title, body)
                    print("Firebase Response:", notification_response)

                    # Save the notification in the database
                    Notification.objects.create(
                        user=purchase_request.user,
                        title=title,
                        message=body,
                        is_sent=True  # Indicating the notification was sent successfully
                    )

                return Response(
                    {"message": "Purchase request rejected."},
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
