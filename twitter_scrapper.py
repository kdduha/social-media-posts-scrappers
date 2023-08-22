from selenium import webdriver
import selenium.common.exceptions as errors
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

import time


def logging(driver, login_url, LOGIN, USERNAME, PASSWORD):

    driver.get(login_url)
    time.sleep(2)

    login = driver.find_element(By.XPATH, "//input").send_keys(LOGIN)
    submit = driver.find_elements(By.CSS_SELECTOR, "[role='button']")[2].click()
    time.sleep(2)

    try: 
        password = driver.find_element(By.CSS_SELECTOR, "[name='password']").send_keys(PASSWORD)
        submit = driver.find_element(By.CSS_SELECTOR, "[data-testid='LoginForm_Login_Button']").click()
        time.sleep(2)

    except errors.NoSuchElementException:
        check_name = driver.find_element(By.XPATH, "//input").send_keys(USERNAME)
        submit = driver.find_element(By.CSS_SELECTOR, "[data-testid='ocfEnterTextNextButton']").click()
        time.sleep(2)

        password = driver.find_element(By.CSS_SELECTOR, "[name='password']").send_keys(PASSWORD)
        submit = driver.find_element(By.CSS_SELECTOR, "[data-testid='LoginForm_Login_Button']").click()
        time.sleep(2)
        
        
    print(f"{time.ctime().split()[-2]} You're succesfully signed up!")

    
def switch_window(driver, user_url):
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    driver.get(user_url)
    time.sleep(10)
    
    
def check_profile(driver):
    try:
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="tweet"]')))
        print(f"{time.ctime().split()[-2]} Connection established")
    except WebDriverException:
        print(f"{time.ctime().split()[-2]} Tweets did not appear! Proceeding after timeout")


def parsing_loaded_tweets(data, driver):
    
    posts = driver.find_elements(By.CSS_SELECTOR, "[data-testid='tweet']")
    time.sleep(2)

    for post in posts:

        post_status_label = post.find_element(By.CSS_SELECTOR, "[data-testid='User-Name']")
        post_links = post_status_label.find_elements(By.CSS_SELECTOR, "[role='link']")
        post_user_url = post_links[0].get_attribute('href') + '?lang=en'

        if post_user_url == user_url:
            parsed_post = dict()

            try:
                parsed_post['text'] = post.find_element(By.CSS_SELECTOR, "div[data-testid='tweetText']").text
            except errors.NoSuchElementException:  
                print(f'{time.ctime().split()[-2]} Post is skipped cause there is no text')
                break

            parsed_post['date'] = post_links[-1].get_attribute('aria-label')
            parsed_post['post url'] = post_links[-1].get_attribute('href')
            parsed_post['user name'] = parsed_user
            
            if parsed_post not in data:
                data.append(parsed_post)
                print(f'{time.ctime().split()[-2]} Parsed one post')
        else:
            print(f"{time.ctime().split()[-2]} It's not {parsed_user} post, continue parsing")


def parsing_dynamic_page(data, driver, tweets_number):
    
    notification_tab = False
    
    total_tweets = driver.find_element(By.CSS_SELECTOR, "[class='css-901oao css-1hf3ou5 r-14j79pv r-37j5jr r-n6v787 r-16dba41 r-1cwl3u0 r-bcqeeo r-qvutc0']").text.split()[0]
    total_tweets = float(total_tweets[:-1]) * 1_000 if total_tweets[-1] == 'K' else int(total_tweets)
    
    start, end = 0, 250
    while tweets_number > len(data) and tweets_number < total_tweets:
        
        parsing_loaded_tweets(data, driver)
        
        ActionChains(driver).scroll_by_amount(start, end).perform()
        time.sleep(2)
        
        start += 250
        end += 250
        
        if not notification_tab:
            try:
                notification = driver.find_element(By.CSS_SELECTOR, "[data-testid='sheetDialog']")
                submit = notification.find_elements(By.CSS_SELECTOR, "[role='button']")[-1].click()
                notification_tab = True
                print(f'{time.ctime().split()[-2]} Notification label was closed')
            except errors.NoSuchElementException:
                pass
        
    print(f'{time.ctime().split()[-2]} Done!')          


if __name__ == "__main__":
    
    parsed_user = '@elonmusk'
    login_url = 'https://twitter.com/login'

    LOGIN = 'example@gmail.com'
    PASSWORD = 'example_password'
    USERNAME = '@example'
    
    user_url = f'https://twitter.com/{parsed_user[1:]}?lang=en'
    
    tweets_number = 20
    data = []
    
    time_action = time.ctime().split()[-2]
    with webdriver.Chrome() as driver:
        t_start = time.perf_counter()
        
        logging(driver, login_url, LOGIN, USERNAME, PASSWORD)
        switch_window(driver, user_url)
        check_profile(driver)
        parsing_dynamic_page(data, driver, tweets_number)
        
        print(f'\n\nTotal posts: {len(data)}\nTotal parsing time: {round(time.perf_counter() - t_start, 3)} sec')
    
