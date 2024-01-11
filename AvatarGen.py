import numpy as np
from matplotlib import pyplot as plt
import os, requests, re

def save_player_skin(player_name: str, path="skin", filename="%player_name%.png"):
    try:
        print("\r  [step 1/3] Getting uuid...",end="")
        flag = 0
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}
        uuid_rep = requests.get("https://mcuuid.net/?q=%s"%player_name, headers=headers)
        re_result = re.search('<input id="results_raw_id".+?value="(.+?)">', uuid_rep.text)
        if not re_result:
            print("\r[WARN] Player %s does not exist."%player_name)
            return
        uuid = re_result.groups()[0]
        print("\r  [step 2/3] Getting skin...",end="")
        flag = 1
        skin_rep = requests.get("https://crafatar.com/skins/%s"%uuid)
        print("\r  [step 3/3] Saving skin...",end="")
        flag = 2
        if not os.path.isdir(path):
            os.makedirs(path)
        filename = filename.replace("%player_name%", player_name)
        file = os.path.join(path, filename)
        with open(file, "wb+") as f:
            f.write(skin_rep.content)
            f.close()
        print("\r  [Finish] Player %s's skin is now saved at %s."%(player_name, file))
        return file
    except Exception as e:
        print("\r  * Error when %s : %s"%(["getting uuid", "getting skin", "saving skin"][flag], e))

def img_array_zoom(array: np.array, scaling: int) -> np.array:
    array = np.array(
                [[[k.tolist()]*scaling for k in i]*scaling for i in array]
            ).reshape(scaling*8, scaling*8, 4)
    return array

def avatar_generate(skin: np.array, size: int = 360) -> np.array:

    if size%72 != 0:
        raise AttributeError("`size` must be a multiple of 72, but `%s`"%size)
    
    shape = skin.shape
    if len(shape) != 3 or shape[0] not in [32, 64] or shape[1] != 64 or shape[2] not in [3,4]:
        raise AttributeError("Mismatched skin size `%s`"%shape)
    
    if shape[2] == 3:
        alpha_flag = True
    else:
        alpha_flag = False
    
    # split
    avatar_bottom = skin[8:16, 8:16, ]
    avatar_top = skin[8:16, 40:48, ]

    # img zoom
    pixel_multi = size//9
    pixel_padding = pixel_multi//2

    avatar_bottom = np.pad(
        array = img_array_zoom(avatar_bottom, pixel_multi),
        pad_width = ((pixel_padding, pixel_padding), (pixel_padding, pixel_padding), (0,0))
    )
    avatar_top = img_array_zoom(avatar_top, size//8)

    # calc alpha
    if alpha_flag:
        alpha_final = alpha_bottom = alpha_top = np.zeros((size, size, 1)) + 1
    else:
        alpha_bottom = avatar_bottom[:, :, 3].reshape(size, size, 1)
        alpha_top = avatar_top[:, :, 3].reshape(size, size, 1)
        alpha_final = alpha_top + alpha_bottom*(255-alpha_top)/255
    
    # apply alpha
    alpha_bottom, alpha_top = np.tile(alpha_bottom/255, 3), np.tile(alpha_top/255, 3)
    color = np.nan_to_num(
        avatar_top[:,:,:3]*alpha_top + avatar_bottom[:,:,:3]*alpha_bottom*(1-alpha_top)/np.tile(alpha_final/255, 3),
        0
    )
    avatar_new = np.zeros((size, size, 4))
    avatar_new[:, :, :3] = color
    avatar_new[:, :, 3] = alpha_final.reshape(size, size)
    avatar_new = np.uint8(avatar_new)

    return avatar_new

def main():
    save_path = "avatar"
    np.seterr(divide='ignore', invalid='ignore')
    print("[x] To exit, press <ENTER> directly when entering player name.")
    try:
        while True:
            player_name = input("Enter player name >>> ")
            if player_name == "":
                break
            file = save_player_skin(player_name)
            if file:
                print("  [Loading] Generating avatar...", end="")
                skin = plt.imread(file)*255
                avatar = avatar_generate(skin)
                plt.imshow(avatar)
                plt.axis("off")
                plt.show()
                if not os.path.isdir("avatar"):
                    os.makedirs("avatar")
                file = os.path.join(save_path, "%s.png"%player_name)
                plt.imsave(file, avatar)
                print("\r  [Finish] Player %s's avatar is now saved at %s."%(player_name, file))
    except Exception as e:
        print("[ERROR] %s"%e)
        input("Press <ENTER> to exit >>> ")

if __name__ == "__main__":
    main()