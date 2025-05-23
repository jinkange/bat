try:
    import cv2
    import pyautogui
    import numpy as np
    import time
    import os
    import keyboard
    import threading
    import mss

except Exception as e:
    print(e)
    input('11')
    
running = False
stopped = False
# 키 입력 감지 스레드
def keyboard_listener():
    global running, stopped
    while True:
        if keyboard.is_pressed('1'):
            running = True
            stopped = False
            print("✅ 매크로 시작됨")
            time.sleep(0.5)
        elif keyboard.is_pressed('2'):
            running = False
            stopped = True
            print("⛔ 매크로 정지됨")
            time.sleep(0.5)
listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
listener_thread.start()


def capture_all_monitors():
    with mss.mss() as sct:
        # 전체 모니터 영역
        monitor = sct.monitors[0]  # [0]은 모든 모니터를 포함한 가상 화면
        screenshot = np.array(sct.grab(monitor))
        return screenshot[:, :, :3]  # BGR 이미지 반환
        

def find_image_on_all_monitors(template_path, threshold=0.97):
    screenshot = capture_all_monitors()
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    if template is None:
        raise ValueError(f"Template image not found at {template_path}")

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    
    for pt in zip(*loc[::-1]):
        return pt  # 첫 번째 매칭 위치 반환

    return None

def find_image_with_orb(template_path, screenshot_img, match_threshold=9):
    # 이미지 읽기
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
    screenshot_gray = cv2.cvtColor(screenshot_img, cv2.COLOR_BGR2GRAY)

    # ORB 객체 생성
    orb = cv2.ORB_create(nfeatures=500)

    # 특징점 및 디스크립터 추출
    kp1, des1 = orb.detectAndCompute(template, None)
    kp2, des2 = orb.detectAndCompute(screenshot_gray, None)

    if des1 is None or des2 is None:
        return None  # 매칭 불가

    # Brute Force 매칭기
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)

    # 매칭
    matches = bf.match(des1, des2)
    matches = sorted(matches, key=lambda x: x.distance)
    print(len(matches))
    if len(matches) >= match_threshold:
        # 좋은 매칭이 충분할 경우: 첫 번째 매칭 포인트의 위치 사용
        match = matches[0]
        pt = kp2[match.trainIdx].pt
        return int(pt[0]), int(pt[1])
    else:
        return None
    
def screenshot_all_monitors():
    with mss.mss() as sct:
        monitor = sct.monitors[0]  # [0]은 모든 모니터 포함
        sct_img = sct.grab(monitor)
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

# 이미지 매칭 함수
def find_image_on_screen(template_path, threshold=0.9):
    screenshot = screenshot_all_monitors()
    # cv2.imwrite("full_screenshot.png", screenshot)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)
    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    loc = np.where(result >= threshold)
    for pt in zip(*loc[::-1]):
        return pt  # 위치 반환
    return None

# 클릭 함수
def click_at(pos):
    if pos:
        pyautogui.click(pos)
        time.sleep(0.5)

# 이미지 경로들
img_path = "./images/"
images = {
    "place_bet": os.path.join(img_path, "place_bet2.png"),
    "bet_closed": os.path.join(img_path, "bet_closed2.png"),
    "bet_closed2": os.path.join(img_path, "bet_closed3.png"),
    "banker_win": os.path.join(img_path, "banker_win2.png"),
    "player_win": os.path.join(img_path, "player_win2.png"),
    "reissued": os.path.join(img_path, "reissued.png"),
    "tie": os.path.join(img_path, "tie.png")
}

# 좌표 예시 (실제 화면에 맞게 조정 필요)
BANKER_POS = (1144, 806)
PLAYER_POS = (794, 840)
AMOUNT_POS = {
    1000: (824, 982),
    2000: (874, 982),
    5000: (937, 982),
    25000: (984, 982),
    100000: (1047, 982),
    500000: (1093, 982),
}



# 금액 계산 함수
def get_bet_amount(stage):
    if 1 <= stage <= 10:
        return 1000
    elif 11 <= stage <= 20:
        return 10000
    elif 21 <= stage <= 30:
        return 20000
    elif 31 <= stage <= 40:
        return 30000
    elif 41 <= stage <= 50:
        return 40000
    else:
        return 0

# 매크로 루프

restart = False
waitingCount = 0
isWaiting = True
totalBat = 0
batSize = 0
bet_target = ''
stage = 1
total_profit = 0
banker_win_count = 0
player_win_count = 0
amount = 0

