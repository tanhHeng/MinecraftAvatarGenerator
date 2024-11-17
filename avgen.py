import numpy as np
import requests
import re
import argparse
from io import BytesIO
import asyncio
import os
from matplotlib import pyplot as plt
import sys

async def get_uuid(player_name):
    try:
        print(f"\r  [step 1/3] Getting uuid for player {player_name}...", end="")
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'}
        uuid_rep = await loop.run_in_executor(None, lambda: requests.get(f"https://mcuuid.net/?q={player_name}", headers=headers))
        uuid_rep.raise_for_status()
        uuid_match = re.search('<input id="results_raw_id".+?value="(.+?)">', uuid_rep.text)
        if uuid_match:
            uuid = uuid_match.groups()[0]
        else:
            print(f"\r  * Player {player_name} not found.")
            return None, None
        print(f"\r  [step 2/3] Getting skin for player {player_name}...", end="")
        skin_rep = await loop.run_in_executor(None, lambda: requests.get(f"https://crafatar.com/skins/{uuid}"))
        skin_rep.raise_for_status()
        print(f"\r  [step 3/3] Saving skin for player {player_name}...", end="")
        return player_name, BytesIO(skin_rep.content)
    except requests.RequestException as e:
        print(f"\r  * Error when getting data for player {player_name}: {e}")
        return None, None
    except Exception as e:
        print(f"\r  * Error: {e}")
        return None, None

def img_array_zoom(array, scaling):
    return np.kron(array, np.ones((scaling, scaling, 1)))

def avatar_generate(skin, size=360):
    if skin is None:
        return None

    if size % 72 != 0:
        raise ValueError("`size` must be a multiple of 72, but `%s`" % size)

    shape = skin.shape
    if len(shape) != 3 or shape[0] not in [32, 64] or shape[1] != 64 or shape[2] not in [3, 4]:
        raise ValueError("Mismatched skin size `%s`" % shape)

    alpha_flag = shape[2] == 3

    avatar_bottom = skin[8:16, 8:16]
    avatar_top = skin[8:16, 40:48]

    pixel_multi = size // 9
    pixel_padding = pixel_multi // 2

    avatar_bottom = np.pad(img_array_zoom(avatar_bottom, pixel_multi), ((pixel_padding, pixel_padding), (pixel_padding, pixel_padding), (0, 0)))
    avatar_top = img_array_zoom(avatar_top, size // 8)

    if alpha_flag:
        alpha_final = alpha_bottom = alpha_top = np.ones((size, size, 1))
    else:
        alpha_bottom = avatar_bottom[:, :, 3].reshape(size, size, 1)
        alpha_top = avatar_top[:, :, 3].reshape(size, size, 1)
        alpha_final = alpha_top + alpha_bottom * (255 - alpha_top) / 255

    alpha_bottom, alpha_top = np.tile(alpha_bottom / 255, 3), np.tile(alpha_top / 255, 3)
    color = np.nan_to_num(avatar_top[:, :, :3] * alpha_top + avatar_bottom[:, :, :3] * alpha_bottom * (1 - alpha_top) / np.tile(alpha_final / 255, 3), 0)

    avatar_new = np.zeros((size, size, 4))
    avatar_new[:, :, :3] = color
    avatar_new[:, :, 3] = alpha_final.reshape(size, size)
    avatar_new = np.uint8(avatar_new)

    return avatar_new

async def save_avatar(player_name_skin_bytes, output_dir="avatar"):
    player_name, skin_bytes = player_name_skin_bytes
    if skin_bytes:
        print(f"  [Loading] Generating avatar for player {player_name}...", end="")
        skin = plt.imread(skin_bytes) * 255
        avatar = avatar_generate(skin)
        if avatar is None:
            print(f"\r  * Error generating avatar for player {player_name}.")
            return

        try:
            os.makedirs(output_dir, exist_ok=True)
            file = os.path.join(output_dir, f"{player_name}.png")
            plt.imsave(file, avatar)
            print(f"\r  [Finish] Player {player_name}'s avatar is now saved at {file}.")
        except OSError as e:
            print(f"\r  * Error saving avatar for player {player_name}: {e}")

async def load_local_skin(file_path):
    """从本地文件加载皮肤"""
    try:
        print(f"\r  [Loading] Reading skin from {file_path}...", end="")
        player_name = os.path.splitext(os.path.basename(file_path))[0]
        with open(file_path, 'rb') as f:
            return player_name, BytesIO(f.read())
    except Exception as e:
        print(f"\r  * Error reading skin file {file_path}: {e}")
        return None, None

async def main():
    np.seterr(divide='ignore', invalid='ignore')

    parser = argparse.ArgumentParser(
        description='从Minecraft玩家名或本地皮肤文件生成头像',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  %(prog)s -n player1,player2,player3     # 从多个玩家名生成头像
  %(prog)s -d skins/                      # 从皮肤文件夹生成头像
  %(prog)s -f skin.png                    # 从单个皮肤文件生成头像
  %(prog)s -n player1 -o custom_avatars/  # 指定输出目录
        '''
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-n', '--names', type=str,
                      help='Minecraft玩家名列表，用逗号分隔')
    group.add_argument('-d', '--dir', type=str,
                      help='包含皮肤文件的目录路径')
    group.add_argument('-f', '--file', type=str,
                      help='单个皮肤文件路径')
    parser.add_argument('-o', '--output', type=str, default="avatar",
                      help='头像输出目录 (默认: avatar)')
    args = parser.parse_args()

    try:
        if args.names:
            if not args.names.strip():
                parser.error("玩家名不能为空")
            player_names = [name.strip() for name in args.names.split(',') if name.strip()]
            if not player_names:
                parser.error("请提供有效的玩家名")
            tasks = [get_uuid(player_name) for player_name in player_names]
            results = await asyncio.gather(*tasks)
        elif args.dir:
            if not os.path.isdir(args.dir):
                parser.error(f"目录不存在: {args.dir}")
            skin_files = [f for f in os.listdir(args.dir) if f.lower().endswith('.png')]
            if not skin_files:
                parser.error(f"在 {args.dir} 中没有找到PNG文件")
            tasks = [load_local_skin(os.path.join(args.dir, f)) for f in skin_files]
            results = await asyncio.gather(*tasks)
        else:  # args.file
            if not os.path.isfile(args.file):
                parser.error(f"文件不存在: {args.file}")
            if not args.file.lower().endswith('.png'):
                parser.error(f"文件必须是PNG格式: {args.file}")
            results = [await load_local_skin(args.file)]

        # 验证输出目录
        if os.path.exists(args.output) and not os.path.isdir(args.output):
            parser.error(f"输出路径已存在且不是目录: {args.output}")

        for result in results:
            await save_avatar(result, args.output)

    except KeyboardInterrupt:
        print("\n程序被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n发生错误: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
