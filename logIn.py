from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time


def login():
    # driver = webdriver.Chrome(executable_path='/Users/himanshuaggarwal/PycharmProjects/pythonProject/chromedriver')
    driver = webdriver.Firefox(executable_path='/Users/himanshuaggarwal/PycharmProjects/pythonProject/geckodriver')
    driver.maximize_window()
    driver.get('https://www.linkedin.com/login?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin')
    driver.find_element_by_id('username').send_keys(Keys.COMMAND + "a")
    driver.find_element_by_id('username').send_keys(Keys.DELETE)
    driver.find_elements_by_id('username')[0].send_keys('himanshu.aggarwal@ironhack.com')
    # driver.find_elements_by_id('username')[0].send_keys('himanshuag098@gmail.com')
    # driver.find_elements_by_id('username')[0].send_keys('ahenpayhs4@gmail.com')

    time.sleep(3)
    # print("username successful")
    driver.find_element_by_id('password').send_keys(Keys.COMMAND + "a")
    driver.find_element_by_id('password').send_keys(Keys.DELETE)
    driver.find_elements_by_id('password')[0].send_keys('Himagga11!')
    # driver.find_elements_by_id('password')[0].send_keys('Hello123')
    # driver.find_elements_by_id('password')[0].send_keys('Hello11!')
    try:
        driver.switch_to.active_element.send_keys(Keys.ENTER)
    except AttributeError:
        print('enter did not work')
        try:
            driver.find_element_by_class_name('login__form_action_container').click()
        except AttributeError:
            print('Username Password Step Errored')
            # exit()
    time.sleep(2)
    if 'checkpoint' in driver.current_url:
        driver.find_element_by_xpath('/html/body/div/main/div/section/footer/form[2]/button').click()
        time.sleep(2)
    try:
        driver.find_element_by_id('ember24').click()
    except Exception as e:
        try:
            time.sleep(2)
            driver.find_element_by_id('global-nav-icon--mercado__jobs').click()
        except Exception as e:
            try:
            #     driver.find_element_by_xpath('/html/body/div[6]/header/div/nav/ul/li[3]/a/span').click()
            #     time.sleep(2)
            # except AttributeError:
            #     try:
                driver.get('https://www.linkedin.com/jobs/')
            except Exception as e:
                print(e)
                print('could not click on jobs tab')
    time.sleep(2)
    return driver, driver.current_url


if __name__ == 'main':
    login()
