from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from time import sleep
from utils import mkdir
import os


def find_save_img(nimg):
    art = soup.findChildren("article")[0]
    img_out = None
    for img in art.findChildren("img"):
        if "data-testid" not in img.attrs.keys():
            img_out = img
            break
    if img_out:
        if "src" in img_out.attrs.keys():
            impath = os.path.join(path2save, "img-{}.jpg".format(nimg))
            urlretrieve(img_out.attrs["src"], impath)
    return img_out


def find_nextbutton():
    next_button = None
    for div in soup.findChildren("div"):
        if "class" in div.attrs.keys():
            if "coreSpriteRightChevron" in div.attrs["class"]:
                next_button = div.parent
                break
    return next_button


def find_time_and_story():
    art = soup.findChildren("article")
    if len(art) >= 1:
        art = art[0]
    else:
        return None, None
    post_time = art.findChildren("time")[0].attrs["title"]
    time_stamp = art.findChildren("time")[0].attrs["datetime"].split(".")[0]
    text = post_time + "\n\n"
    for span in art.findChildren("span"):
        if len(span.contents) and "class" in span.attrs.keys():
            if span.attrs["class"] == [] and len(span.contents[0]) > 1:
                for line in span.contents:
                    line_text = str(line)
                    if not line_text.startswith("<"):
                        text += str(line)
                        text += "\n"
                break
    for a in span.findChildren("a"):
        text += a.text + " "
    return time_stamp, text


working_login = "andrybin17"
working_password = "vostok120461"
parsed_user = "andre.rybin"
n_scroll = 25
clear_folders = False

mkdir("out", clear_dirs=clear_folders)
mkdir("screens", clear_dirs=True)

chromedriver = "/home/binrey/Dev/fb_parser/resourses/chromedriver"
options = webdriver.ChromeOptions()
#options.add_argument('headless')  # для открытия headless-браузера
browser = webdriver.Chrome(executable_path=chromedriver, options=options)
sleep(1)

browser.get("https://www.instagram.com/accounts/login/?source=auth_switcher")
sleep(3)

browser.save_screenshot("./screens/init{:03.0f}.png".format(0))


email = browser.find_element_by_name("username")
password = browser.find_element_by_name("password")
login = browser.find_element_by_tag_name("button")

email.send_keys(working_login)
password.send_keys(working_password)

submit = browser.find_element_by_tag_name('form')
submit.submit()
sleep(3)
browser.save_screenshot("./screens/init{:03.0f}.png".format(1))

for i in range(n_scroll):
    browser.get("https://www.instagram.com/{}".format(parsed_user))
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)
    browser.save_screenshot("./screens/scroll{:03.0f}.png".format(i))
    print("{} scroll...".format(i))

    soup = BeautifulSoup(browser.page_source, 'html5lib')

    posts_links = []
    for div in soup.findChildren("div"):
        a = div.findChildren("a")
        if len(a):
            a = a[0].attrs["href"]
            if a.startswith("/p"):
                posts_links += [a]
    posts_links = set(posts_links)

    for npost, plink in enumerate(posts_links):
        browser.get("https://www.instagram.com/{}{}".format(parsed_user, plink))
        sleep(1)
        browser.save_screenshot("./screens/post{:03.0f}.png".format(npost))

        soup = BeautifulSoup(browser.page_source, 'html5lib')

        time_stamp, story = find_time_and_story()
        if time_stamp is None:
            print("!!! broken post: {}".format(plink))
            continue

        path2save = os.path.join("./out", "{}".format(time_stamp))
        if mkdir(path2save, clear_dirs=clear_folders):
            with open(os.path.join(path2save, "story.txt"), "w") as f:
                f.write(story)

            nimg = 0
            find_save_img(nimg)
            next_button = find_nextbutton()

            while next_button is not None:
                nimg += 1
                browser.find_elements_by_class_name(next_button.attrs["class"][0])[0].click()
                soup = BeautifulSoup(browser.page_source, 'html5lib')
                find_save_img(nimg)
                next_button = find_nextbutton()


