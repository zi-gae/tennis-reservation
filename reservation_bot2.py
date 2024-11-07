from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pytesseract
import cv2
import numpy as np
import time
from selenium.webdriver.common.alert import Alert
from datetime import datetime
from selenium.common.exceptions import NoSuchElementException
import pyautogui


import ssl
ssl._create_default_https_context = ssl._create_unverified_context


location_id = 5 # 탄천 1, 수내 5
year_month = "2024-11"  # 원하는 년월 입력
day = "8"  # 원하는 일자 입력
turn_number = 1
card_id = "FAC64"


# Step 1: Chrome 드라이버 시작
driver = Chrome()

# Step 2: 예약 페이지 방문
driver.get("https://res.isdc.co.kr")
time.sleep(1)  # 페이지 로딩을 기다림

# Step 3: 로그인 정보 입력ØD
driver.find_element(By.ID, "web_id").send_keys("doscm164")
driver.find_element(By.ID, "web_pw").send_keys("!rjsdn123")

move_distance = 100  # 픽셀 단위로 좌우로 이동할 거리

while True:
    move_distance = move_distance * -1 
    pyautogui.moveRel(move_distance * -1, 0, duration=0.5)
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"Current time is {current_time}, waiting until 07:00 AM.") 
    if "06:55:00" <= current_time <= "07:05:00":  # 06:55 ~ 07:05 사이의 조건
        print("It's exactly 07:00 AM, proceeding with the next steps.", )
        break
    time.sleep(1)  

# Step 4: 로그인 버튼 클릭 (로그인 버튼 ID 확인 필요)
login_button = driver.find_element(By.ID, "btn_login")  # 예시로 버튼 ID 사용
login_button.click()

# 로그인 후 페이지 이동을 기다림
WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "1")))
time.sleep(0.5)  # 추가 딜레이


# while True:
#     current_time = datetime.now().strftime("%H:%M:%S")
#     print(f"Current time is {current_time}, waiting until 07:00 AM.") 
#     if current_time == "06:59:59":
#         print("It's exactly 07:00 AM, proceeding with the next steps.", )
#         break
#     time.sleep(1)  

# Step 5: 페이지 이동 후 예약 섹션으로 이동
driver.find_element(By.ID, location_id).click()
time.sleep(2)
# Step 6: 특정 시설 선택
driver.find_element(By.ID, card_id).click()

time.sleep(3)

# Step 7: 캘린더에서 날짜 선택
# 이번달 예약 해야 할 떄
while True:
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"Current time is {current_time}, waiting until 07:00 AM.")

    if current_time >= "07:00:00":
        driver.refresh()  # 새로고침 
        print("It's exactly 07:00 AM, attempting to find and click the target date.")
        try:
            # 지정된 날짜 요소가 존재하면 클릭
            calendar_date = driver.find_element(By.ID, f"{year_month}-{day}")
            calendar_date.click()
            print(f"Clicked on the calendar date: {year_month}-{day}")
            break  # 클릭 성공 시 루프 중단
        except NoSuchElementException:
            print(f"Element for date {year_month}-{day} not found. Retrying...")
    
    time.sleep(1)
# 다음달 예약 해야 할 때
# max_attempts = 5  # 최대 반복 횟수 설정
# attempts = 0  # 시도 횟수 초기화

# while attempts < max_attempts:
#     try:
#         # 날짜가 보이면 클릭
#         calendar_date = driver.find_element(By.ID, f"{year_month}-{day}")
#         print("@@@@",calendar_date)
#         calendar_date.click()
#         print(f"{year_month}-{day} 날짜가 선택되었습니다.")
#         break
#     except:
#         print("다음 달로 이동합니다.")
#         attempts += 1
#         # 다음 달로 이동하는 버튼을 다양한 방법으로 찾기
#         try:
#             next_month_button = driver.find_element(By.NAME, "nextMon")
#         except:
#             try:
#                 next_month_button = driver.find_element(By.CSS_SELECTOR, ".ui-datepicker-next")
#             except:
#                 next_month_button = driver.find_element(By.XPATH, "//a[contains(@class, 'ui-datepicker-next')]")

