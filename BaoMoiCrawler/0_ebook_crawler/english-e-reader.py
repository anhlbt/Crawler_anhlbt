from os.path import dirname, join, realpath, isfile
import sys

CURRENT_DIR = dirname(realpath(__file__))
PARENT_DIR = dirname(CURRENT_DIR)

sys.path.insert(0, PARENT_DIR)
import requests
import shutil
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.firefox.options import Options
from utils.instalogger import InstaLogger
import pdb
from selenium.webdriver.support.ui import Select
import requests
from os.path  import basename, join


def get_html_(url):
    # sleep(0.5)
    k = 0
    page = ""
    while page == '':
        try:
            # headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686; rv:68.0) Gecko/20100101 Firefox/68.0'}  
            headers = {
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36'}
            page = requests.get(url, headers=headers)
            return page.text
            break
        except Exception as ex:
            print(ex)
            k += 1
            print("Connection refused by the doctor server..")
            print("Let me sleep for 10 seconds")
            print("ZZzzzz...")
            sleep(10)
            # print("Was a nice sleep, now let me continue...")
            continue


def get_info(html,image_folder):
     
    dictionary = []
    # dic={}

    # x=(html.find("<table class=\"detail-view table table-striped table-condensed\" id=\"yw1\">"))
    # html1=html[x:-1]
    #
    # try:
    soup1 = BeautifulSoup(html, "lxml")
    #     soup2 = BeautifulSoup(html1,"lxml")
    soup1 = soup1.find("div", class_="container fix-height").findAll("div", class_="book-container")
    for i in soup1:
        dictionary.append("https://english-e-reader.net" + i.find("a").get("href"))
        img_link = "https://english-e-reader.net" + i.find("img").get("src")
        # with open(join(image_folder,basename(img_link)), "wb") as f:
        #     f.write(requests.get(img_link).content)
    return dictionary

def get_img_cover(html, image_folder):
    
    dictionary = []
    soup1 = BeautifulSoup(html, "lxml")
    soup1 = soup1.findAll("div", class_="book-container")
    for i in soup1:
        img_link = "https://english-e-reader.net" + i.find("img").get("src")

        # r = requests.get(img_link, stream = True)
        # if r.status_code == 200:
        #     # Set decode_content value to True, otherwise the downloaded image file's size will be zero.
        #     r.raw.decode_content = True
            
        #     # Open a local file with wb ( write binary ) permission.
        #     with open(join(image_folder,basename(img_link)), "wb") as f:
        #         shutil.copyfileobj(r.raw, f)
                
        #     print('Image sucessfully Downloaded: ',img_link)
        # else:
        #     print('Image Couldn\'t be retreived')

        dictionary.append(img_link)
        with open(join(image_folder,basename(img_link)), "wb") as f:
            f.write(requests.get(img_link).content)
    return dictionary    

def get_files(url):
    croll_by_Y = 400
    js_string = '''var tmp = document.elementFromPoint({0}, {1});  \
                    mutex = true; \
                    tmp.click();'''
    js_check_location = '''\
            function printMousePos(event) {\
                alert("clientX: " + event.clientX + " - clientY: " + event.clientY) }\
            document.addEventListener("click", printMousePos);'''
            
    js_download='''$( "button.btn.btn-danger" ).click(
			function( event ) {
				var target = event.target;
                
				var downloadID = ( new Date() ).getTime();
                target.setAttribute('href', "downloadFileByFormat('mp3')");
				//target.href += ( "?downloadID=" + downloadID );
				var cookiePattern = new RegExp( ( "downloadID=" + downloadID ), "i" );
                console.log(cookiePattern)
                
				var cookieTimer = setInterval( checkCookies, 500 );
				function checkCookies() {
					if ( document.cookie.search( cookiePattern ) >= 0 ) {
						clearInterval( cookieTimer );
						console.log( "Download complete!!" );
						return(
							console.log( "Download complete!!" )
						);
					}
					console.log(
						"File still downloading...",
						new Date().getTime(),
                        document.cookie.split(";")

					);
				}
			}
		);

    '''
    
    # 
    # document.cookie.search( "/downloadID=1593836174248/i" )
    chrome_options = Options()
    chrome_options.add_argument('--dns-prefetch-disable')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--lang=en-US')
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument('window-size=1920x1200')
    downloadFilepath = '~/Downloads/english_reader'
    # downloadFilepath='/media/anhlbt/DATA/A2_Elementary'
    prefs = {'profile.default_content_setting_values.automatic_downloads': 1,\
        "profile.default_content_settings.popups":0, \
            "download.default_directory": downloadFilepath,\
         'intl.accept_languages': 'en-US'}
    chrome_options.add_experimental_option('prefs',prefs) 
    chrome_options.add_experimental_option("excludeSwitches", ['enable-automation']);
    # browser = geckodriver 
    # browser= webdriver.Firefox(options=chrome_options)
    browser = webdriver.Chrome(join(CURRENT_DIR,'assets/chromedriver'), options=chrome_options)    
    # makes sure slower connections work as well        
    print ("Waiting 10 sec")
    browser.implicitly_wait(1)   
    
    try:
        browser.get(url)
    except Exception as e:
        print(e)
        browser.quit()
        
    try:
        browser.implicitly_wait(2)

        # #open file in write and binary mode
        # with open('Logo.png', 'wb') as file:
        #     #identify image to be captured
        #     l = browser.find_element_by_xpath("/html/body/div[3]/div/div[1]/div[1]/img")
        #     #write file
        #     image_url = l.get_attribute("src")
        #     reponse = requests.get(image_url)
        #     file.write(reponse.content)        
        
        
        window_size = browser.get_window_size()
        browser.maximize_window()
        # browser.execute_script(js_download)
        browser.execute_script("window.scrollTo(0, {0});".format(croll_by_Y))
        browser.implicitly_wait(3)
        actions = ActionChains(browser)
        
        
        dismiss_cookie = browser.find_element_by_xpath('/html/body/div[1]/div/a')
        browser.execute_script(js_string.format(int(dismiss_cookie.rect['x'])+ 5, int(dismiss_cookie.rect['y']) + 5 - croll_by_Y))
        browser.implicitly_wait(3)
        # actions.click(dismiss_cookie).perform()
        

        # browser.execute_script(js_string.format(854, 463))
        el2 = browser.find_element_by_xpath('//*[@id="dropdown"]/div/button[2]') #choose ebook format
        browser.execute_script(js_string.format(int(el2.rect['x'])+ 5, int(el2.rect['y']) + 5 - croll_by_Y))
        browser.implicitly_wait(3)
        # actions.click(el2).perform()
        # actions.click()
  
        # browser.execute_script(js_string.format(821, 613))
        el3 = browser.find_element_by_xpath('//*[@id="dropdown"]/div/ul/li[5]/a') # select txt format
        browser.execute_script(js_string.format(int(el3.rect['x'])+ 5, int(el3.rect['y']) + 5 - croll_by_Y))
        # actions.click(el3).perform()
        
        # browser.execute_script(js_string.format(791, 475))
        el4 = browser.find_element_by_xpath('//*[@id="download"]') #download txt book
        browser.execute_script(js_string.format(int(el4.rect['x'])+ 5, int(el4.rect['y']) + 5 - croll_by_Y))
        # actions.click(el4).perform()
        # browser.execute_script(js_download)
  
        
        try:
            audio = browser.find_element_by_xpath('/html/body/div[3]/div/div[1]/div[2]/div[8]/a') # download audio
        except Exception as ex:
            print(ex)
            try:
                audio =  browser.find_element_by_xpath("/html/body/div[3]/div/div[1]/div[2]/div[8]/div[1]/button[1]")
            except Exception as ex:
                print(ex)
                InstaLogger.logger().warn('link: %s, no have audio file' %(url))
        if (audio):        
            browser.execute_script(js_string.format(int(audio.rect['x'])+ 5, int(audio.rect['y']) + 5 - croll_by_Y))
   
            
        InstaLogger.logger().info('link: %s' %(url))
        

    except Exception as e:
        print(e)
    finally:
        
        print("close browser after 200s....")
        sleep(200)
        
        browser.delete_all_cookies()
        browser.close()
        # browser.quit()

if __name__ == "__main__":
    #https://english-e-reader.net/level/elementary
    image_folder = '/media/anhlbt/DATA/A2_Elementary'
    html = get_html_("https://english-e-reader.net/level/elementary") 

    links = (get_info(html, image_folder))
    for index,i in enumerate(links):
        print(i, "\n{} from {}".format(str(index+1),str(len(links))))
        get_files(i)
        

    # get_img_cover(html, image_folder) 

    # pdb.set_trace()
    # get_files('https://english-e-reader.net/book/muhammad-ali-b-smith')
        # 

