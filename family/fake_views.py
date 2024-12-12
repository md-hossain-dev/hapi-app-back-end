from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from faker import Faker
import random
from hapi_app.models import User, Country, UserLV  
from family.models import CreateFamily, FamilyMember,BonusLevel
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import AllowAny
fake = Faker()

class GenerateFakeDataView(APIView):
    # permission_classes = [IsAuthenticated]
    permission_classes = [AllowAny] 
    """
    API to generate and update fake data for User, CreateFamily, and FamilyMember models.
    """
    def post(self, request, *args, **kwargs):
        try:
            # Create Countries and User Levels if not exist
            # countries = [Country.objects.get_or_create(name=f"Country {i}")[0] for i in range(1, 6)]
            # levels = [UserLV.objects.get_or_create(level_name=f"Level {i}", level_rank=i)[0] for i in range(1, 6)]

            # Create 100 fake users
            users = []
            for _ in range(100):
                user = User.objects.create(
                    email=fake.unique.email(),
                    username=fake.user_name(),
                    profile=fake.file_path(depth=1, category='image'),
                    cover_photo=fake.file_path(depth=1, category='image'),
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    bio=fake.text(max_nb_chars=200),
                    nick_name=fake.first_name(),
                    fcm_token=fake.uuid4(),
                    gender=random.choice(['male', 'female']),
                    birth_day=fake.date_of_birth(),
                    phone_number=fake.phone_number(),
                    is_active=True,
                    is_svip=random.choice([True, False]),
                    country=Country.objects.get(id=1), 
                    level=UserLV.objects.get(id=1)
                )
                users.append(user)

            # Create 10 fake families
            families = []
            for _ in range(10):
                family = CreateFamily.objects.create(
                    name=fake.unique.company(),
                    family_image=fake.file_path(depth=1, category='image'),
                    family_notification=fake.sentence(),
                    join_mode=random.choice(["Leader/Co-Leader Review", "Join Freely"]),
                    created_by=random.choice(users),
                    contribution=fake.random_number(digits=6),
                    bonus_level=fake.random_int(min=1, max=10),
                    level=UserLV.objects.get(id=1)
                )
                families.append(family)

            # Create family members
            for user in users:
                family = random.choice(families)
                FamilyMember.objects.create(
                    user=user,
                    family=family,
                    coins_contributed=fake.random_int(min=0, max=1000),
                    is_join=True,
                    contribution=fake.random_number(digits=5),
                    is_leader=random.choice([True, False]),
                    reward=fake.random_number(digits=6),
                )

            return Response(
                {"message": "Fake data generated successfully!"},
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )




class CreateFakeBonusLevelAPIView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request, *args, **kwargs):
        fake = Faker()
        fake_data = []
        existing_levels = set(BonusLevel.objects.values_list('level', flat=True))  


        for i in range(1, 101):  
            if i in existing_levels:  
                continue
            
            bonus_level = BonusLevel(
                level=i,
                target_contribution=fake.random_int(min=1000, max=100000),
                leader_coins=fake.random_int(min=50, max=500),
                top1_coins=fake.random_int(min=40, max=300),
                top2_coins=fake.random_int(min=30, max=200),
                top3_coins=fake.random_int(min=20, max=100),
            )
            fake_data.append(bonus_level)

        if fake_data:
            BonusLevel.objects.bulk_create(fake_data)
            return Response({"message": f"{len(fake_data)} fake BonusLevel records created successfully!"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "No new records were created. Levels already exist!"}, status=status.HTTP_200_OK)