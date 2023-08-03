import sys
import you_get
from pathlib import Path
from time import sleep

"""
特殊参数说明：
--playlist      下载播放列表中的所有视频
--no-caption    不下载弹幕文件
--auto-rename   自动重命名同名文件
"""

DELAY_TIME = 60 # 等待60s

def ReadUrlsFile(fileName):
    """
    获取链接列表
    :param fileName:链接保存文件
    :return:返回列表
    """
    urls = []
    with open(fileName, encoding="utf-8") as fileRead:
        for url in fileRead:
            urls.append(url)

    return urls


def DownUseYouGet(url):
    try:
        sys.argv = ['you-get', url.strip(), '--no-caption', '--auto-rename']
        print(sys.argv)
        you_get.main() #使用you_get.main()可以在脚本运行时显示you-get的下载情况
    except Exception as e:
        print("下载异常，结束下载......",e)
        exit(-1)


def Engine(fileName):
    urls = ReadUrlsFile(fileName)
    for url in urls:
        DownUseYouGet(url)
        print("完成第{}条记录---{}".format(urls.index(url) + 1, url))
        sleep(DELAY_TIME)
        
    print("Finished! Thanks!")


if __name__ == '__main__':
    fileName = str(Path(sys.argv[0]).resolve().parent) + "/urls.download"
    Engine(fileName)