#         next_month_button.click()
#         time.sleep(0.5)  # 페이지 로딩 기다림 및 딜레이 추가
    

driver.find_element(By.ID, "move_reservation").click()
time.sleep(0.5)  # '예약으로 이동' 버튼 클릭 후 기다림

# Step 8: 회차 선택
def select_radio_by_회차(target_회차):
    # 모든 라디오 버튼 요소 가져오기
    radio_buttons = driver.find_elements(By.CLASS_NAME, 'rbTime')
    
    for radio in radio_buttons:
        # 라디오 버튼의 부모 tr 요소 찾기
        row = radio.find_element(By.XPATH, "./ancestor::tr")
        
        # 회차를 포함하는 두 번째 td 요소의 텍스트 추출
        회차 = row.find_elements(By.TAG_NAME, 'td')[1].text.strip()
        
        # 타겟 회차와 일치하면 라디오 버튼을 JavaScript로 클릭
        if 회차 == str(target_회차):
            driver.execute_script("arguments[0].click();", radio)
            break

select_radio_by_회차(turn_number)


# Step 9: 사용자 정보 입력
driver.find_element(By.CSS_SELECTOR, "label[for='userType-P']").click()
time.sleep(1)
driver.find_element(By.ID, "headcount").send_keys("2")
time.sleep(1)
driver.find_element(By.ID, "user2").send_keys("양승희")
time.sleep(1.5)
driver.find_element(By.ID, "user2_contact").send_keys("01086159140")
time.sleep(2)

# Step 10: 캡챠 이미지 처리
# 캡챠 이미지 요소를 스크린샷으로 가져오기
def scroll_to_bottom():
    # 페이지 최하단으로 스크롤
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(0.5)  # 스크롤 완료를 기다림

def solve_captcha():
    # 캡챠 이미지 요소를 스크린샷으로 가져오기
    captcha_element = driver.find_element(By.ID, "captcha_img")
    captcha_image_png = captcha_element.screenshot_as_png

    # 스크린샷을 이미지 파일로 저장
    with open("captcha.png", "wb") as f:
        f.write(captcha_image_png)

    # 이미지 전처리 및 OCR
    captcha_image = cv2.imread("captcha.png", cv2.IMREAD_GRAYSCALE)

    # Adaptive Thresholding으로 이진화
    binary_image = cv2.adaptiveThreshold(captcha_image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

    # 노이즈 제거용 커널 생성
    kernel = np.ones((2, 2), np.uint8)
    processed_image = cv2.morphologyEx(binary_image, cv2.MORPH_CLOSE, kernel)

    # OCR 수행 - 숫자 6자리만 인식하도록 설정
    captcha_answer = pytesseract.image_to_string(processed_image, config='--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789').strip()
    print(f"OCR 캡챠 해석 결과: {captcha_answer}")

    return captcha_answer if len(captcha_answer) == 6 else None

def attempt_submission():
    captcha_answer = solve_captcha()
    check_button = driver.find_element(By.ID, "check")
    if captcha_answer:
        # 캡챠 입력 및 제출
        answer_field = driver.find_element(By.ID, "answer")
        answer_field.clear()
        answer_field.send_keys(captcha_answer)
        
        check_button.click()
        
        # 확인 창 메시지 출력
        time.sleep(0.5)  # 잠시 대기 후 confirm 창 확인
        alert = Alert(driver)
        alert_contains_confirm = "확인" in alert.text
        alert.accept()  # 확인 창 닫기
        return alert_contains_confirm
    else:
        check_button.click()
        alert = Alert(driver)
        alert.accept()
        return False 


# 재시도 루프
scroll_to_bottom()  # 시작 전 최하단으로 스크롤
while not attempt_submission():
    time.sleep(0.5)  # 재시도 간격을 둠

reservation_button = driver.find_element(By.ID, "btnReservation")
reservation_button.click()

input("예약을 완료하려면 엔터를 누르세요.")
driver.quit()
