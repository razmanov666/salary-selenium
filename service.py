class Nav:
    def __init__(self, month=None, day=None, week=None, prev=None, next=None, today=None):
        self.attr_month = month
        self.attr_day = day
        self.attr_week = week
        self.attr_prev = prev
        self.attr_next = next
        self.attr_today = today

    def day(self):
        self.attr_day.click()

    def month(self):
        self.attr_month.click()

    def week(self):
        self.attr_week.click()

    def prev(self):
        self.attr_prev.click()

    def next(self):
        self.attr_next.click()

    def today(self):
        self.attr_today.click()


class Lesson:
    def __init__(self, date=None, time_start=None, time_end=None, id_user=None, name=None, is_abon=None, data=None):
        self.date = date
        self.time_start = time_start
        self.time_end = time_end
        self.id = id_user
        self.name = name
        self.is_abon = is_abon
        self.data = data

    def __str__(self):
        lesson_show_str = (f"id: {self.id}\n"
                           f"name: {self.name}\n"
                           f"datetime: {self.time_start}-{self.time_end} {self.date}\n"
                           f"payed: {self.is_abon}\n"
                           f"other data: {self.data}\n")
        return lesson_show_str


class User:
    def __init__(self, id, title, link, data):
        self.id = id
        self.title = title
        self.link = link
        self.data = data

    def time_lesson(self):
        return self.data["N группы"].strip()[-2:]

    def is_indiv(self):
        return 1 if self.data["N группы"].strip()[-2:].isdigit() else 0

    def is_ovz(self):
        return 1 if self.data["ОВЗ"].strip().lower() == "да" else 0

    def __str__(self):
        return f"{self.id}\n" \
               f"{self.title}\n" \
               f"{self.data['Курс']}\n"

    def __dict__(self):
        return {"id": self.id,
                "title": self.title,
                "link": self.link,
                "data": self.data}


