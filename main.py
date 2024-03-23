import os
import re
from service import Nav, User, Lesson
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, TimeoutException
from pprint import pprint
import gspread
import json
import copy

from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()

# payment = "gr_pro": [],
#                         "group2": [],
#                         "group3": [],
#                         "group4": [],
#                         "ind50": [],
#                         "ind80": [],
#                         "OVZind50": [],
#                         "Trial": [],
#                         "add_less": []
baseplate_lessons = {"complete": {"gr_pro": [],
                                  "group2": [],
                                  "group3": [],
                                  "group4": [],
                                  "ind50": [],
                                  "ind80": [],
                                  "OVZind50": [],
                                  "Trial": [],
                                  "add_less": []},
                     "cancel": [],
                     "unpayed": [],
                     "uncomplete": [],
                     "other": []}

lessons = copy.deepcopy(baseplate_lessons)

lessons_per_days = {}
creds = 'credentials.json'
client = gspread.service_account(creds)

# spreadsheet = client.create('salary_month')
# worksheet = spreadsheet.get_worksheet(0)
#
# spreadsheet.share("razmanov666@gmail.com", role="writer", perm_type="user")

users = {}
today = datetime.now()
last_month = today - timedelta(days=1)

days_in_last_month = (last_month.replace(day=1) - timedelta(days=1)).day
prim_rev_month = str((last_month - timedelta(days=30)).month)
prev_month = prim_rev_month if len(prim_rev_month) == 2 else '0' + prim_rev_month
spreadsheet = client.create(f'month{last_month.month}')
weekend_sheet = []
overall_sums = []
nav = Nav()
imp_wait = 0.3


platform_url = "https://space.rts.school/"
alfa_url = "https://rtschool.s20.online/login?backUrl=https%3A%2F%2Frtschool.s20.online%2Fteacher%2F1%2Fcalendar%2Findex"

# weekend_sheet = client.create(f'month{last_month.month}')
# weekend_sheet.share("razmanov666@gmail.com", role="writer", perm_type="user")
spreadsheet.share("razmanov666@gmail.com", role="writer", perm_type="user")


def try_to_click(lesson):
    try:
        driver.execute_script("arguments[0].click();", lesson)
    except ElementClickInterceptedException:
        driver.find_element(By.CSS_SELECTOR, "a.pull-right:nth-child(2)").click()
        try_to_click(lesson)


# def sheets_wait():


def login_alfa():
    username_input = driver.find_element(By.NAME, "LoginForm[username]")
    password_input = driver.find_element(By.NAME, "LoginForm[password]")
    submit_button = driver.find_element(By.NAME, "login-button")

    username_input.send_keys(os.getenv('EMAIL'))
    password_input.send_keys(os.getenv('PASSWORD'))
    submit_button.click()
    wait.until(expected_conditions.title_is("Календарь | ALFACRM"))
    wait.until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "fc-month-button")))


def find_lessons(day_in_cal):
    global lessons
    # pprint(lessons)
    date = f"{day_in_cal}.{prev_month}.{last_month.year}"
    try:
        for current_lesson in driver.find_elements(By.CLASS_NAME, "fc-event.status3"):
            try_to_click(current_lesson)
            driver.implicitly_wait(imp_wait)
            try:
                div_popover = driver.find_element(By.CLASS_NAME, "popover-content")
            except NoSuchElementException:
                try_to_click(current_lesson)
                driver.implicitly_wait(imp_wait)
                div_popover = driver.find_element(By.CLASS_NAME, "popover-content")
            data_lesson = get_data_lesson(date, div_popover)
            lesson = Lesson(**data_lesson)
            if data_lesson["is_abon"] == "не спис":
                lesson_path = 'lessons["unpayed"]'
            else:
                if "gr_" in current_lesson.text.lower():
                    lesson_path = 'lessons["complete"]["gr_pro"]'
                elif "gr" in current_lesson.text.lower():
                    lesson_path = 'lessons["complete"]["group3"]'
                else:
                    driver.implicitly_wait(imp_wait)
                    if data_lesson["data"]["type_lesson"] == "Индивидуальный":
                        with open('user_data.json', 'r', encoding="UTF-8") as f:
                            users = json.load(f)
                        # users[lesson.id] = create_new_user(lesson.id)
                        # save_data_to_json(users[lesson.id])
                        if lesson.id not in users.keys():
                            users[lesson.id] = create_new_user(lesson.id)
                            save_data_to_json(users[lesson.id])
                            current_user = users[lesson.id]

                        else:
                            current_user = get_current_user(lesson.id)
                        if current_user.is_indiv():
                            ovz = "OVZ"
                            lesson_path = f'lessons["complete"]["{ovz * current_user.is_ovz()}ind{current_user.time_lesson()}"]'
                        else:
                            lesson_path = 'lessons["complete"][f"add_less"]'
                        current_lesson.click()
                    else:
                        lesson_path = 'lessons["complete"]["Trial"]'
            add_lesson(lesson_path, lesson)
        for current_lesson in driver.find_elements(By.CLASS_NAME, "fc-event.status1"):
            try:
                div_popover = driver.find_element(By.CLASS_NAME, "popover-content")
            except NoSuchElementException:
                current_lesson.click()
                div_popover = driver.find_element(By.CLASS_NAME, "popover-content")
            data_lesson = get_data_lesson(date, div_popover)
            lesson = Lesson(**data_lesson)
            lesson_path = 'lessons["uncomplete"]'
            add_lesson(lesson_path, lesson)
        for current_lesson in driver.find_elements(By.CLASS_NAME, "fc-event.status2"):
            try:
                div_popover = driver.find_element(By.CLASS_NAME, "popover-content")
            except NoSuchElementException:
                current_lesson.click()
                div_popover = driver.find_element(By.CLASS_NAME, "popover-content")
            data_lesson = get_data_lesson(date, div_popover)
            lesson = Lesson(**data_lesson)
            lesson_path = 'lessons["cancel"]'
            add_lesson(lesson_path, lesson)
        return lessons
    except TimeoutException:
        pass


