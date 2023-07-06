import json
import os.path

import requests
import jsonpath


def MakeUrlsWithPageNum(formatUrl, start: int, end: int):
    """
    根据页码制作格式化的链接
    :param start: 页码第一页
    :param end: 页码最后一页
    :return: 生成的链接列表
    """
    urls = []
    for i in range(start, end + 1):
        urlTmp = formatUrl.format(i)
        urls.append(urlTmp)

    return urls


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
    json_data = DownPage(url)
    # print(json.dumps(json_data))
    objUrls = jsonpath.jsonpath(json_data, "$..archives..bvid")
    return objUrls


def WriteToFile(fileName: str, objUrls: list):
    """
    将爬虫分析返回的结果保存到文件中
    :param UrlsList: 获取到的结果列表
    :return:None
    """

    with open(fileName, "a", encoding="utf-8") as fileOpen:
        for bvid in objUrls:
            objUrl = "https://www.bilibili.com/video/{}".format(bvid)
            fileOpen.write(objUrl + "\n")


def Engine(fileName, formatUrl, end: int, start=1):
    """
    爬虫引擎
    :return:
    """
    SUM = 0
    urls = MakeUrlsWithPageNum(formatUrl, start, end)
    if os.path.exists(fileName):
        os.remove(fileName)

    for url in urls:
        objUrls = ParseObjUrls(url)
        WriteToFile(fileName, objUrls)
        print("{}---成功！---获取记录条数: {}".format(url, len(objUrls)))
        SUM += len(objUrls)
    print("Finished! 总共获取记录条数：{}".format(SUM))


if __name__ == '__main__':
    # json api接口
    formatUrl = "https://api.bilibili.com/x/series/archives?mid=1567748478&series_id=358497&only_normal=true&sort=desc&pn={}&ps=30"
    fileName = "urls.txt"
    Engine(fileName, formatUrl, end=3)
