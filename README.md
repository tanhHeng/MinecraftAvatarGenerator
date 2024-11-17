# MinecraftAvatarGenerator

一个使用 Python 编写的 Minecraft 双层皮肤头像生成器。支持从玩家名称获取在线皮肤，也支持从本地文件生成头像。

## ✨ 特性

- 支持在线获取玩家皮肤并生成头像
- 支持从本地皮肤文件生成头像
- 支持批量处理多个玩家或文件
- 支持自定义输出目录
- 完整支持双层皮肤
- 支持 alpha 通道（透明度）

## 🚀 使用方法

### 在线获取玩家皮肤
```bash
# 单个玩家
python avgen.py -n player_name

# 多个玩家
python avgen.py -n player1,player2,player3
```

### 从本地文件生成
```bash
# 从单个皮肤文件生成
python avgen.py -f path/to/skin.png

# 从目录批量生成
python avgen.py -d path/to/skins/directory
```

### 自定义输出目录
```bash
python avgen.py -n player_name -o custom_output_dir
```

### 命令参数说明
- `-n, --names`: 玩家名称（多个玩家用逗号分隔）
- `-f, --file`: 单个皮肤文件路径
- `-d, --dir`: 皮肤文件目录路径
- `-o, --output`: 输出目录路径（默认为 "avatar"）

## 📦 依赖

```bash
pip install numpy matplotlib requests
```

## 🛠️ 从源码编译

如果你想编译成可执行文件：
```bash
# 安装编译工具
pip install nuitka

# 编译
python -m nuitka --lto=no --jobs=<job_count> --onefile avgen.py
```

## 🔗 API 来源

- `mcuuid.net`: 用于获取玩家 UUID
- `crafatar.com`: 用于获取玩家皮肤

## 📸 效果展示

![示例头像](skin2.png)

## ⚠️ 注意事项

- 使用玩家名称时，请确保名称之间的逗号没有空格
- 确保有稳定的网络连接以获取在线皮肤
- 本地皮肤文件必须是有效的 Minecraft 皮肤格式
