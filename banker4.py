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
            global hole_total_profit
            running = False
            stopped = True
            print("⛔ 매크로 정지됨")
            hole_total_profit= 0
            init()
            time.sleep(0.5)
listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
listener_thread.start()

    
def screenshot_all_monitors():
    with mss.mss() as sct:
        monitor = sct.monitors[0]  # [0]은 모든 모니터 포함
        sct_img = sct.grab(monitor)
        img = np.array(sct_img)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        return img

    
# # 이미지 매칭 함수
def find_image_on_screen(template_path, threshold=0.99):
# 1. 전체 스크린샷 캡처
    screenshot = pyautogui.screenshot()
    screenshot_np = np.array(screenshot)
    screenshot_cv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)

    # 2. 템플릿 이미지 불러오기
    template = cv2.imread(template_path)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    w, h = template_gray.shape[::-1]

    # 3. 스크린샷을 회색으로 변환
    screen_gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)

    # 4. 템플릿 매칭 수행
    res = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    threshold = 0.99
    loc = np.where(res >= threshold)
    # 5. 결과 판별
    found = False
    for pt in zip(*loc[::-1]):
        found = True
        break

    # 6. 결과 출력
    if found:
        return True
    else:
        return False


region = (708, 574, 573, 57)

# 특정 영역에서 이미지가 있는지 판단하는 함수
def is_image_in_region(template_path, region, threshold=0.95):
    """
    template_path: 찾을 이미지 파일 경로
    region: (x, y, width, height)1281 631
    threshold: 일치 정도 (0.0 ~ 1.0)
    """
    screenshot = pyautogui.screenshot(region=region)
    # screenshot = screenshot_all_monitors()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    max_val = np.max(result)
    return max_val >= threshold

# 클릭 함수
def click_at(pos):
    if pos:
        time.sleep(0.1)
        pyautogui.click(pos)