def get_nav_buttons():
    month_button = driver.find_element(By.CLASS_NAME, "fc-month-button")
    day_button = driver.find_element(By.CLASS_NAME, "fc-agendaDay-button")
    week_button = driver.find_element(By.CLASS_NAME, "fc-agendaWeek-button")
    prev_button = driver.find_element(By.CLASS_NAME, "fc-prev-button")
    next_button = driver.find_element(By.CLASS_NAME, "fc-next-button")
    today_button = driver.find_element(By.CLASS_NAME, "fc-today-button")
    return Nav(month_button, day_button, week_button, prev_button, next_button, today_button)


def wait_lessons_load():
    try:
        wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "fc-content")))
    except TimeoutException:
        nav.next()
        wait_lessons_load()


def save_data_to_json(user):
    data = {
        user.id: {
            'title': user.title,
            'link': user.link,
            'data': user.data
        }
    }

    with open('user_data.json', 'r', encoding="UTF-8") as f:
        existing_data = json.load(f)
    existing_data.update(data)
    with open('user_data.json', 'w', encoding="UTF-8") as f:
        json.dump(existing_data, f, indent=4, ensure_ascii=False)
    # with open('user_data.json', 'w', encoding="UTF-8") as f:
    #     json.dump(data, f, indent=4, ensure_ascii=False)


def go_to_first_day_of_month():
    nav.month()
    wait.until(expected_conditions.presence_of_element_located((By.CLASS_NAME, "fc-more")))
    nav.prev()
    nav.day()
    # for i in range(20):
    #     nav.next()
    wait_lessons_load()


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


def calculate_overall():
    print(overall_sums)
    worksheet_overall = spreadsheet.get_worksheet(0)
    # worksheet_overall.update_cell(end + 3, 3, "Sum: ")


def collect_month_lesson():
    global lessons_per_days, lessons
    go_to_first_day_of_month()
    # for i in range(15):
    #     nav.next()
    for day in range(1, days_in_last_month):
        find_lessons(day)
        driver.execute_script("window.scrollTo(0, 0);")
        lessons_per_days[str(day)] = lessons
        # print(lessons_per_days)
        lessons = copy.deepcopy(baseplate_lessons)
        collect_data_in_sheets(day)
        try:
            nav.next()
        except ElementClickInterceptedException or TimeoutException:
            driver.find_element(By.CSS_SELECTOR, "a.pull-right:nth-child(2)").click()
            nav.next()
    calculate_overall()

    show_info(lessons)


