import vk_api as vk
from vk_api.upload import VkUpload
from os.path import join
from os import listdir
from utils import date2unix
from time import sleep
import argparse


def upload_photos(files):
    attachment = []
    for file in files:
        ext = file.split(".")[-1]
        if ext.lower() in ["mp4", "mov", "avi", "mpeg"]:
            response = upload.video(file)
            file_id = response['video_id']
            file_type = "video"
        else:
            response = upload.photo_wall(file)[0]
            file_id = response['id']
            file_type = "photo"

        owner_id = response['owner_id']
        access_key = response['access_key']
        attachment.append(f"{file_type}{owner_id}_{file_id}_{access_key}")
    attachment = ",".join(attachment)
    return attachment


def send_post(message, attachment, post_time=None):
    method_dict = {"message": message,
                   "attachment": attachment,
                   "friends_only": 1,
                   "mute_notifications": 1}
    if post_time is not None:
        method_dict.update({"publish_date": post_time})
    for attempt in range(1, 11):
        try:
            resp = vk_session.method('wall.post', method_dict)
            return resp
        except Exception as e:
            print(f"!!! attempt {attempt} error ({e})... waiting for 120 seconds and try again")
            sleep(120)
    return False
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", required=True, help="Путь к папкам, содержащим посты и их ресурсы")
    parser.add_argument("--start_date", required=False, default=None,
                        help="Дата первого отложенного поста в формате 01/01/2020 17:15 (время по гринвичу!). " +
                             "Остальные посты будут публиковаться с интервалом в минуту после первого" +
                             " (умолч. пост публикуется сразу)")
    parser.add_argument("--start_post_num", default=0, required=False,
                        help="С какой папки по счёту начать публикацию (умолч. 0)." +
                             " Полезно для продолжения прерванной загрузки")
    parser.add_argument("--user_login", required=True, help="Логин")
    parser.add_argument("--user_password", required=True, help="Пароль")

    args = vars(parser.parse_args())

    data_dir = args["data_dir"]
    start_date = args["start_date"]
    start_post_num = args["start_post_num"]
    user_login = args["user_login"]
    user_password = args["user_password"]

    posts_list = sorted(listdir(data_dir))

    vk_session = vk.VkApi(user_login, user_password)
    vk_session.auth()

    vk_api = vk_session.get_api()
    upload = VkUpload(vk_api)

    for n, post in enumerate(posts_list[start_post_num:1]):
        with open(join(data_dir, post, "story.txt")) as f:
            post_story = f.read()
            post_story += " #by_socmigration"
        impath = join(data_dir, post)
        images = [join(impath, p) for p in listdir(impath) if "txt" not in p]
        post_time = date2unix(start_date) + int(60*n) if start_date is not None else None

        resp = send_post(post_story, upload_photos(images), post_time)
        if resp:
            print("post {:04.0f} {} uploaded: {}".format(n+start_post_num, post, resp))
            sleep(7)
        else:
            print("!!! No response from sended request after 10 attempts")
            break