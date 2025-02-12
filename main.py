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
                "탄천 평일 1코트": "FAC26",
                "탄천 평일 2코트": "FAC17",
                "탄천 평일 3코트": "FAC18",
                "탄천 평일 4코트": "FAC35",
                "탄천 토요일 4코트": "FAC43",
                "탄턴 일요일 1코트": "FAC41",
                "탄천 일요일 4코트": "FAC19",
                "탄천 당일 토요일 1코트": "FAC46"
            },
            "야탑":{
                "야탑 1코트": 'FAC99',
                "야탑 2코트": 'FAC100', 
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

        self.users = {
            "정건우": {
                "id": "doscm164",
                "pwd": "!rjsdn123",
                "partner_name": "양승희",
                "partner_number": "01086159140"
            },
            "양승희": {
                "id": "0603yang",
                "pwd": "Yeji9140!!",
                "partner_name": "정건우",
                "partner_number": "01048085382"
            }
        }


        # self.users = {
        #     "임정연": {
        #         "id": "aliceice",
        #         "pwd": "Jagh0412!!",
        #         "partner_name": "양승희",
        #         "partner_number": "01086159140"
        #     },
        #     "정건우": {
        #         "id": "doscm164",
        #         "pwd": "!rjsdn123", 
        #         "partner_name": "박성찬",
        #         "partner_number": "01093968821"
        #     }
        # }


        # self.users = {
        #     "최종문": {
        #         "id": "swingcjm",
        #         "pwd": "qtm@@890",
        #         "partner_name": "정건우",
        #         "partner_number": "01048085382"
        #     },
        #     "박성찬": {
        #         "id": "pptroll",
        #         "pwd": "@@ignite123",
        #         "partner_name": "양승희",
        #         "partner_number": "01086159140"
        #     }
        # }

        
        # 기본 윈도우 설정
        self.setWindowTitle("자동 예약 GUI")
        self.setGeometry(100, 100, 300, 400)
        
        # 레이아웃 설정
        layout = QVBoxLayout()


        # 사용자 선택
        self.user_select_label = QLabel("사용자 선택:")
        layout.addWidget(self.user_select_label)
        self.user_select_combo = QComboBox()
        self.user_select_combo.addItems(self.users.keys())
        layout.addWidget(self.user_select_combo)
        self.user_select_combo.currentTextChanged.connect(self.update_user_info)

        # user_id 필드
        self.user_id_label = QLabel("아이디:")
        layout.addWidget(self.user_id_label)
        self.user_id_input = QLineEdit()
        layout.addWidget(self.user_id_input)

        # user_pw 필드
        self.user_pw_label = QLabel("비밀번호:")
        layout.addWidget(self.user_pw_label)
        self.user_pw_input = QLineEdit()
        self.user_pw_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.user_pw_input)


        # location_id 필드 (드롭다운 메뉴)
        self.location_label = QLabel("장소 선택:")
        layout.addWidget(self.location_label)
        self.location_combo = QComboBox()
        self.location_combo.addItem("탄천", 1)
        self.location_combo.addItem("수내", 5)
        self.location_combo.addItem("야탑", 14)
        self.location_combo.addItem("대원", 6)
        layout.addWidget(self.location_combo)

        # 날짜 선택
        self.date_label = QLabel("예약 날짜:")
        layout.addWidget(self.date_label)
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        layout.addWidget(self.date_input)

        # 회차 선택 필드
        self.turn_number_label = QLabel("회차:")
        layout.addWidget(self.turn_number_label)
        self.turn_number_input = QSpinBox()
        self.turn_number_input.setRange(1, 8)
        layout.addWidget(self.turn_number_input)


        # 대기 시간
        self.pending_time_label = QLabel("대기시간:")
        layout.addWidget(self.pending_time_label)
        self.pending_time_input = QLineEdit()
        self.pending_time_input.setText("10")
        layout.addWidget(self.pending_time_input)

        # 카드 ID 선택
        self.card_id_label = QLabel("코트 선택:")
        layout.addWidget(self.card_id_label)
        self.card_id_combo = QComboBox()
        layout.addWidget(self.card_id_combo)

        # 장소 선택에 따른 카드 ID 설정
        self.location_combo.currentIndexChanged.connect(self.update_card_options)

        # 예약 버튼
        self.reserve_button = QPushButton("예약 시작")
        self.reserve_button.clicked.connect(self.start_reservation)
        layout.addWidget(self.reserve_button)

        # 레이아웃 설정
        self.setLayout(layout)

        # 초기 데이터 설정 (모든 위젯 생성 후 호출)
        self.update_card_options()
        self.update_user_info()

    def update_user_info(self):
        """사용자 선택에 따른 정보 업데이트"""
        user = self.users.get(self.user_select_combo.currentText(), {})
        self.user_id_input.setText(user.get("id", ""))
        self.user_pw_input.setText(user.get("pwd", ""))
    
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
        if location == "야탑": 
            for display_name, card_code in self.card_options["야탑"].items():
                self.card_id_combo.addItem(display_name, card_code) 
        
    
    def start_reservation(self):
        # 입력된 정보 가져오기
        driver = Chrome(version_main=132)
        self.driver = driver
        user_id = self.user_id_input.text()
        user_pw = self.user_pw_input.text()
        location_id = self.location_combo.currentData()
        year_month_day = self.date_input.date().toString("yyyy-MM-dd")
        turn_number = self.turn_number_input.value()
        pending_time = self.pending_time_input.text()
        card_id = self.card_id_combo.currentData()  # 실제 예약에 필요한 card_id 값
        
        # 예약 절차 시작
        self.driver.get("https://res.isdc.co.kr")
        time.sleep(5)

        
        
        # 로그인
        self.driver.find_element(By.ID, "web_id").send_keys(user_id)
        self.driver.find_element(By.ID, "web_pw").send_keys(user_pw)

        # 예약 시간 대기
        move_distance = 100  # 픽셀 단위로 좌우로 이동할 거리
        while True:
            move_distance = move_distance * -1 
            pyautogui.moveRel(move_distance * -1, 0, duration=0.5)
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"Current time is {current_time}, waiting until 07:00 AM.") 
            if "06:58:00" <= current_time <= "07:05:00":  # 06:58 ~ 07:05 사이의 조건
                print("It's exactly 07:00 AM, proceeding with the next steps.", )
                break
            time.sleep(3)  

        self.driver.find_element(By.ID, "btn_login").click()
        
        # 예약 페이지 이동 후 특정 위치, 코트, 날짜 및 회차 선택
        time.sleep(5)
        self.driver.find_element(By.ID, str(location_id)).click()
        time.sleep(2)  
        self.driver.find_element(By.ID, card_id).click()

        formatted_date = datetime.strptime(year_month_day, "%Y-%m-%d").strftime("%Y-%m-%d")
        formatted_date = formatted_date.replace("-0", "-")
        
       

        # 날짜 클릭
        refresh_done = False  # 리프레시 여부를 확인하는 플래그
        while True:
            current_time = datetime.now().strftime("%H:%M:%S")
            print(f"Current time is {current_time}, waiting until 07:00 AM.")            

            if current_time >= "06:59:59":
                print("It's exactly 07:00 AM, attempting to find and click the target date.")
                if not refresh_done:  # 리프레시가 아직 실행되지 않았다면
                    print("It's exactly 07:00 AM, refreshing the page once.")
                    self.driver.refresh()
                    refresh_done = True  # 플래그를 True로 변경
                    print("Page refreshed.")
                    
                try:
                    # 지정된 날짜 요소가 존재하면 클릭
                    # 선택한 날짜가 다음달인 경우, 다음달 버튼 클릭 
                    
                    print("@@@month",formatted_date.split("-")[1], datetime.now().month)
                    if formatted_date.split("-")[1] != str(datetime.now().month):
                        print("다음 달로 이동합니다.") 
                        self.driver.find_element(By.CLASS_NAME, "ui-datepicker-next").click()
                    print("@@@formatted_date",formatted_date)
                    calendar_date = self.driver.find_element(By.ID, formatted_date)
                    calendar_date.click()
                    print(f"Clicked on the calendar date: {formatted_date}")
                    break  # 클릭 성공 시 루프 중단
                except NoSuchElementException:
                    print("요소를 찾을 수 없습니다. 페이지를 새로고침합니다.")
                    self.driver.refresh()  # 새로고침
                    body_class = self.driver.find_element(By.TAG_NAME, "body").get_attribute("class")
                    if "neterror" in body_class:
                        print("네트워크 오류 발생. 페이지를 이동합니다.")
                        self.driver.get("https://res.isdc.co.kr/index.do")
                        self.driver.find_element(By.ID, str(location_id)).click()
                        time.sleep(1)  
                        self.driver.find_element(By.ID, card_id).click()
                except ElementClickInterceptedException:
                    print("클릭이 가로막혔습니다. 대기 후 재시도합니다.")  # 새로고침하지 않음
                    calendar_date_text = calendar_date.text  # 현재 텍스트 가져오기
                    self.driver.execute_script(
                        """
                        arguments[0].innerHTML = '<font>' + arguments[1] + '</font>';
                        """,
                        calendar_date,
                        calendar_date_text
                    )
                    self.driver.execute_script("""arguments[0].setAttribute('style', 'pointer-events: auto; background-color: rgb(212, 245, 193); color: rgb(0, 0, 0);'); arguments[0].classList.add('ui-state-default', 'spandate', 'usedate');
                    """, calendar_date)
                except Exception as e:
                    print(f"예상치 못한 오류 발생: {e}. 페이지를 새로고침합니다.")
                    self.driver.refresh()  # 새로고침
            time.sleep(1)
        
       
        # 예약 제출
        self.driver.find_element(By.ID, "move_reservation").click()

        # 회차 선택
        start_time = time.time()  # 회차 선택 시작 시각 기록
        while not self.select_turn(driver, turn_number):
            time.sleep(0.5) 


        # 예약자 정보
        # Step 9: 사용자 정보 입력

        def type_text_slowly(element, text, delay=0.15):
            element.clear()  # 기존 텍스트 제거
            for char in text:
                element.send_keys(char)
                time.sleep(delay)  # 입력 사이 간격 설정

        
        WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, "label[for='userType-P']")))
        userTypeEl = self.driver.find_element(By.CSS_SELECTOR, "label[for='userType-P']")
        ActionChains(driver).move_to_element(userTypeEl).perform()
        userTypeEl.click() 
        # headcount_field = self.driver.find_element(By.ID, "headcount")
        # type_text_slowly(headcount_field, "2")
        self.driver.find_element(By.ID, "headcount").send_keys("2")

        # user2_field = self.driver.find_element(By.ID, "user2")
        # partner_name = self.users[self.user_select_combo.currentText()]["partner_name"]
        # type_text_slowly(user2_field, partner_name)
        self.driver.find_element(By.ID, "user2").send_keys(self.users[self.user_select_combo.currentText()]["partner_name"])
        
        # user2_contact_field = self.driver.find_element(By.ID, "user2_contact")
        # partner_number = self.users[self.user_select_combo.currentText()]["partner_number"]
        # type_text_slowly(user2_contact_field, partner_number)
        self.driver.find_element(By.ID, "user2_contact").send_keys(self.users[self.user_select_combo.currentText()]["partner_number"])


        # 스크롤 최하단으로 이동
        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(0.5)  # 스크롤 완료를 기다림

        # 캡챠 해결 시도

        while not self.attempt_submission():
            time.sleep(0.5)  # 재시도 간격을 둠

        end_time = time.time()
        duration = end_time - start_time
        print(f"회차 선택부터 캡챠 해결 시도까지 소요 시간: {duration:.2f}초")  # 소요 시간 출력

        # 9초 미만일 경우 부족한 시간만큼 대기
        pending = float(pending_time)
        if duration < pending:
            wait_time = pending - duration
            print(f"{pending}초를 맞추기 위해 {wait_time:.2f}초 대기합니다.")
            time.sleep(wait_time)


        reservation_button = driver.find_elements(By.CSS_SELECTOR, "[id^='btnReservation']")
        reservation_button[0].click()
        
        
        QMessageBox.information(self, "성공", "예약이 완료되었습니다.")
        self.driver.quit()
    
    def select_turn(self, driver, turn_number):
        try:
            radio_buttons = self.driver.find_elements(By.CLASS_NAME, 'rbTime')
            for radio in radio_buttons:
                row = radio.find_element(By.XPATH, "./ancestor::tr")
                회차 = row.find_elements(By.TAG_NAME, 'td')[1].text.strip()
                if 회차 == str(turn_number):
                    self.driver.execute_script("arguments[0].click();", radio)
                    return  True
            return False
        except Exception as e:
            print(f"회차 선택 중 오류 발생: {e}")
            return False
                


    def solve_captcha(self):
        # 캡챠 이미지 요소를 스크린샷으로 가져오기
        captcha_element = self.driver.find_element(By.ID, "captcha_img")
        captcha_image_png = captcha_element.screenshot_as_png

        # 스크린샷을 이미지 파일d로 저장
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
            # for char in captcha_answer:
                # answer_field.send_keys(char)
                # time.sleep(0.2)  # 글자 입력 사이에 약간의 대기 추가 (옵션)
            
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