def init():
    global waitingCount
    global isWaiting
    global totalBat
    global batSize
    global bet_target
    global stage
    global total_profit
    global banker_win_count
    global player_win_count
    global amount
    
    waitingCount = 0
    isWaiting = True
    totalBat = 0
    batSize = 0
    bet_target = ''
    stage = 1
    total_profit = 0
    banker_win_count = 0
    player_win_count = 0
    amount = 0
    
print("▶ 1번을 누르면 시작, 2번을 누르면 정지")

while True:
    if not running:
        time.sleep(1)
        continue

    # 매크로 루프 시작
    while running:
        #목표치 확인
        if total_profit >= 1700:
            print("💰 수익 목표 도달, 데이터 초기화, 3판 대기후 재시작")
            time.sleep(1)
            init()
            restart = True
            continue
        
        if(isWaiting):
            print("💹 관전 대기판...")
            
        #배팅 대기중에서 항상 걸림
        while (not (find_image_on_all_monitors(images["bet_closed"]) or find_image_on_all_monitors(images["bet_closed2"]))):
            False
        
        if(restart):
            waitingCount += 1
            isWaiting = True
            if(waitingCount > 3): 
                restart = False
                break
            print(f"💹 3판중 {waitingCount}판 대기중...")
            
        result = None
        while not result:
            if find_image_on_screen(images["banker_win"]):
                result = "BANKER"
                batSize = 1.95
                if(not restart): banker_win_count += 1
                if(player_win_count == banker_win_count): isWaiting= True
                else: isWaiting= False
                time.sleep(1)
            elif find_image_on_screen(images["player_win"]):
                result = "PLAYER"
                batSize = 2
                if(not restart): player_win_count += 1
                if(player_win_count == banker_win_count): isWaiting= True
                else: isWaiting= False
                time.sleep(1)
            elif find_image_on_screen(images["tie"]):
                result = "TIE"
                isWaiting = True
                batSize = 1
                time.sleep(1)
        
        if(not restart): 
            print(f"🏆 결과: {result} 비율 PLAYER {player_win_count} : BANKER {banker_win_count}")
        
        if result == "TIE":
            print("💹 무승부 → 다음 판 대기")
            continue
        
        if(result == bet_target and bet_target != ''):
            if(stage <= 1): stage = 1
            elif(stage >= 10): stage = 1
            else: stage -= 1
            total_profit = total_profit + (amount * batSize) - amount
            print(f"💹 배팅성공 누적 수익: {total_profit}원")
        elif(result != bet_target and bet_target != '' and result !="TIE"):
            stage += 1
            total_profit = total_profit - amount
            print(f"💹 배팅실패 누적 수익: {total_profit}원")
                
        while not find_image_on_screen(images["place_bet"]):
            False
        time.sleep(2)
        pos = find_image_on_all_monitors('./images/reissued.png')
        if pos:
            print("💹 슈 교체 한턴 쉬기 및 카운팅 초기화")
            banker_win_count = 0
            player_win_count = 0
            bet_target = ''
            isWaiting = True
            continue
        if(isWaiting):
            bet_target = ''
            continue
        amount = get_bet_amount(stage)
        if(amount == 1000): click_at(AMOUNT_POS[amount])
        if(amount == 10000): 
            click_at(AMOUNT_POS[5000]) 
        if(amount == 20000): 
            click_at(AMOUNT_POS[5000])
        if(amount == 30000): 
            click_at(AMOUNT_POS[5000])
        if(amount == 40000): 
            click_at(AMOUNT_POS[5000])
        
        if(banker_win_count > player_win_count):
            if(amount == 1000): click_at(PLAYER_POS)
            if(amount == 10000): 
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
            if(amount == 20000): 
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
            if(amount == 30000): 
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
            if(amount == 40000): 
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
            print("🎯PLAYER 배팅 클릭")
            bet_target = "PLAYER"
        elif(banker_win_count < player_win_count):
            if(amount == 1000): click_at(BANKER_POS)
            if(amount == 10000): 
                click_at(BANKER_POS)
                click_at(BANKER_POS)
            if(amount == 20000): 
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
            if(amount == 30000): 
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
            if(amount == 40000): 
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
            print("🎯BANKER 배팅 클릭")
            bet_target = "BANKER"
        totalBat += 1
        print(f"🎯 배팅: {bet_target}, 금액: {amount}원, 단계: {stage}단계, 총 배팅: {totalBat}회")

    if stopped:
        break

    # 적절한 sleep 필수
    time.sleep(1)
