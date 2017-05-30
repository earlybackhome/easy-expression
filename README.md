# Easy-expression

## 简述
   *Easy-expression* 是一个基于文本的表情包联想插件，可以对网络上的表情包(有文字)进行文字区域提取和ＯＣＲ识别，将整理到的语句集成语句库。对输入语句进行模糊匹配，便可以得到与之对应的图片。
   
**除了对此项目有兴趣的开发者，对于其中的个别模块有需求的也可以将其clone下来作为一种尝试，所有模型和数据均在百度网盘上**

**开发者借用Github上的开源项目搭建了这个项目, 由衷地感谢提供支持的项目和作者**
## 依赖
* 在测试之前请安装好相关依赖
>
python3
opencv3+
sklearn
pyocr
tesseract-ocr
PIL
matplotlib
pyqt4
## 直接测试

1. 下载[链接](https://pan.baidu.com/s/1hs21ZzI)密码: 4fck
2. 将其中５个文件放到`Easy-expression/module/DL/`下
3. `cd ./easy-expression`
`python3 setup.py`

模块说明
---
### 文本提取
**此模型文本提取效率不高**

**单模块使用说明:**

1. 修改Image2txt.py中的Image_dir的目录路径（所有图片放在一个目录下）
2. 修改out的写入路径(这是将所有信息写入的路径)
3. 运行`python3   Image2txt.py`

### 文本相似度匹配

**使用模型语义资料来源于百度贴吧**

**部分代码参考[FAQrobot](https://github.com/ofooo/FAQrobot)**

**单模块使用说明:**

1. 下载[链接](https://pan.baidu.com/s/1hs21ZzI)密码: 4fck
2. 将其中５个文件放到`Easy-expression/module/DL/`下
3. 运行`python3 maxSim.py`
4. 根据提示输入一句话即可得到反馈

### 图形界面
* qt部分引用了[pyqtChat](https://github.com/HeLiangHIT/pyqtChat)
* 在此基础上将源码改为Python3，并增加了表情功能，支持表情收藏与删除。
* 发送的快捷键以及界面风格也做了一些修改

**主要功能**

1. groupUserList 类用于好友列表展示，模拟QQ好友界面。
2. msgList 类用于消息展示，模拟微信PC端消息界面，支持图片和文字显示。
3. flowlayout 类是pyqt的example里面的布局，就是依次布局按钮等控件时可能用到，自动调整位置。
4. exptable 类是表情窗口
5. pyqtChatApp 类是APP主界面。需在此修改代码最后的表情包路径

**使用说明**

