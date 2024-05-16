from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import pandas as pd
import os


# Bắt đầu chương trình
# Đổi topic để crawl chủ đề khác
# Nếu là topic mới không trong mapper thì thêm vào mapper
topic = 'công nghệ'
mapper = {'thế giới': 'the-gioi', 'việc làm': 'viec-lam', 'bất động sản':'bat-dong-san',
          'giáo dục': 'giao-duc', 'kinh doanh': 'kinh-doanh', 'xã hội': 'xa-hoi', 'nhân ái': 'nhan-ai', 
          'sức khỏe':'suc-khoe', 'văn hóa': 'van-hoa', 'xe': 'o-to-xe-may', 'công nghệ' : 'suc-manh-so',
          'an sinh': 'an-sinh', 'pháp luật': 'phap-luat', 'thể thao': 'the-thao',
          'giải trí': 'giai-tri'}

# Reset page ở đây đẻ crawl trang
page = 6

# Tạo driver để crawl
bot = webdriver.Edge(executable_path='msedgedriver.exe')
bot.get(f'https://dantri.com.vn/{mapper[topic]}{"" if page == 1 else ("/trang-" + str(page))}.htm')
bot.maximize_window()

data = []
count = 1


while True:
     articles = WebDriverWait(bot, 100).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".main .article-item")))
     for i in range(0, len(articles)):
          print(f'Đang crawl item thứ {i+1} - trang {page} ...............')
          # Tìm link ảnh để bấm
          WebDriverWait(bot, 100).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".main .article-item .article-content .article-title a")))
          try:
               link = articles[i].find_element(By.CSS_SELECTOR, '.article-content .article-title a')
          except:
               print('Error is here !!!')
               continue

          # Click link
          sleep(1)
          original_window = bot.current_window_handle
          link.click()
          new_window = bot.current_window_handle
          bot.switch_to.window(new_window)
          try:
               para = WebDriverWait(bot, 30).until(EC.visibility_of_element_located((By.CSS_SELECTOR, ".singular-container")))
          except:
               # bot.back()
               # bot.switch_to.window(original_window)
               # articles = WebDriverWait(bot, 60).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".main .article-item")))
               # continue
               try:
                    para = WebDriverWait(bot, 60).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "article.e-magazine")))
               except:
                    bot.back()
                    bot.switch_to.window(original_window)
                    articles = WebDriverWait(bot, 100).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".main .article-item")))
                    continue

          # Thu thập title
          try:
               title = para.find_element(By.CSS_SELECTOR,'.title-page.detail').get_attribute('textContent').strip('\" ')
          except:
               # title = None
               try:
                    title = para.find_element(By.CSS_SELECTOR,'.e-magazine__title').get_attribute('textContent').strip('\" ')
               except:
                    bot.back()
                    bot.switch_to.window(original_window)
                    articles = WebDriverWait(bot, 100).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".main .article-item")))
                    continue
          print(f'title : {title}')

          # Thu thập summary
          try:
               summary =  para.find_element(By.CSS_SELECTOR,'.singular-sapo').get_attribute('textContent').strip('\" ')
          except:
               try:
                    summary =  para.find_element(By.CSS_SELECTOR,'.e-magazine__sapo').get_attribute('textContent').strip('\" ')
               except:
                    bot.back()
                    bot.switch_to.window(original_window)
                    articles = WebDriverWait(bot, 100).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".main .article-item")))
                    continue
          print(f'summary : {summary}')
          
          # Thu thập text
          # texts = para.find_elements(By.CSS_SELECTOR, 'p')
          try:
               texts = para.find_elements(By.CSS_SELECTOR, 'p')
          except:
               texts = None
          if texts == None:
               bot.back()
               bot.switch_to.window(original_window)
               articles = WebDriverWait(bot, 100).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".main .article-item")))
               continue

          sentences = []
          for t in texts:
               sentences.append(t.get_attribute('textContent').strip('\" '))
          removed_text = 'This is a modal window. Bắt đầu cửa sổ hộp thoại. Esc sẽ thoát và đóng cửa sổ. Kết thúc cửa sổ hộp thoại. '
          text = ' '.join(sentences)
          text = text.replace(removed_text,'')
          text = re.sub("\s\(.-*?\)","",text)

          # Thêm dữ liệu vào biến data
          data.append({'topic': topic, 'title': title ,'text': text, 'summary': summary})

          # Quay về trang trước
          bot.back()
          bot.switch_to.window(original_window)
          articles = WebDriverWait(bot, 100).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".main .article-item")))
     # Viết vào file
     df = pd.DataFrame.from_dict(data)
     df.to_csv(f'{mapper[topic]}.csv', mode='a', index=False, header=False)
     data = []
     # Chuyển sang trang tiếp theo
     isFound = False
     count += 1
     navigations = WebDriverWait(bot, 100).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, ".pagination > .page-item")))
     for navigate_link in navigations:
          num_page = navigate_link.get_attribute('textContent')
          if num_page == '❯': 
               isFound = True
               navigate_link.click()
               page += 1
               new_window = bot.current_window_handle
               bot.switch_to.window(new_window)
               break
          else: continue
     if isFound: continue
     else: break
# df = pd.DataFrame.from_dict(data)
# df.to_csv(f'{mapper[topic]}.csv', index=False)

# Clean text : (Ảnh : ...) , (thử cho các dấu cách từ một khoảng trắng)