def get_calculate_template(day):
    calculate_template = {"gr_pro": {"cell_start": 0, "cell_end": 0, "price": 1.8},
                          "group2": {"cell_start": 0, "cell_end": 0, "price": 6.6},
                          "group3": {"cell_start": 0, "cell_end": 0, "price": 7.7},
                          "group4": {"cell_start": 0, "cell_end": 0, "price": 8.8},
                          "ind50": {"cell_start": 0, "cell_end": 0, "price": 3.3},
                          "ind80": {"cell_start": 0, "cell_end": 0, "price": 5.5},
                          "OVZind50": {"cell_start": 0, "cell_end": 0, "price": 5.5},
                          "Trial": {"cell_start": 0, "cell_end": 0, "price": 3},
                          "add_less": {"cell_start": 0, "cell_end": 0, "price": 3}}
    prev_type = None

    for current_type in calculate_template.keys():
        if not prev_type:
            prev_day_lessons = 1
        else:
            prev_day_lessons = len(lessons_per_days[str(day)]["complete"][prev_type])
        amount_lessons = len(lessons_per_days[str(day)]["complete"][current_type])

        calculate_template[current_type]["cell_start"] = 2 if not prev_type else calculate_template[prev_type][
                                                                                     "cell_end"] + 3 if prev_day_lessons else \
            calculate_template[prev_type]["cell_end"]
        calculate_template[current_type]["cell_end"] = amount_lessons + calculate_template[current_type][
            "cell_start"] if amount_lessons else calculate_template[current_type]["cell_start"]

        prev_type = current_type
    return calculate_template


def collect_data_in_sheets(day_num):
    global overall_sums
    duration_script_before_sheets = float((datetime.now() - start_time).seconds)
    print(f"{int(duration_script_before_sheets // 60)} min {int(duration_script_before_sheets % 60)} sec")
    worksheet_day = spreadsheet.add_worksheet(str(day_num), 1000, 10)

    # worksheet_day.update_title()t = f"day{day_num}"
    data = []
    calculate_template = get_calculate_template(day_num)

    for type_les, data_les in lessons_per_days[str(day_num)]["complete"].items():
        data.append([type_les]) if lessons_per_days[str(day_num)]["complete"][type_les] else 0

        for lesson in lessons_per_days[str(day_num)]["complete"][type_les]:
            list_info = [lesson.date, f"{lesson.time_start} - {lesson.time_end}", lesson.name, lesson.is_abon]
            data.append(list_info)

        data.append([]) if lessons_per_days[str(day_num)]["complete"][type_les] else 0
        data.append([]) if lessons_per_days[str(day_num)]["complete"][type_les] else 0
        len_of_lesson_by_type_per_day = len(lessons_per_days[str(day_num)]["complete"][type_les])

        # formula = f'=SUM(D{prev_count}:D{len_of_lesson_by_type_per_day})'

        # worksheet_day.update_cell(len_of_lesson_by_type_per_day + 1, 4, formula) if len_of_lesson_by_type_per_day else 0
        # worksheet_day.update_cell(len_of_lesson_by_type_per_day + 1, 5, type_les) if len_of_lesson_by_type_per_day else 0

    # pprint(lessons_per_days)
    worksheet_day.insert_rows(data)
    end = 0
    formula_sum = '='
    for current_type in calculate_template.keys():
        if calculate_template[current_type]["cell_end"] != calculate_template[current_type]["cell_start"]:
            start = calculate_template[current_type]["cell_start"]
            end = calculate_template[current_type]["cell_end"]
            formula = f'=SUM(D{start}:D{end - 1})*{calculate_template[current_type]["price"]}'
            worksheet_day.update_cell(end, 4, formula)
            worksheet_day.update_cell(end, 5, current_type)
            formula_sum += f"D{end}+" if bool(end - start) else 0

    worksheet_day.update_cell(end + 3, 3, "Sum: ")
    worksheet_day.update_cell(end + 3, 4, formula_sum[:-1])
    overall_sums.append(end+3)


def create_new_user(id_user):
    data = {}
    link_user = f"https://rtschool.s20.online/teacher/1/customer/view?id={str(id_user)}"
    driver.execute_script(f"window.open('{link_user}', '_blank');")
    driver.switch_to.window(driver.window_handles[1])
    driver.implicitly_wait(imp_wait)
    title = driver.find_element(By.CLASS_NAME, "font-noraml.no-margins.no-padding").text.strip()
    info_rows = driver.find_element(By.CLASS_NAME, "col-lg-4").find_elements(By.CLASS_NAME, "row")
    for row in info_rows:
        try:
            data_row = row.find_elements(By.TAG_NAME, "div")
            data[data_row[0].text.strip()] = data_row[1].text.strip()
        except IndexError:
            continue
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return User(id_user, title, link_user, data)


def get_current_user(id: int):
    with open("user_data.json", "r", encoding="UTF-8") as file:
        return User(id=id, **json.load(file)[str(id)])


def add_lesson(path, les: Lesson):
    global lessons
    eval(path).append(les)


