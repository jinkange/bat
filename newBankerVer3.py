try:
    import cv2
    import pyautogui
    import numpy as np
    import time
    import os
    import keyboard
    import threading
    import mss
    import winsound
    import ctypes
    import win32gui
    import win32con
    
except Exception as e:
    print(e)
    
    
    
    
    
    
    
    
running = False
stopped = False
sueChange = False
# 키 입력 감지 스레드
def keyboard_listener():
    global running, stopped
    global hole_total_profit
    global banker_win_count, player_win_count, bet_target, isWaiting
    while True:
        if keyboard.is_pressed('a'):
            running = True
            stopped = False
            print("✅ 매크로 시작됨")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            time.sleep(0.5)
        elif keyboard.is_pressed('s'):

            running = False
            stopped = True
            print("⛔ 매크로 정지됨")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            hole_total_profit= 0
            init()
            time.sleep(0.5)
        elif keyboard.is_pressed('d'):
            print("💹 슈 교체 한턴 쉬기 및 카운팅 초기화")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            banker_win_count = 0
            player_win_count = 0
            bet_target = ''
            isWaiting= True
            time.sleep(0.5)
        elif keyboard.is_pressed('f'):
            print("💹 매크로 초기화")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            totalRestart()
            stopped = True
            time.sleep(0.5)
            
listener_thread = threading.Thread(target=keyboard_listener, daemon=True)
listener_thread.start()

def set_console_window(x=1360, y=160, width=570, height=330, always_on_top=True):
    hwnd = ctypes.windll.kernel32.GetConsoleWindow()
    if hwnd:
        win32gui.MoveWindow(hwnd, x, y, width, height, True)
        if always_on_top:
            win32gui.SetWindowPos(
                hwnd,
                win32con.HWND_TOPMOST,
                0, 0, 0, 0,
                win32con.SWP_NOMOVE | win32con.SWP_NOSIZE
            )

# 실행 시 적용
set_console_window()


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

bet_region = (715, 165, 463, 238)

# 뱃클로즈
wat_region = (800, 689, 340, 61)
# dd
open_region = (650, 960, 700, 118)
#슈체인지
sue_region = (15,815, 508, 205)
sue_region2 = (15,815, 508, 205)

# 특정 영역에서 이미지가 있는지 판단하는 함수
def is_image_in_region(template_path, region, threshold=0.96):
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
    # if(max_val >= threshold):
    #     print(f"{template_path} : {max_val} 찾음!")
    # else:
    #     print(f"{template_path} : {max_val}")
    return max_val >= threshold

# 클릭 함수
def click_at(pos):
    if pos:
        pyautogui.click(pos)

# 이미지 경로들
img_path = "./newImages/"
images = {
    "place_bet": os.path.join(img_path, "place_bet.png"),
    "bet_closed": os.path.join(img_path, "bet_closed.png"),
    "banker_win": os.path.join(img_path, "banker_win.png"),
    "player_win": os.path.join(img_path, "player_win.png"),
    "reissued": os.path.join(img_path, "reissued.png"),
    "tie": os.path.join(img_path, "tie.png")
}

# 좌표 예시 (실제 화면에 맞게 조정 필요)
BANKER_POS = (1166,877)
PLAYER_POS = (733,869)
AMOUNT_POS = {
    100: (700,1020),
    500: (771, 1020),
    2500: (848, 1020),
    10000: (919, 1020),
    125000: (1071, 1020),
    500000: (1141, 1020),
    500000: (1141, 1020),
    2500000: (1219, 1020),
}

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
    amount = 0
    
def totalRestart():
    global restart
    global waitingCount
    global isWaiting
    global totalBat
    global batSize
    global bet_target
    global stage
    global total_profit
    global hole_total_profit
    global banker_win_count
    global player_win_count
    global amount
    global last_restart
    global last_restart_bat_size
    global isRestart
    global isSueRestart
    global isPass
    global isSueRestartChange
    global isSuePass
    global isSueChange

    global running
    global stopped
    global sueChange
    running = False
    stopped = False
    sueChange = False
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
    
    
def get_integer_input(prompt):
    while True:
        try:
            value = int(input(prompt))  # 음수 포함 정수 입력 받기
            return value
        except ValueError:
            print("숫자만 입력해주세요.")
            
