import vk_api as vk
from vk_api.upload import VkUpload
import os
from os.path import join


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

def send_post(message, attachment):
    with vk.VkRequestsPool(vk_session) as pool:
        wall = pool.method('wall.post', {"message": message,
                                         "attachment": attachment,
                                         "friends_only": 1,
                                         "mute_notifications": 1,
                                         "publish_date": 1630454399})
    return wall
# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":

    data_dir = "out"
    #my_app_id = "7930899"
    user_login = "+79251751046"
    user_password = "contact120461"

    posts_list = sorted(os.listdir(data_dir))



    vk_session = vk.VkApi(user_login, user_password)
    vk_session.auth()

    vk_api = vk_session.get_api()
    upload = VkUpload(vk_api)

    npost = 180

    with open(join(data_dir, posts_list[npost], "story.txt")) as f:
        post_story = f.read()

    impath = join(data_dir, posts_list[npost])
    images = [join(impath, p) for p in os.listdir(impath) if "txt" not in p]

    resp = send_post(post_story, upload_photos(images))
    print(resp)

    #with vk.VkRequestsPool(vk_session) as pool:
    #    wall = pool.method('wall.post', {"message": "puk"})
    #print(wall)