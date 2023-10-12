import os
from service import Nav
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import *
from pprint import pprint

from dotenv import load_dotenv
from datetime import datetime, timedelta

start_time = datetime.now()
load_dotenv()

driver = webdriver.Firefox()
driver.set_window_size(2060, 1440)
url = "https://rtschool.s20.online/login?backUrl=https%3A%2F%2Frtschool.s20.online%2Fteacher%2F1%2Fcalendar%2Findex"
wait = WebDriverWait(driver, 10)
lessons = {"complete": {"gr_pro": [], "group2": [], "group3": [], "group4": [], "ind50": [], "ind80": [], "OVZind50": [], "Trial": [], "add_less": []},
           "cancel": [], "unpayed": [], "uncomplete": []}


today = datetime.now()
last_month = today - timedelta(days=1)

days_in_last_month = (last_month.replace(day=1) - timedelta(days=1)).day
def login_alfa():
    username_input = driver.find_element(By.NAME, "LoginForm[username]")
    password_input = driver.find_element(By.NAME, "LoginForm[password]")
    submit_button = driver.find_element(By.NAME, "login-button")

    username_input.send_keys(os.getenv('EMAIL'))
    password_input.send_keys(os.getenv('PASSWORD'))
    submit_button.click()


def find_lessons():
    global lessons
    try:
        # wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fc-event")))
        for _ in driver.find_elements(By.CLASS_NAME, "fc-event.status3"):
            lesson_name = _.text
            _.click()
            try:
                div_popover = driver.find_element(By.CLASS_NAME, "popover-content")
            except NoSuchElementException:
                _.click()
                div_popover = driver.find_element(By.CLASS_NAME, "popover-content")
            status = div_popover.find_elements(By.TAG_NAME, "span")[2].text
            if status == "не спис":
                lessons["unpayed"].append(_)
            else:
                if "gr_" in _.text.lower():
                    lessons["complete"]["gr_pro"].append(_)
                elif "gr" in _.text.lower():
                    lessons["complete"]["group4"].append(_)
                else:
                    driver.implicitly_wait(3)
                    # print(lesson_name)
                    if div_popover.find_element(By.CLASS_NAME, "col-sm-7").text.strip().split('\n')[0] == "Индивидуальный":
                        div_popover.find_element(By.XPATH, "/html/body/div[16]/div[2]/div[1]/div/a").click()
                        driver.implicitly_wait(3)
                        driver.switch_to.window(driver.window_handles[1])
                        take_and_save_screenshot("info table lag")
                        info_table = driver.find_element(By.CLASS_NAME, "col-lg-4")
                        driver.execute_script("window.scrollBy(0, 500);")
                        time_lesson = driver.find_element(By.XPATH, "/html/body/div[2]/div/div/div[2]/div[3]/div[2]/div/div/div[39]/div[2]").text[-2:]
                        if time_lesson.isdigit():
                            if info_table.find_elements(By.CLASS_NAME, "row")[19].text == "да":
                                lessons["complete"][f"OVZind{time_lesson}"].append(_)
                            else:
                                lessons["complete"][f"ind{time_lesson}"].append(_)
                        else:
                            lessons["complete"][f"add_less"].append(_)

                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                        _.click()
                    else:
                        lessons["complete"]["Trial"].append(_)

                pprint(lessons["unpayed"])
        for _ in driver.find_elements(By.CLASS_NAME, "fc-event.status1"):
            lessons["uncomplete"].append(_)
        for _ in driver.find_elements(By.CLASS_NAME, "fc-event.status2"):
            lessons["cancel"].append(_)
        return lessons
    except TimeoutException:
        pass


def get_nav_buttons():
    wait.until(EC.title_is("Календарь | ALFACRM"))
    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "fc-month-button")))
    month_button = driver.find_element(By.CLASS_NAME, "fc-month-button")
    day_button = driver.find_element(By.CLASS_NAME, "fc-agendaDay-button")
    week_button = driver.find_element(By.CLASS_NAME, "fc-agendaWeek-button")
    prev_button = driver.find_element(By.CLASS_NAME, "fc-prev-button")
    next_button = driver.find_element(By.CLASS_NAME, "fc-next-button")
    today_button = driver.find_element(By.CLASS_NAME, "fc-today-button")
    return Nav(month_button, day_button, week_button, prev_button, next_button, today_button)


def go_to_first_day_of_month():
    nav.month()
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fc-more")))
    nav.prev()
    nav.day()
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, "fc-content")))


def take_and_save_screenshot(screen_name):
    scr_shot = driver.get_screenshot_as_png()
    with open(f"{screen_name}.png", "wb") as file:
        file.write(scr_shot)


def show_info(les):
    print(f"""
    Оплаченных  уроков: 
        gr_pro: {len(les["complete"]["gr_pro"])},
        Индивы 50 минут: {len(les["complete"]["ind50"])},
        Индивы 80 минут: {len(les["complete"]["ind80"])},
        Группы4: {len(les["complete"]["group4"])},
        Индвивы ОВЗ: {len(les["complete"]["OVZind50"])},
        Пробные: {len(les["complete"]["Trial"])}
        Групп отработка: {len(les["complete"]["add_less"])}
    Отмененных уроков: {len(les["cancel"])},
    Неоплаченных уроков: {len(les["unpayed"])},
    Неотмеченных уроков: {len(les["uncomplete"])}
    """)


def collect_month_lesson():
    go_to_first_day_of_month()
    for day in range(days_in_last_month):
        print(float((datetime.now()-start_time).seconds))
        response_lessons = find_lessons()
        try:
            nav.next()
        except ElementClickInterceptedException:
            driver.find_element(By.CSS_SELECTOR, "a.pull-right:nth-child(2)").click()
            nav.next()
    # for lesson in response_lessons["complete"]:
    #     print(lesson.find_element(By.CLASS_NAME, "fc-title").text)
    show_info(response_lessons)


if __name__ == "__main__":
    driver.get(url)
    login_alfa()
    nav = get_nav_buttons()
    collect_month_lesson()
