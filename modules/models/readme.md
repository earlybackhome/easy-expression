
# 图形界面
qt部分引用了 https://github.com/HeLiangHIT/pyqtChat
在此基础上将源码改为Python3，并增加了表情功能，支持表情收藏与删除。
发送的快捷键以及界面风格也做了一些修改

1.groupUserList 类用于好友列表展示，模拟QQ好友界面。

2.msgList 类用于消息展示，模拟微信PC端消息界面，支持图片和文字显示。

3.flowlayout 类是pyqt的example里面的布局，就是依次布局按钮等控件时可能用到，自动调整位置。

4.exptable 类是表情窗口

5.pyqtChatApp 类是APP主界面。需在此修改代码最后的表情包路径