def get_data_lesson(date, div):
    try:
        is_abon = 1 if "абон" in [el.text for el in div.find_elements(By.TAG_NAME, "span")] else 0
        name = div.find_element(By.CLASS_NAME, "customer-name").text
        link_user = div.find_element(By.CLASS_NAME, "col-sm-12").find_element(By.TAG_NAME, "a").get_attribute("href")
        matches = re.findall(r'=(.*?)(?=\=|$)', link_user)
        id_user = matches[-1] if matches else None
    except NoSuchElementException or IndexError:
        is_abon = 0
        name = ''
        link_user = None
        id_user = None
    div_info = div.find_elements(By.CLASS_NAME, "col-sm-7")
    type_lesson = div_info[0].text.split()[0] if div_info[0].text.split() else None
    type_material = div_info[4].text
    time_start, time_end = [data for data in div_info[1].text.split()[1:4:2]]
    return {"date": date,
            "is_abon": is_abon,
            "time_end": time_end,
            "name": name,
            "id_user": id_user,
            "time_start": time_start,
            "data": {"type_lesson": type_lesson,
                     "type_material": type_material,
                     "link_user": link_user}
            }


def get_lessons_for_weekends():
    go_to_first_day_of_month()
    nav.month()
    nav.next()
    nav.day()
    write_data = []
    for day in range(7):
        nav.next()
    for day in range(10):
        write_data.clear()
        date = f"{day + 8}.01.{last_month.year}"
        worksheet_day = weekend_sheet.add_worksheet(f"{day + 8}.01", 1000, 10)
        # worksheet_day.insert_rows(["date", "time", "link_user", "type_lesson"])
        for current_lesson in driver.find_elements(By.CLASS_NAME, "fc-event.status1"):
            try_to_click(current_lesson)
            driver.implicitly_wait(imp_wait)
            try:
                div_popover = driver.find_element(By.CLASS_NAME, "popover-content")
            except NoSuchElementException:
                try_to_click(current_lesson)
                div_popover = driver.find_element(By.CLASS_NAME, "popover-content")
                data_lesson = get_data_lesson(date, div_popover)
                if data_lesson.get("data").get("link_user"):
                    write_data.append(
                        [data_lesson.get("date"), f'{data_lesson.get("time_start")} - {data_lesson.get("time_end")}',
                         data_lesson.get("data").get("link_user"), data_lesson.get("data").get("type_material")])
        try_to_click(nav.attr_next)
        worksheet_day.insert_rows(write_data)


def salary_last_month():
    global nav
    driver.get(alfa_url)
    login_alfa()
    nav = get_nav_buttons()

    collect_month_lesson()


def login_platform():
    driver.get(platform_url)
    driver.implicitly_wait(5)
    email_field = driver.find_element(By.XPATH,
                                      '//*[@id="rc-tabs-0-tab-2"]')
    email_field.click()
    username_input = driver.find_element(By.TAG_NAME, "input")
    username_input.send_keys(os.getenv('EMAIL'))
    submit_button = driver.find_element(By.XPATH,
                                        "/html/body/div[1]/div/section/main/div/div/div[2]/div[1]/div/div/form/button")
    submit_button.click()
    password_input = driver.find_element(By.TAG_NAME, "input")
    password_input.send_keys(os.getenv('PASSWORD'))
    submit_button = driver.find_element(By.XPATH,
                                        "/html/body/div/div/section/main/div/div/div[2]/div[1]/div/div/form/button")

    submit_button.click()
    return driver


def collect_records_url_from_platform():
    platform_rts = login_platform()
    platform_rts.find_element(By.XPATH, '//*[@id="__next"]/div/section/div/div/div[1]/div[2]/a[1]').click()
    driver.implicitly_wait(imp_wait)
    table_of_sessions = platform_rts.find_element(By.CLASS_NAME, 'SelectionList_cont__JXL4A')
    sessions = [session for session in table_of_sessions.find_elements(By.TAG_NAME, "span") if session.text]

    for session in sessions:
        session.click()
        driver.implicitly_wait(imp_wait)
        driver.find_element(By.XPATH,
                            '/html/body/div/div/section/main/div/div/div[2]/div/div/div[1]/div[2]/div/div/div/div/div[2]/div/div[4]/div/div[1]/button/span').click()
        months = driver.find_element(By.CLASS_NAME, 'RecordingsHistory_cont__UgA90').find_elements(By.CLASS_NAME,
                                                                                                   'MonthGroup_cont__GsxK9')

        for el in months:
            adsadsa = el.find_elements(By.TAG_NAME, 'div')
            for adsads in adsadsa:
                print(adsads.text)


if __name__ == "__main__":
    start_time = datetime.now()
    driver = webdriver.Firefox()
    driver.set_window_size(3000, 2000)
    driver.implicitly_wait(imp_wait)

    wait = WebDriverWait(driver, 10)

    collect_records_url_from_platform()
    # salary_last_month()

    duration_script = float((datetime.now() - start_time).seconds)
    print(f"{int(duration_script // 60)} min {int(duration_script % 60)} sec")
