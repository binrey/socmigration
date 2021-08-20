import vk_api as vk
from vk_api.upload import VkUpload
from os.path import join
from os import listdir
from utils import date2unix
from time import sleep


def upload_photos(files):
    attachment = []
    for file in files:
        if file.split(".")[-1] == "mp4":
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
    return vk_session.method('wall.post', method_dict)
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":

    data_dir = "out"
    start_date = "20/08/2021 19:15"
    start_post_num = 0
    user_login = "+79251751046"
    user_password = "contact120461"

    posts_list = sorted(listdir(data_dir))

    vk_session = vk.VkApi(user_login, user_password)
    vk_session.auth()

    vk_api = vk_session.get_api()
    upload = VkUpload(vk_api)

    for n, post in enumerate(posts_list[start_post_num:]):
        with open(join(data_dir, post, "story.txt")) as f:
            post_story = f.read()
            post_story += " #соцмиграция"

        impath = join(data_dir, post)
        images = [join(impath, p) for p in listdir(impath) if "txt" not in p]
        if start_date is not None:
            post_time = date2unix(start_date) + int(60*n)
        resp = send_post(post_story, upload_photos(images), post_time)
        print("post {:04.0f} {} uploaded: {}".format(n+start_post_num, post, resp))

        sleep(5)