# 매크로 시작 시 입력 받기
TURN_FINISH_PRICE = get_integer_input("💰 판당 목표 수익 금액을 입력하세요 (예: -50): ")
GAME_FINISH_PRICE = get_integer_input("🛑 매크로 정지 수익 금액을 입력하세요 (예: 850): ")
GAME_BAT_PRICE = get_integer_input("▷ 판당 배팅 금액을 입력하세요 (예: 500): ")
print(f"판당 목표 수익 : {TURN_FINISH_PRICE} / 매크로 정지수익 : {GAME_FINISH_PRICE}")
print(f"✅ 배팅금액 1단계 x {GAME_BAT_PRICE}원 [비율배팅] *TEST ver3.0.2")
# print("✅ 배팅금액 1단계 x {GAME_BAT_PRICE}원 [비율배팅] ver3.0.2")
print("▶ A : 시작, S : 정지, D : 슈교체 및 초기화, F : 매크로 초기화")

sorted_chips = sorted(AMOUNT_POS.keys(), reverse=True)
        
def get_chip_combination(amount):
    """큰 칩부터 조합"""
    amount = int(round(amount))  # 👈 float을 int로 바꿔서 방지
    combination = []
    for chip in sorted_chips:
        count = int(amount // chip)
        if count > 0:
            combination.append((chip, count))
            amount -= chip * count
    return combination

def place_bet(target_pos, amount):
    """칩 1번 클릭 → 해당 위치에 반복 클릭"""
    combination = get_chip_combination(amount)

    for chip_value, count in combination:
        chip_pos = AMOUNT_POS[chip_value]

        # 칩 클릭 1번
        pyautogui.click(chip_pos)
        time.sleep(0.1)
        try:
            safe_count = int(count)
        except (TypeError, ValueError):
            print(f"경고: count 값이 정수로 변환 불가합니다: {count}")
            continue
        # 대상에 safe_count번 클릭
        for _ in range(safe_count):
            pyautogui.click(target_pos)
            time.sleep(0.1)
def beep_alert():
    for _ in range(6):  # 삐비 삐비 2번
        winsound.Beep(1000, 150)  # 주파수: 1000Hz, 지속시간: 150ms
        winsound.Beep(1500, 150)




while True:
    if not running:
        time.sleep(1)
        continue

    # 매크로 루프 시작
    while running:
        
        # is_image_in_region(images["banker_win"],bet_region)
        # is_image_in_region(images["player_win"],bet_region)
        # is_image_in_region(images["tie"],bet_region)
        # is_image_in_region(images["bet_closed"],wat_region)
        # is_image_in_region(images["place_bet"],open_region)
        # is_image_in_region(images["reissued"],sue_region)
        # continue
        #목표치 확인
        if hole_total_profit >= GAME_FINISH_PRICE:
            print("💰 누적 목표 수익 도달, 매크로 정지")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            time.sleep(1)
            running = False
            stopped = True
            restart = False
            print("⛔ 매크로 정지됨")
            beep_alert()
            hole_total_profit= 0
            init()
            time.sleep(0.5)
            continue
        
        if stage > 200:
            print("💰 손절 스테이지 도달, 매크로 정지")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
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
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        
        # pos = find_image_on_screen('./newImages/stop.png')
        # if pos:
        #     running = False
        #     stopped = True
        #     print("⛔ 게임 팅김 매크로 정지됨")
        #     init()
        #     time.sleep(0.5)
        #     break
            
        if(restart):
            isWaiting = True
            waitingCount += 1
            if(waitingCount > 2):
                restart = False
                isRestart = True
                isSueRestartChange = True
                break
            print(f"💹 2판중 {waitingCount}판 대기중...")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            while not is_image_in_region(images["bet_closed"], wat_region):
                if stopped:
                    break
            
            
        
        if(not restart):
            if(not isSueRestartChange):
                if(not isSueChange):
                    pos = is_image_in_region(images["reissued"], sue_region)
                    if pos:
                        print("💹 슈 교체 한턴 쉬기 및 카운팅 초기화")
                        print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
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
            if is_image_in_region(images["banker_win"],bet_region):
                result = "BANKER"
                last_restart = "BANKER"
                batSize = 1.95
                last_restart_bat_size=1.95
                isRestart = False
                isPass = False
                if(not restart): banker_win_count += 1
                if(player_win_count == banker_win_count): isWaiting= True
                else: isWaiting= False
            elif is_image_in_region(images["player_win"],bet_region):
                result = "PLAYER"
                last_restart = "PLAYER"
                batSize = 2
                last_restart_bat_size = 2
                isRestart = False
                isPass = False
                if(not restart): player_win_count += 1
                if(player_win_count == banker_win_count): isWaiting= True
                else: isWaiting= False
            elif is_image_in_region(images["tie"],bet_region):
                if(isRestart):
                    print("💹 2판 대기중 무승부 → 직전판 그대로 배팅 ")
                    isRestart = False
                    result = last_restart
                    batSize = last_restart_bat_size
                    isWaiting= False
                else:
                    result = "TIE"
                    batSize = 1
                    print("💹 무승부 → 다음판으로")
                    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                    isPass = True
                    time.sleep(2)
                    break
                
        if(isPass and isWaiting):
            isPass = False
            continue
        
        if stopped:
            break
                
        
        if(result == bet_target and bet_target != '' and result != "TIE"):
            stage += 1
            total_profit = total_profit + (amount * batSize) - amount
            hole_total_profit =  hole_total_profit + (amount * batSize) - amount
            if(not (restart)): print(f"🏆 결과: {result} 비율 PLAYER {player_win_count} : BANKER {banker_win_count} (승리)")
            print(f"💹 누적 수익: {total_profit}원 / 총 수익: {hole_total_profit}원")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
            if(hole_total_profit >= GAME_FINISH_PRICE): continue
            if total_profit >= TURN_FINISH_PRICE:
                print("💰 수익 목표 도달, 데이터 초기화, 2판 대기후 재시작")
                print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
                time.sleep(1)
                init()
                restart = True
                isWaiting = True
                continue
        elif(result != bet_target and bet_target != '' and result !="TIE"):
            stage += 1
            total_profit = total_profit - amount
            hole_total_profit =  hole_total_profit - amount
            if(not (restart)): print(f"🏆 결과: {result} 비율 PLAYER {player_win_count} : BANKER {banker_win_count} (패배)")
            print(f"💹 누적 수익: {total_profit}원 / 총 수익: {hole_total_profit}원")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        else:
            if(not (restart)): print(f"🏆 결과: {result} 비율 PLAYER {player_win_count} : BANKER {banker_win_count} (관전)")
            print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
        
        time.sleep(1)
                
        while not is_image_in_region(images["place_bet"], open_region):
            if stopped:
                break
        if stopped:
            break
        
        pos = is_image_in_region(images["reissued"], sue_region)
        if(not restart):
            if(not isSueRestartChange):
                if pos:
                    print("💹 슈 교체 한턴 쉬기 및 카운팅 초기화")
                    print("ㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡㅡ")
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
        

        # 50단계 10000원 배팅 일때 총 누적 금액이 -5000원이다.
        # 배팅금액(10000원) > -5000 * -1 해서 배팅금액이 크면 추가 알고리즘 작동
        # 굳이 만원을 걸 필요없이 5000원(25단계)만 걸어서 따면 26단계부터 다시 진행하면 됨
        # 이길시 : 
        # 1. 플 승이면 초기화
        # 2. 뱅 승리시 26단계 (배팅금액 5200원) 총누적 금액 -500원이기
        # 3. 다음 배팅금액 5200원보다 -500이 적기 때문에 추가 알고리즘 작동이기때문에 200원(1단계) 배팅을 함
        # 4. 그럼 -50원이기때문에 판수 초기화 완료
        # 지면 : 51단계
        amount = stage * GAME_BAT_PRICE
        if(total_profit < -50 and stage != 2):
            if(amount >= total_profit * -1):
                print(f"배팅금액 : {amount} > 누적수익 : {total_profit}")
                stage = (total_profit * -1) // GAME_BAT_PRICE
                if(stage <= 0):
                    stage = 1
                amount = stage * GAME_BAT_PRICE
                print(f"※누적수익에 따른 배팅금액,단계 변경")
                print(f"배팅금액 : {amount}, 단계 : {stage}")
                
                
            
        # 실제 배팅
        if(banker_win_count < player_win_count):
            place_bet(BANKER_POS, amount)
            bet_target = "BANKER"
        elif(banker_win_count > player_win_count):
            place_bet(PLAYER_POS, amount)
            bet_target = "PLAYER"
        else: 
            if(last_restart == "BANKER"):
                bet_target = "PLAYER"
                place_bet(PLAYER_POS, amount)
            else:
                bet_target = "BANKER"
                place_bet(BANKER_POS, amount)
        # # 테스트
        # if(banker_win_count < player_win_count):
        #     click_at(AMOUNT_POS[100])
        #     click_at(BANKER_POS)
        #     bet_target = "BANKER"
        # elif(banker_win_count > player_win_count):
        #     click_at(AMOUNT_POS[100])
        #     click_at(PLAYER_POS)
        #     bet_target = "PLAYER"
        # else: 
        #     if(last_restart == "BANKER"):
        #         bet_target = "PLAYER"
        #         click_at(AMOUNT_POS[100])
        #         click_at(PLAYER_POS)
                
        #     else:
        #         bet_target = "BANKER"
        #         click_at(AMOUNT_POS[100])
        #         click_at(BANKER_POS)
        
        totalBat += 1
        print(f"🎯 배팅: {bet_target}, 금액: {amount}원, 단계: {stage}단계, 총 배팅: {totalBat}회")

        if stopped:
            break   

    # 적절한 sleep 필수
    time.sleep(1)