# 이미지 경로들
img_path = "./images/"
images = {
    "place_bet": os.path.join(img_path, "place_bet2.png"),
    "bet_closed": os.path.join(img_path, "bet_closed2.png"),
    "bet_closed2": os.path.join(img_path, "bet_closed3.png"),
    "banker_win": os.path.join(img_path, "banker_win2.png"),
    "player_win": os.path.join(img_path, "player_win2.png"),
    "reissued": os.path.join(img_path, "reissued.png"),
    "tie": os.path.join(img_path, "tie2.png")
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
    if 1 <= stage <= 14:
        return 1000
    elif 15 <= stage <= 25:
        return 14000
    elif 26 <= stage <= 35:
        return 80000
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
hole_total_profit = 0
banker_win_count = 0
player_win_count = 0
amount = 0
last_restart = ''
last_restart_bat_size = 0
isRestart = False
isSueRestart = False
isPass = False
isSueRestartChange = False
isSuePass = False
isSueChange = False
totalWinCount = 0
def init():
    global waitingCount
    global isWaiting
    global totalBat
    global batSize
    global isRestart
    global isSueRestart
    
    global bet_target
    global stage
    global total_profit
    global banker_win_count
    global player_win_count
    global amount
    global totalWinCount
    isRestart = False
    waitingCount = 0
    isWaiting = True
    isSueRestart =False
    totalBat = 0
    batSize = 0
    bet_target = ''
    stage = 1
    total_profit = 0
    banker_win_count = 0
    player_win_count = 0
    totalWinCount = 0
    amount = 0
    
TURN_FINISH_PRICE = 1200
GAME_FINISH_PRICE = 2300
# print("✅ 신규 4번째 버전 1.4만원, 8만원 배팅 (1000원 TEST) ver1.0.0")    
print("✅ 신규 4번째 버전 1.4만원, 8만원 배팅 ver1.0.0")    
print("▶ 1번을 누르면 시작, 2번을 누르면 정지")

while True:
    if not running:
        time.sleep(1)
        continue

    # 매크로 루프 시작
    while running:
        #목표치 확인
        
        if total_profit >= TURN_FINISH_PRICE:
            print("💰 수익 목표 도달, 데이터 초기화, 2판 대기후 재시작")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            time.sleep(1)
            init()
            restart = True
            isWaiting = True
            continue
        
        if hole_total_profit >= GAME_FINISH_PRICE:
            print("💰 누적 목표 수익 도달, 매크로 정지")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            time.sleep(1)
            running = False
            stopped = True
            print("⛔ 매크로 정지됨")
            hole_total_profit= 0
            init()
            time.sleep(0.5)
            continue
        
        if stage >= 36:
            print("💰 손절 스테이지 도달, 매크로 정지")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            time.sleep(1)
            running = False
            stopped = True
            print("⛔ 매크로 정지됨")
            hole_total_profit= 0
            init()
            time.sleep(0.5)
            continue
        

        if(isWaiting):
            print("💹 관전 대기판...")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        
        pos = find_image_on_screen('./images/stop.png')
        if pos:
            running = False
            stopped = True
            print("⛔ 게임 팅김 매크로 정지됨")
            init()
            time.sleep(0.5)
            break
            
        while True:
            if stopped:
                break
            if is_image_in_region(images["bet_closed"], region):
                break
            elif is_image_in_region(images["bet_closed2"], region):
                break
            
        if(restart):
            waitingCount += 1
            isWaiting = True
            if(waitingCount > 2):
                restart = False
                isRestart = True
                isSueRestartChange = True
                break
            print(f"💹 2판중 {waitingCount}판 대기중...")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            
        
        if(not restart):
            if(not isSueRestartChange):
                if(not isSueChange):
                    pos = find_image_on_screen('./images/reissued.png')
                    if pos:
                        print("💹 슈 교체 한턴 쉬기 및 카운팅 초기화")
                        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                        banker_win_count = 0
                        player_win_count = 0
                        bet_target = ''
                        isWaiting= True
                else:
                    isSueChange = False
            else:
                isSueRestartChange = False
            
        result = None
        while not result:
            if stopped:
                break
            if is_image_in_region(images["banker_win"],region):
                result = "BANKER"
                last_restart = "PLAYER"
                batSize = 1.95
                last_restart_bat_size=2
                isRestart = False
                isPass = False
                if(not restart): banker_win_count += 1
                if(player_win_count == banker_win_count): isWaiting= True
                else: isWaiting= False
            elif is_image_in_region(images["player_win"],region):
                result = "PLAYER"
                last_restart = "BANKER"
                batSize = 2
                last_restart_bat_size = 1.95
                isRestart = False
                isPass = False
                if(not restart): player_win_count += 1
                if(player_win_count == banker_win_count): isWaiting= True
                else: isWaiting= False
            elif is_image_in_region(images["tie"],region):
                if(isRestart):
                    print("💹 2판 대기중 무승부 → 직전판 반대 ")
                    isRestart = False
                    result = last_restart
                    batSize = last_restart_bat_size
                    isWaiting= False
                else:
                    result = "TIE"
                    batSize = 1
                    print("💹 무승부 → 다음판으로")
                    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                    isPass = True
                    break
                
        if(isPass and isWaiting):
            isPass = False
            continue
        
        if(result == bet_target and bet_target != '' and result != "TIE"):
            if(stage > 25): totalWinCount +=1
            if(stage <= 1): stage = 1
            elif(stage == 15): stage = 1
            else: stage -= 1
            total_profit = total_profit + (amount * batSize) - amount
            hole_total_profit =  hole_total_profit + (amount * batSize) - amount
            if(not (restart)): print(f"🏆 결과: {result} 비율 PLAYER {player_win_count} : BANKER {banker_win_count} (승리)")
            print(f"💹 누적 수익: {total_profit}원 / 총 수익: {hole_total_profit}원")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            if(totalWinCount >= 2):
                print("💹 8만원판 2판 승리 데이터 초기화, 2판 대기후 재시작")
                print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                time.sleep(1)
                init()
                restart = True
                isWaiting = True
                continue
            if(total_profit >= TURN_FINISH_PRICE): continue
            if(hole_total_profit >= GAME_FINISH_PRICE): continue
        elif(result != bet_target and bet_target != '' and result !="TIE"):
            if(stage == 25): stage = 27
            else: 
                stage += 1
                if(stage > 25): totalWinCount -=1
            total_profit = total_profit - amount
            hole_total_profit =  hole_total_profit - amount
            if(not (restart)): print(f"🏆 결과: {result} 비율 PLAYER {player_win_count} : BANKER {banker_win_count} (패배)")
            print(f"💹 누적 수익: {total_profit}원 / 총 수익: {hole_total_profit}원")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        else:
            if(not (restart)): print(f"🏆 결과: {result} 비율 PLAYER {player_win_count} : BANKER {banker_win_count} (관전)")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                
        while not is_image_in_region(images["place_bet"], region):
            if stopped:
                break
        if stopped:
            break
        time.sleep(1)
        

        
        pos = find_image_on_screen('./images/reissued.png')
        if(not restart):
            if(not isSueRestartChange):
                if pos:
                    print("💹 슈 교체 한턴 쉬기 및 카운팅 초기화")
                    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                    banker_win_count = 0
                    player_win_count = 0
                    bet_target = ''
                    isWaiting = True
                    isSueChange = True
                    continue
            else:
                isSueRestartChange = False
        if(isWaiting):
            bet_target = ''
            continue

        amount = get_bet_amount(stage)
        
        # ##1000원 고정 테스트
        # if(amount == 1000): click_at(AMOUNT_POS[amount])
        # if(amount == 14000): 
        #     click_at(AMOUNT_POS[1000])
        # if(amount == 80000): 
        #     click_at(AMOUNT_POS[1000])
            
        # if(banker_win_count > player_win_count):
        #     if(amount == 1000): click_at(PLAYER_POS)
        #     if(amount == 14000): 
        #         click_at(PLAYER_POS)
        #     if(amount == 80000): 
        #         click_at(PLAYER_POS)
        #     bet_target = "PLAYER"
        # elif(banker_win_count < player_win_count):
        #     if(amount == 1000): click_at(BANKER_POS)
        #     if(amount == 14000): 
        #         click_at(BANKER_POS)
        #     if(amount == 80000): 
        #         click_at(BANKER_POS)
        #     bet_target = "BANKER"
        # else: 
        #     if(last_restart == "BANKER"):
        #         bet_target = last_restart
        #         click_at(BANKER_POS)
        #     else:
        #         bet_target = last_restart
        #         click_at(PLAYER_POS)

        if(amount == 1000): click_at(AMOUNT_POS[amount])
        if(amount == 14000): 
            click_at(AMOUNT_POS[5000])
            
        if(amount == 80000): 
            click_at(AMOUNT_POS[25000])
        
        if(banker_win_count > player_win_count):
            if(amount == 1000): click_at(PLAYER_POS)
            if(amount == 14000): 
                click_at(AMOUNT_POS[5000])
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(AMOUNT_POS[2000])
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
            if(amount == 80000):
                click_at(AMOUNT_POS[25000])
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(PLAYER_POS)
                click_at(AMOUNT_POS[5000])
                click_at(PLAYER_POS)
            bet_target = "PLAYER"
        elif(banker_win_count < player_win_count):
            if(amount == 1000): click_at(BANKER_POS)
            if(amount == 14000): 
                click_at(AMOUNT_POS[5000])
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(AMOUNT_POS[2000])
                click_at(BANKER_POS)
                click_at(BANKER_POS)
            if(amount == 80000): 
                click_at(AMOUNT_POS[25000])
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(BANKER_POS)
                click_at(AMOUNT_POS[5000])
                click_at(BANKER_POS)
            bet_target = "BANKER"
        else: 
            if(last_restart == "BANKER"):
                bet_target = last_restart
                click_at(BANKER_POS)
            else:
                bet_target = last_restart
                click_at(PLAYER_POS)
                
        
        totalBat += 1
        print(f"🎯 배팅: {bet_target}, 금액: {amount}원, 단계: {stage}단계, 총 배팅: {totalBat}회")

        if stopped:
            break   

    # 적절한 sleep 필수
    time.sleep(1)
