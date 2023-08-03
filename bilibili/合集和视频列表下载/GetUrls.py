import sys
import os.path
from pathlib import Path
import requests
import jsonpath


def DownPage(url):
    """
    下载url对应的页面
    :param url:
    :return:
    """
    user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
    headers = {'User-Agent': user_agent}
    page = requests.get(url, headers=headers)  # 下载页面
    return page.json()


def ParseObjUrls(url: str):
    """
    根据传入的一个页面链接，分析此页面上所有的目标链接，返回爬虫结果列表
    :param url: 需要分析的页面链接
    :return: 获取到的结果链接列表
    """

    return bvids


def formatUrlToFile(fileName: str, bvids: list):
    """
    将爬虫分析返回的结果保存到文件中
    :param bvids: 获取到的结果列表bvids
    :return:None
    """

    with open(fileName, "w", encoding="utf-8") as fileOpen:
        for bvid in bvids:
            objUrl = "https://www.bilibili.com/video/{}".format(bvid)
            fileOpen.write(objUrl + "\n")


def Engine(fileName, mid, series_id):
    """
    爬虫引擎
    :return:
    """

    formatUrl = "https://api.bilibili.com/x/series/archives"
    formatUrl += "?mid=" + str(mid)
    formatUrl += "&series_id=" + str(series_id)
    formatUrl += "&only_normal=true&sort=asc&pn={}&ps=30"
    print(formatUrl)


    if os.path.exists(fileName):
        os.remove(fileName)

    page_num = 0
    bvid_list = []
    while True:
        page_num += 1
        json_data = DownPage(formatUrl.format(page_num))
        bvids = jsonpath.jsonpath(json_data, "$..archives..bvid")
        bvid_list.extend(bvids)
        total = jsonpath.jsonpath(json_data, "$..page.total")[0]
        size = jsonpath.jsonpath(json_data, "$..page.size")[0]
        num = jsonpath.jsonpath(json_data, "$..page.num")[0]
        if total <= size * num:
            break # 结束条件

    formatUrlToFile(fileName, bvid_list)
    print("Finished! 总共获取记录条数：{}".format(len(bvid_list)))


if __name__ == '__main__':
    mid = 1567748478 # up主ID
    series_id = 358497 # 合集和列表ID
    fileName = str(Path(sys.argv[0]).resolve().parent) + "/urls.download"
    Engine(fileName, mid,series_id)
