# MinecraftAvatatGenerator
一个python编写的简易Minecraft双层皮肤的图像生成器

主函数位于`method.py`，可直接复制源码或`import`使用

~~绝对不是因为不想写命令行~~

## 参数

`PATH: string = ""` - 存储皮肤文件和保存生成文件的路径，默认为同级目录

`FILE: string = "skin.png"` - 皮肤文件名称，皮肤文件应当是一个Minecraft中使用的`.png`格式的`64x64`大小的图片，具有RGB通道和Alpha（透明）通道

`SAVE: string = "skin2.png"` - 生成文件的存储名称

`SIZE: int = 360` - 生成图片的大小，应当是`72`的倍数

## 样例

![image](skin2.png)
