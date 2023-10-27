from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import os

def gen_avatar(PATH="", FILE="skin.png", SAVE="skin2.png", SIZE=360):
    if SIZE%72 != 0:
        print("`size` must be s multiple of 72")
        return

    skin = np.array(Image.open(os.path.join(PATH, FILE)))
    if skin.shape != (64,64,4):
        print("Mismatched skin size, should be (64,64,4) but `{}`".format(skin.shape))

    head_1 = skin[8:16,8:16,]
    head_2 = skin[8:16,40:48,]
    px_size = SIZE//9
    padding_size = px_size//2
    head_1 = np.pad(
        np.array([[[k.tolist()]*px_size for k in i]*px_size for i in head_1]
                ).reshape(px_size*8,px_size*8,4),((padding_size,padding_size),(padding_size,padding_size),(0,0)))
    head_2 = np.array([[[k.tolist()]*(SIZE//8) for k in i]*(SIZE//8) for i in head_2]).reshape(SIZE,SIZE,4)
    head_double = np.array([[int(sum(k==[0,0,0,0])==4)]*4 for i in head_2 for k in i]).reshape(SIZE,SIZE,4)*head_1+head_2
    plt.imshow(head_double)
    plt.axis('off')
    plt.show()

    img = Image.fromarray(np.uint8(head_double))
    path = os.path.join(PATH, SAVE)
    img.save(path)

    print("Saved at {}".format(path))
