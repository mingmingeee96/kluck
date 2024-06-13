import firebase_admin # Firebase Admin SDK 사용
from firebase_admin import credentials # 서비스 계정 키를 사용하여 Firebase Admin SDK 인증
from firebase_admin import messaging # FCM 메시지 생성 및 전송
from datetime import datetime
from kluck_env import env_settings as env
from .models import DeviceToken
from luck_messages.models import LuckMessage

# firebase adminsdk 초기화
cred_path = 'kluck-firebase.json'
cred = credentials.Certificate(cred_path)
firebase_admin.initialize_app(cred)
print("Firebase Admin SDK 초기화 완료")

# push 보내는 함수
def send_push_notification():
    # 특정 앱에 해당하는 디바이스 토큰 가져오기
    registration_tokens = list(DeviceToken.objects.filter(app_name='오늘의 운세').values_list('token', flat=True))

    # firebase에 등록된 디바이스 토큰 가져오기
    registration_tokens = env.FCM_TOKEN
    print(f"등록된 토큰 수: {len(registration_tokens)}")

    # 오늘 날짜 가져오기
    today = datetime.now().strftime("%Y%m%d")
    # DB에서 오늘의 운세 메시지 가져오기
    today_luck_msg = LuckMessage.objects.filter(luck_date=today, category='today').first()

    # 오늘의 운세 메시지가 존재한다면 푸시 알림 보내기
    if today_luck_msg:
        title = '오늘의 운세'
        body = today_luck_msg.luck_msg

    # 여러 기기에 메시지 전송
    message = messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        android=messaging.AndroidConfig(
            ttl=datetime.timedelta(seconds=3600),
            priority='normal',
            notification=messaging.AndroidNotification(
                icon='https://exodus-web.gcdn.ntruss.com/static/appicon_512_512.png'
            )
        ),
        tokens = registration_tokens, # 여러 개의 등록 토큰 리스트
    )
    print("푸시 알림 메시지 생성 완료")

    # Firebase로 푸시 알림 전송
    response = messaging.send_multicast(message)
    print('{0} messages were sent successfully'.format(response.success_count))
