import pyautogui
import sys
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox,
                             QSpinBox, QDateEdit, QMessageBox)
import cv2
from PyQt5.QtCore import QDate
from undetected_chromedriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import pytesseract
import numpy as np
import time
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.common.action_chains import ActionChains


import ssl
ssl._create_default_https_context = ssl._create_unverified_context




class ReservationApp(QWidget):
    def __init__(self):
        super().__init__()

        # 카드 ID 옵션 설정 (사용자 표시명: 코드값)
        self.card_options = {
            "탄천": {
                "탄천 평일 2코트": "FAC17",
                "탄천 토요일 4코트": "FAC42",
                "탄천 일요일 4코트": "FAC19",
                "탄천 당일 평일 코트": "FAC46"
            },
            "수내": {
                "수내 1코트": "FAC61",
                "수내 2코트": "FAC62",
                "수내 3코트": "FAC64",
                "수내 4코트": "FAC65",
                "수내 5코트": "FAC66",
                "수내 6코트": "FAC85"
            },
            "대원" :{
                "대원 1코트": "FAC67", 
            }
        }
        
        # 기본 윈도우 설정
        self.setWindowTitle("자동 예약 GUI")
        self.setGeometry(100, 100, 300, 400)
        
        # 레이아웃 설정
        layout = QVBoxLayout()
        
        # user_id 필드
        self.user_id_label = QLabel("아이디:")
        layout.addWidget(self.user_id_label)
        self.user_id_input = QLineEdit()
        self.user_id_input.setText("doscm164")  # 아이디 기본값
        layout.addWidget(self.user_id_input)
        
        # user_pw 필드
        self.user_pw_label = QLabel("비밀번호:")
        layout.addWidget(self.user_pw_label)
        self.user_pw_input = QLineEdit()
        self.user_pw_input.setEchoMode(QLineEdit.Password)
        self.user_pw_input.setText("!rjsdn123")  # 비밀번호 기본값
        layout.addWidget(self.user_pw_input)
        
        # location_id 필드 (드롭다운 메뉴)
        self.location_label = QLabel("장소 선택:")
        layout.addWidget(self.location_label)
        self.location_combo = QComboBox()
        self.location_combo.addItem("탄천", 1)
        self.location_combo.addItem("수내", 5)
        self.location_combo.addItem("대원", 6)
        layout.addWidget(self.location_combo)
        
        # 날짜 선택 필드 (Date Picker)
        self.date_label = QLabel("예약 날짜:")
        layout.addWidget(self.date_label)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        layout.addWidget(self.date_input)
        
        # 회차 선택 필드 (카운터)
        self.turn_number_label = QLabel("회차:")
        layout.addWidget(self.turn_number_label)
        self.turn_number_input = QSpinBox()
        self.turn_number_input.setRange(1, 8)
        layout.addWidget(self.turn_number_input)
        
        # card_id 필드 (장소에 따라 선택 값 달라짐)
        self.card_id_label = QLabel("코트 선택:")
        layout.addWidget(self.card_id_label)
        self.card_id_combo = QComboBox()
        layout.addWidget(self.card_id_combo)
        
        # 장소 선택에 따른 카드 ID 설정
        self.location_combo.currentIndexChanged.connect(self.update_card_options)
        self.update_card_options()  # 초기값 설정
        
        # 예약 시작 버튼
        self.reserve_button = QPushButton("예약 시작")
        self.reserve_button.clicked.connect(self.start_reservation)
        layout.addWidget(self.reserve_button)
        
        # 레이아웃 설정
        self.setLayout(layout)
    
    def update_card_options(self):
        self.card_id_combo.clear()
        location = self.location_combo.currentText()
        if location == "탄천":
            for display_name, card_code in self.card_options["탄천"].items():
                self.card_id_combo.addItem(display_name, card_code)
        if location == "대원": 
            for display_name, card_code in self.card_options["대원"].items():
                self.card_id_combo.addItem(display_name, card_code) 
        if location == "수내": 
            for display_name, card_code in self.card_options["수내"].items():
                self.card_id_combo.addItem(display_name, card_code)
    
    def start_reservation(self):
        # 입력된 정보 가져오기
        driver = Chrome()
        self.driver = driver
        user_id = self.user_id_input.text()
        user_pw = self.user_pw_input.text()
        location_id = self.location_combo.currentData()
        year_month_day = self.date_input.date().toString("yyyy-MM-dd")
        turn_number = self.turn_number_input.value()
        card_id = self.card_id_combo.currentData()  # 실제 예약에 필요한 card_id 값
        
        # 예약 절차 시작
        self.driver.get("https://res.isdc.co.kr")
        time.sleep(1)

        
        
        # 로그인
        self.driver.find_element(By.ID, "web_id").send_keys(user_id)
        self.driver.find_element(By.ID, "web_pw").send_keys(user_pw)

        # 예약 시간 대기
        # move_distance = 100  # 픽셀 단위로 좌우로 이동할 거리
        while True:
            move_distance = move_distance * -1 
            pyautogui.moveRel(move_distance * -1, 0, duration=0.5)
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"Current time is {current_time}, waiting until 07:00 AM.") 
            if "06:55:00" <= current_time <= "07:05:00":  # 06:55 ~ 07:05 사이의 조건
                print("It's exactly 07:00 AM, proceeding with the next steps.", )
                break
            time.sleep(1)  

        self.driver.find_element(By.ID, "btn_login").click()
        
        # 예약 페이지 이동 후 특정 위치, 코트, 날짜 및 회차 선택
        time.sleep(1)
        self.driver.find_element(By.ID, str(location_id)).click()
        time.sleep(1)  
        self.driver.find_element(By.ID, card_id).click()

        formatted_date = datetime.strptime(year_month_day, "%Y-%m-%d").strftime("%Y-%m-%d")
        formatted_date = formatted_date.replace("-0", "-")
        print("@@@formatted_date",formatted_date)
        # 날짜 클릭        
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"Current time is {current_time}, waiting until 07:00 AM.")

            if current_time >= "06:59:59":
                self.driver.refresh()  # 새로고침 
                print("It's exactly 07:00 AM, attempting to find and click the target date.")
                try:
                    # 지정된 날짜 요소가 존재하면 클릭
                    calendar_date = self.driver.find_element(By.ID, formatted_date)
                    calendar_date.click()
                    print(f"Clicked on the calendar date: {formatted_date}")
                    break  # 클릭 성공 시 루프 중단
                except Exception as e:
                    if isinstance(e, NoSuchElementException):
                        print("요소를 찾을 수 없습니다. 다른 페이지나 상태를 확인하세요.")
                    elif isinstance(e, ElementClickInterceptedException):
                        print("클릭이 가로막혔습니다. 대기 후 재시도합니다.")
            time.sleep(1)
        
       
        # 예약 제출
      
        self.driver.find_element(By.ID, "move_reservation").click()

         # 회차 선택
         
        self.select_turn(self.driver, turn_number)

        # 예약자 정보
        # Step 9: 사용자 정보 입력
        
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "label[for='userType-P']")))
        userTypeEl = self.driver.find_element(By.CSS_SELECTOR, "label[for='userType-P']")
        ActionChains(driver).move_to_element(userTypeEl).perform()
        userTypeEl.click() 
        time.sleep(1)
        self.driver.find_element(By.ID, "headcount").send_keys("2")
        time.sleep(1)
        self.driver.find_element(By.ID, "user2").send_keys("양승희")
        time.sleep(1.5)
        self.driver.find_element(By.ID, "user2_contact").send_keys("01086159140")
        time.sleep(2)


        # 스크롤 최하단으로 이동
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)  # 스크롤 완료를 기다림

        # 캡챠 해결 시도
        while not self.attempt_submission():
            time.sleep(0.5)  # 재시도 간격을 둠

        reservation_button = self.driver.find_element(By.ID, "btnReservation")
        # reservation_button.click()
        
        QMessageBox.information(self, "성공", "예약이 완료되었습니다.")
        self.driver.quit()
    
    def select_turn(self, driver, turn_number):
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, 'rbTime'))) 
        radio_buttons = self.driver.find_elements(By.CLASS_NAME, 'rbTime')
        print("@@@",radio_buttons)
        for radio in radio_buttons:
            row = radio.find_element(By.XPATH, "./ancestor::tr")
            회차 = row.find_elements(By.TAG_NAME, 'td')[1].text.strip()
            if 회차 == str(turn_number):
                self.driver.execute_script("arguments[0].click();", radio)
                break


    def solve_captcha(self):
        # 캡챠 이미지 요소를 스크린샷으로 가져오기
        captcha_element = self.driver.find_element(By.ID, "captcha_img")
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

    def attempt_submission(self):
        captcha_answer = self.solve_captcha()
        check_button = self.driver.find_element(By.ID, "check")
        if captcha_answer:
            # 캡챠 입력 및 제출
            answer_field = self.driver.find_element(By.ID, "answer")
            answer_field.clear()
            answer_field.send_keys(captcha_answer)
            
            check_button.click()
            
            # 확인 창 메시지 출력
            time.sleep(0.5)  # 잠시 대기 후 confirm 창 확인
            alert = Alert(self.driver)
            alert_contains_confirm = "확인" in alert.text
            alert.accept()  # 확인 창 닫기
            return alert_contains_confirm
        else:
            check_button.click()
            alert = Alert(self.driver)
            alert.accept()
            return False 

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ReservationApp()
    window.show()
    sys.exit(app.exec_())
