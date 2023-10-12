class Nav:
    def __init__(self, month, day, week, prev, next, today):
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
    pass


class User:
    def __init__(self, id, title, link_user, data):
        self.id = id
        self.title = title
        self.link_user = link_user
        self.data = data
        print("Создан новый пользователь")

    def time_lesson(self):
        return self.data["N группы"].rstrip()[-2:]

    def is_indiv(self):
        return 1 if self.data["N группы"].rstrip()[-2:].isdigit() else 0

    def is_ovz(self):
        return 1 if self.data["ОВЗ"].strip().lower() == "да" else 0

    def __str__(self):
        return f"{self.id}\n" \
               f"{self.title}\n" \
               f"{self.data['Курс']}\n"


