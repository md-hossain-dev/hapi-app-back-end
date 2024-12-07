from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from hapi_app.models import User,Country,UserLV
from .serializers import UserListSerializer,CountryListSerializer,UserLVListSerializer
from .forms import UserAuthForm 
from django.shortcuts import redirect, render
from django.contrib.auth.views import LoginView
from django.views.generic import View
from django.contrib.auth import login as do_login
from django.contrib.auth import logout as do_logout
from django.contrib import messages
from django.contrib.auth import authenticate
from .pagination import CustomPageNumberPagination
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet
from rest_framework import viewsets
from rest_framework import viewsets, status


class LoginPageView(LoginView):
    template_name = 'base/login.html'
    form_class = UserAuthForm

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.is_active:
                return redirect('/dashboard/') 
            return redirect('/')
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form = UserAuthForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                do_login(request, user)
                if not user.is_active:
                    messages.error(
                        request, 'Please confirm your email address to activate the account.')
                return redirect('/dashboard/')
            else:
                messages.error(request, 'Invalid Username / Password')
        return render(request, self.template_name, {'form': form, 'no_footer_header': True})



class LogoutView(View):
    def dispatch(self, request):
        try:
            if self.request.user.is_authenticated:
                do_logout(request)
                if not "next" in request.GET:
                    return redirect('/login')
                return redirect(request.GET['next'])
            else:
                return redirect('/login')
        except Exception as e:
            logger.info(str(e))
            return redirect('/login')


class AllUserViewList(APIView):
    # permission_classes = [AllowAny]
    pagination_class = CustomPageNumberPagination

    def get(self, request, *args, **kwargs):
        queryset = User.objects.filter(is_active=True).order_by('id')

        # 'q' parameter used to filter title, category, and subcategory
        query = request.query_params.get('q')
        if query:
            queryset = queryset.filter(
                Q(email__icontains=query) |
                Q(username__icontains=query) |
                Q(nick_name__icontains=query) |
                Q(gender__icontains=query) |
                Q(phone_number__icontains=query) |
                Q(level__level_name__icontains=query)
            )

        # Pagination settings
        paginator = self.pagination_class()
        page_size = int(request.query_params.get('size', 30))
        paginator.page_size = page_size
        paginated_queryset = paginator.paginate_queryset(queryset, request)

        if paginated_queryset:
            serializer = UserListSerializer(paginated_queryset, many=True)
            return paginator.get_paginated_response({
                "count_page": paginator.page.paginator.num_pages,
                "current_page": paginator.page.number,
                "size": paginator.page.paginator.per_page,
                "data": serializer.data
            })

        return Response({
            "count_page": 0,
            "current_page": 1,
            "size": page_size,
            "data": []
        }, status=status.HTTP_200_OK)




class UserUpdateAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def put(self, request, pk=None):
        # Fetch the user instance
        user_instance = User.objects.filter(pk=pk, is_active=True).first()

        if not user_instance:
            return Response(
                {"error": True, "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check for duplicate data
        email = request.data.get("email")
        if email and User.objects.filter(email=email).exclude(pk=pk).exists():
            return Response(
                {"error": "email already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        username = request.data.get("username")
        if username and User.objects.filter(username=username).exclude(pk=pk).exists():
            return Response(
                {"error": "username already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        phone_number = request.data.get("phone_number")
        if phone_number and User.objects.filter(phone_number=phone_number).exclude(pk=pk).exists():
            return Response(
                {"error": "phone_number already exists."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Update country
        country_id = request.data.get("country")
        if country_id:
            try:
                country_instance = get_object_or_404(Country, pk=country_id)
                user_instance.country = country_instance
            except:
                return Response(
                    {"error": True, "message": f"Invalid country ID: {country_id}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Update level
        level_id = request.data.get("level")
        if level_id:
            try:
                level_instance = get_object_or_404(UserLV, pk=level_id)
                user_instance.level = level_instance
            except:
                return Response(
                    {"error": True, "message": f"Invalid level ID: {level_id}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Handle profile image upload
        profile = request.FILES.get("profile")
        if profile:
            user_instance.profile = profile

        # Update other fields
        update_data = {
            "email": request.data.get("email", user_instance.email),
            "username": request.data.get("username", user_instance.username),
            "first_name": request.data.get("first_name", user_instance.first_name),
            "last_name": request.data.get("last_name", user_instance.last_name),
            "bio": request.data.get("bio", user_instance.bio),
            "nick_name": request.data.get("nick_name", user_instance.nick_name),
            "gender": request.data.get("gender", user_instance.gender),
            "birth_day": request.data.get("birth_day", user_instance.birth_day),
            "phone_number": request.data.get("phone_number", user_instance.phone_number),
            "is_active": request.data.get("is_active", user_instance.is_active),
            "is_svip": request.data.get("is_svip", user_instance.is_svip),
        }

        for field, value in update_data.items():
            setattr(user_instance, field, value)

        user_instance.save()

        # Serialize and return the response
        serializer = UserListSerializer(user_instance)
        response_data = {
            "error": False,
            "message": "User updated successfully",
            "data": serializer.data
        }
        return Response(response_data, status=status.HTTP_200_OK)



class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated]
    # permission_classes = [AllowAny]

    def delete(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.is_active = False
            user.save()

            return Response({"message": "User deleted successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)



class UserDetailView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]

    def get(self, request, pk):
        # Get the user instance or raise a 404 if not found
        user_instance = get_object_or_404(User, id=pk, is_active=True)
        user_data = UserListSerializer(user_instance).data
        
        response_data = {
            "user": user_data,
        }
        return Response(response_data, status=status.HTTP_200_OK)


class CountryListView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    def get(self, request):
        country = Country.objects.all()
        serializer = CountryListSerializer(country, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




class UserLVListView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny]
    def get(self, request):
        level = UserLV.objects.all()
        serializer = UserLVListSerializer(level, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)




















