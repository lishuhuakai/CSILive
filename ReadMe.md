# 运行环境的搭建
程序由python书写而成，所以如果想运行程序的话，首先要安装python。为了避免各种各样复杂的包依赖，这里推荐一步到位，直接安装anaconda即可。

anaconda的安装包在官网可以下载到，如果速度太慢的话，可以到清华镜像站下载。地址如下[https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/](https://mirrors.tuna.tsinghua.edu.cn/anaconda/archive/)

环境搭建好之后，使用命令行进入`CSILive.py`所在路径，运行命令：
```shell
python CSILive.py
```
这个时候系统可能会提示你缺少了一个数据包，比如:
```shell
Traceback (most recent call last):
  File "CSILive.py", line 18, in <module>
    from Train import TrainCSI
  File "C:\Users\ASUS\Desktop\App\CSILive\Train.py", line 8, in <module>
    from keras.models import Sequential
ModuleNotFoundError: No module named 'keras'
```
没关系，我们直接安装`keras`这个包即可：
```shell
conda install keras
```
conda默认的软件源可能非常慢，为了加速，可以切换到清华的软件源，命令如下：
```shell
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --set show_channel_urls yes
```
具体的配置说明可能会有变动，不过可以参照这里[https://mirror.tuna.tsinghua.edu.cn/help/anaconda/](https://mirror.tuna.tsinghua.edu.cn/help/anaconda/)

软件跑起来应该没有什么问题。

# 中转程序的编译
在目录中有一个`log_to_server.c`文件，这个代码来自这里[https://github.com/lubingxian/Realtime-processing-for-csitool](https://github.com/lubingxian/Realtime-processing-for-csitool)，代码的编译需要linux 802.n csi tool工具的支持，具体可以参考这里：http://github.com/dhalperi/linux-80211n-csitool-supplementary

首先将源代码放入~/linux-80211n-csitool-supplementary/netlink目录之下，然后执行gcc来编译代码：
```shell
gcc log_to_server.c –o trans
```
在当前目录之下会生成trans程序，你可以将这个程序拷贝到任意一个目录。

# 程序原理
中转程序实时从内核中抽取出`CSI`，然后传递给`CSILive`，`CSILive`实时解析和显示这些数据。



