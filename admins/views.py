from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ParseError
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from .serializers import *
from drf_spectacular.utils import extend_schema, OpenApiExample

# from django.contrib.auth import authenticate, login, logout
# from .forms import LoginForm


# api/v1/admin/login/
class AdminLogin(APIView):
    serializer_class = AdminLoginSerializer

    # POST 메소드에 대한 스키마 정의 및 예시 포함
    @extend_schema(tags=['Admin'],
        examples=[
            OpenApiExample(
                'Example',
                value={'username': 'admin1', 'password': 'sodlfmadmsrhksflwk1'},
                request_only=True,  # 요청 본문에서만 예시 사용
            )
        ],
        description="BE-ADM001: 프론트에서 username(ID), password(패스워드)를 받아 로그인\n관리자 로그인 후 최종 접속 날짜(last_date)를 오늘 날짜로 업데이트"
    )

    # def post(self, request):
    #     form = LoginForm(request.POST)
    #     if form.is_valid():
    #         username = form.cleaned_data.get('username')
    #         password = form.cleaned_data.get('password')
    #         user = authenticate(request, username=username, password=password)
    #         try:
    #             if user is not None:
    #                 login(request, user)
    #                 return Response({'message': '로그인 성공'}, status=status.HTTP_200_OK)
    #             else:
    #                 return Response({'message': '정보가 없습니다.'}, status=status.HTTP_401_UNAUTHORIZED)
    #         except kluck_Admin.DoesNotExist:
    #             return Response({'message': '존재하지 않는 관리자 ID입니다.'}, status=status.HTTP_404_NOT_FOUND)
    #     else:
    #         return Response({'message': 'form 정보에 오류가 있습니다.'}, status=status.HTTP_200_OK)






    def post(self, request):
        admin_id = request.data.get('username')
        admin_pw = request.data.get('password')

        try:
            admin = kluck_Admin.objects.get(admin_id=admin_id)
            if check_password(admin_pw, admin.password):
                # 비밀번호 확인 후 로그인 처리
                admin.last_date = timezone.now()
                admin.save()
                return Response({'message': '로그인 성공'}, status=status.HTTP_200_OK)
            else:
                return Response({'message': '비밀번호가 일치하지 않습니다.'}, status=status.HTTP_401_UNAUTHORIZED)
        except kluck_Admin.DoesNotExist:
            return Response({'message': '존재하지 않는 관리자 ID입니다.'}, status=status.HTTP_404_NOT_FOUND)


# api/vi/admin/
class AdminUsers(APIView):
    '''
    BE-ADM003: 프론트에서 admins_id(PK), email, admin_user(사용자명), cell_num(폰 번호), create_date(등록일)를 로드
    '''
    serializer_class = AdminSerializer
    @extend_schema(tags=['Admin'])
    def get(self, request):
        admins = kluck_Admin.objects.all()
        serializer = AdminSerializer(admins, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# api/v1/admin/signup/   사용 안할수도.
class AdminUsersSignup(APIView):
    serializer_class = AdminSignupSerializer
    @extend_schema(tags=['Admin'],
        examples=[
            OpenApiExample(
                'Example',
                value={"username": "admin99",
                        "cell_num": "01000000000",
                        "email": "admin99@admin99.com",
                        "password": "sodlfmadmsrhksflwk99"
                },
                request_only=True,  # 요청 본문에서만 예시 사용
            )
        ],
        description="BE-ADM002(화면없음): 프론트에서 admin_id(ID), admin_user(사용자명), cell_num(폰 번호), email, user_pw(패스워드)를 받아 관리자 등록\n수정 내용을 따로 다시 반환 하지는 않는다."
    )
    def post(self, request):

        password = request.data.get('password')
        serializer = AdminSignupSerializer(data=request.data)

        # try:
        #     validate_password(password)
        # except:
        #     raise ParseError('Password is invalid.')

        if serializer.is_valid():
            user = serializer.save()
            user.password = make_password(password)
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise ParseError(serializer.errors)


# api/v1/admin/msg/
class EditLuckMessage(APIView):
    serializer_class = LuckMessageSerializer
    @extend_schema(tags=['AdminMsg'],
        examples=[
            OpenApiExample(
                'Example',
                value={"msg_id": "2694",
                        "luck_msg": "오늘은 아이유 좋은날 들어요. 오늘은 좋은날이니까"
                },
                request_only=True,  # 요청 본문에서만 예시 사용
            )
        ],
        description="BE-GPT105(205, 305, 405): 프론트에서 msg_id를 받아 luck_messages의 모델에서 해당 id를 찾아 내용 수정\n수정 내용을 따로 다시 반환하지는 않는다."
    )
    def post(self, request):
        msg_id = request.data.get('msg_id')
        try:
            msg_id = LuckMessage.objects.get(msg_id=msg_id)
        except LuckMessage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = LuckMessageSerializer(msg_id, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

