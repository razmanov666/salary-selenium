from selenium import webdriver
from selenium.webdriver.common.by import By
# Создаем экземпляр браузера (здесь используется Chrome)
driver = webdriver.Chrome()

# Открываем страницу для входа в Google
driver.get('https://accounts.google.com/ServiceLogin')

# Вписываем e-mail
email_input = driver.find_element(By.ID, 'identifierId')
email_input.send_keys('razmanov666@gmail.com')

# Нажимаем "Далее"
next_button = driver.find_element(By.ID, 'identifierNext')
next_button.click()

# Вписываем пароль
password_input = driver.find_element(By.NAME, 'password')
password_input.send_keys('mypassword')

# Нажимаем "Далее" и ожидаем загрузки Google Sheets
submit_button = driver.find_element(By.ID, 'passwordNext')
submit_button.click()