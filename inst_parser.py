from selenium import webdriver
from bs4 import BeautifulSoup
from urllib.request import urlretrieve
from time import sleep
from utils import mkdir
import os
import argparse


def find_imgs(src_list):
    art = soup.findChildren("article")[0]
    for img in art.findChildren("img"):
        if "data-testid" not in img.attrs.keys():
            if "src" in img.attrs.keys():
                if img.attrs["src"] not in src_list:
                    src_list.append(img.attrs["src"])
    return src_list


def save_imgs(src_list):
    for nimg, src in enumerate(src_list):
        impath = os.path.join(path2save, "img-{}.jpg".format(nimg))
        urlretrieve(src, impath)


def find_videos():
    art = soup.findChildren("article")[0]
    if len(art.findChildren("video")):
        video_link_path = os.path.join(path2save, "video-link.txt")
        if not os.path.exists(video_link_path):
            with open(video_link_path, "w") as f:
                f.write("https://www.instagram.com/{}{}".format(parsed_user, plink))


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
# ----------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--working_login", required=True, help="Логин инстаграмм-аккаунта для входа в систему")
    parser.add_argument("--working_password", required=True, help="Пароль")
    parser.add_argument("--parsed_user", required=True, help="Логин инстаграмм-аккаунта, который нужно скопировать")
    parser.add_argument("--nscroll", required=False, default=1,
                        help="Сколько прокруток экрана сделать для чтения контента (умолч. 1)")
    parser.add_argument("--clear_folders", required=False, default="y", choices=["y", "n"],
                        help="Удалить все файлы перед новой работой (Да-y, Нет-n, умолч. Да)")
    parser.add_argument("--out_dir", required=False, default="./out", help="Путь для сохранения скачанных данных")

    args = vars(parser.parse_args())

    working_login = args["working_login"]
    working_password = args["working_password"]
    parsed_user = args["parsed_user"]
    n_scroll = args["nscroll"]
    clear_folders = True if args["clear_folders"] == "y" else False
    out_dir = args["out_dir"]

    mkdir("out", clear_dirs=clear_folders)
    mkdir("screens", clear_dirs=True)

    saved_posts = ["/p/{}/".format(d.split()[1]) for d in os.listdir(out_dir)]
    print("There are {} already parsed posts".format(len(saved_posts)))

    chromedriver = "resourses/chromedriver"
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
    sleep(4)
    browser.save_screenshot("./screens/init{:03.0f}.png".format(1))

    browser.get("https://www.instagram.com/{}".format(parsed_user))
    sleep(3)
    posts_links = set([])
    for i in range(n_scroll):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        sleep(2)
        browser.save_screenshot("./screens/scroll{:03.0f}.png".format(i))
        print("{} scroll...".format(i), end=" ")

        soup = BeautifulSoup(browser.page_source, 'html5lib')

        for div in soup.findChildren("div"):
            a = div.findChildren("a")
            if len(a):
                a = a[0].attrs["href"]
                if a.startswith("/p"):
                    if a not in saved_posts:
                        posts_links.add(a)

        print(len(posts_links), "new posts found")
    posts_links = list(posts_links)

    print("\nstart parsing {} posts\n-------------------------------------------".format(len(posts_links)))
    for npost, plink in enumerate(posts_links):
        print("post {:04.0f}/{:04.0f}".format(npost+1, len(posts_links)), end=" ")
        browser.get("https://www.instagram.com/{}{}".format(parsed_user, plink))
        sleep(1)
        browser.save_screenshot("./screens/post{:03.0f}.png".format(npost))

        soup = BeautifulSoup(browser.page_source, 'html5lib')

        time_stamp, story = find_time_and_story()
        if time_stamp is None:
            print("!!! broken post: {}".format(plink))
            continue

        path2save = os.path.join(out_dir, "{} {}".format(time_stamp, plink.replace("/p/", "").replace("/", "")))
        if mkdir(path2save, clear_dirs=clear_folders):
            with open(os.path.join(path2save, "story.txt"), "w") as f:
                f.write(story)

            src_list = find_imgs([])
            next_button = find_nextbutton()
            while next_button is not None:
                browser.find_elements_by_class_name(next_button.attrs["class"][0])[0].click()
                soup = BeautifulSoup(browser.page_source, 'html5lib')
                src_list = find_imgs(src_list)
                next_button = find_nextbutton()
            save_imgs(src_list)
            find_videos()
