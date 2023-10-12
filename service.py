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
    pass
