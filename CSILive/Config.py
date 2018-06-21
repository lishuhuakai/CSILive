'''
    说明:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    这个文件中包含这整个项目的一些配置参数,你可以在这里修改.
'''

import numpy as np

# 一些常量的定义,请不要修改
#==========================================
triangle = np.array([1, 3, 6])
carriers = 30
#==========================================


# 下面是可配置的参数
#==========================================
# 每一个样本应当包含的数据包的个数
packetsPerGroup = 10000

# CSILive作为服务端,在(ip, port)地址进行监听
# ip要求是有效的ip地址字符串,port要求是有效的端口地址
ip = '127.0.0.1'
port = 8090

# 实时显示的间隔,单位是秒,0.1秒表示每0.1秒绘制一张图片
# 间隔的下限是0.05s,间隔太短可能会导致延迟的发生.
liveGap = 0.1
# 每一次训练时,采集样本的个数
numOfTrainSamples = 3
#===========================================

'''
    一些说明:
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    python的多线程其实是一个鸡肋,每个时刻最多只有一个线
    程在跑,不能充分利用cpu的资源.原本我以为利用QThread
    能够消除python的多线程鸡肋,但是事实证明,我错了,任何
    我的代码貌似用了四个线程,但是实际测试来看,某一时刻最
    多只有一个线程在跑,所以这不是真正意义上的多线程.
    所以为了处理的流畅性,我将采集的间隔降低了,每秒钟最多采集
    20张图片,这个和我之前做的每秒钟200张图片,差距确实很大,
    但是没有办法,我还要干别的事情呢,比如说训练,测试以及记录.
    这些事情如果堆在一起,然后采集的间隔小于0.05s,那么UI会
    非常卡.
    
    好吧,这个只是1.0版本,后续要继续做的话,必须考虑用多核来加快
    处理速度.
'''
