pip install pyautogui
pip install keyboard
pip install mss
pyinstaller --onefile --hidden-import=cv2 main.py 
pyinstaller --onefile --hidden-import=cv2 banker2.py
pyinstaller --onefile --hidden-import=cv2 banker3.py
pyinstaller --onefile --hidden-import=cv2 newBanker.py
pyinstaller --onefile --hidden-import=cv2 newBankerVer2.py

- 매크로 기능정의서
1. 기본 규칙
  1.1 배팅 뱅커, 플레이어 선택은 나온횟수가 적은곳을 선택
  1.2 승리, 패배 카운터가 동률이 될떄 배팅 관전
  1.3 누적수익 +1700원이상일시 
  1.4 3판휴식 후 4째판 관전후 다음판 다시작동
  1.4 플레이어승 2배, 뱅커승 1.95배
  1.5 슈 변경시(20초이상 미선택) 플뱅 선택 비율은 리셋(배팅한텀 쉼) , 배팅단계는 유지
2.실행순서
  2.1 첫판의 결과를 통해 다음판의 배팅을 결정한다.(결과의 반대로 배팅) 무승부시 다음판 대기
  2.2 승리시 
    2.2.1 1~10단계일시 -1단계로 배팅 (1,000원)
    2.2.2 11~50단계일시 1단계로 리셋 배팅
  2.3 패배시
    2.3.1 1~10단계일시 +1단계 후 배팅 (1,000원)
    2.3.2 11~50단계일시 +1단계 후 배팅 (10,000원 ~ 50,000원)
    2.3.3 계단식 베팅 단계 및 금액
    단계 범위	베팅 금액 (원)
       1~10	1,000
      11~20	10,000
      21~30	20,000
      31~40	30,000
      41~50	40,000
  2.4 무승부시
    2.4.1 배팅한 방식 그대로 다음판 진행