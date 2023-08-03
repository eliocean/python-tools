import re
import sys
import os
import you_get
import requests
from jsonpath import jsonpath
from pathlib import Path
from time import sleep
from logging import getLogger


logger = getLogger('eli_logger')
logger.setLevel(20) # 20 is INFO level

def youget_Download(url,outDir:str='./',time_delay=60):
    """使用you-get 一个个视频下载"""
    try:
        sys.argv = ['you-get', url.strip(), '--no-caption', '--auto-rename','-o',outDir]
        print(sys.argv)
        you_get.main() #使用you_get.main()可以在脚本运行时显示you-get的下载情况
        logger.info(f"[{url.strip()}]-[{outDir}]")
        sleep(time_delay) # 设置 time_delay ，避免网络封禁
    except Exception as e:
        print("下载异常，结束下载......",e)
        exit(-1)


def create_folder(folder_path):
    """创建文件夹"""
    try:
        os.makedirs(folder_path)
        print(f"文件夹 {folder_path} 创建成功！")
    except FileExistsError:
        print(f"文件夹 {folder_path} 已存在！")
    except Exception as e:
        print(f"创建文件夹时发生错误：{str(e)}")


def download_playlist(bvid:str='BV1AL4yxxxxx',parent:str='./'):
    """bilibili 播放列表下载"""
    pagelist_json = requests.get(f"https://api.bilibili.com/x/player/pagelist?bvid={bvid}&jsonp=jsonp").json()
    page_list = jsonpath(pagelist_json, "$.data..page")
    "title"
    videoTitle = jsonpath(requests.get(f'https://api.bilibili.com/x/web-interface/view?bvid={bvid}').json(),'$..name')[0]
    create_folder(f"{parent}/{videoTitle}") # 每个播放视频列表，归类一个文件夹
    for page in page_list:
        down_url = f'https://www.bilibili.com/video/{bvid}?p={page}'
        youget_Download(down_url,f"{parent}/{videoTitle}")


def download_series(series:tuple[int,int]=('1567748000', '358000'),parent:str='./'):
    """bilibili up主合集下载"""
    mid = series[0] # up主ID
    series_id = series[1] # up主合集ID
    base_url = "https://api.bilibili.com/x/series/archives?mid=1567748478&series_id=358497&only_normal=true&sort=asc&pn={}&ps=30"
    videoTitle = jsonpath(requests.get(f'https://api.bilibili.com/x/series/series?series_id={series_id}').json(),'$..name')[0]
    
    page_num = 0
    bvid_list = []
    while True:
        # 获取各视频，bvid
        page_num += 1
        json_data = requests.get(base_url.format(page_num)).json()
        bvids = jsonpath(json_data, "$..archives..bvid")
        bvid_list.extend(bvids)
        total = jsonpath(json_data, "$..page.total")[0]
        size = jsonpath(json_data, "$..page.size")[0]
        num = jsonpath(json_data, "$..page.num")[0]
        if total <= size * num:
            break # 结束条件
    
    for bvid in bvid_list:
        download_playlist(bvid=bvid,parent=f"{parent}/{videoTitle}") # 合集总结为一个文件夹




def main(filename):
    download_path = str(Path(sys.argv[0]).resolve().parent)

    # 播放列表： https://www.bilibili.com/video/BV1AL4y1Y7gu/?spm_id_from=333.999.0.0&vd_source=7c9638e0b1221cd415d0a259d7a88dc6
    regex_playlist = re.compile(r"\/video\/(\w+)\/\?")

    # up主合集：  https://space.bilibili.com/1567748478/channel/seriesdetail?sid=358497
    regex_series = re.compile(r"\/(\d+)\/.+sid=(\d+)")


    if not os.path.exists(filename):
        with open(filename, 'w') as _:
            print(f"文件 {filename} 不存在，已自动创建.")
    with open(filename,encoding="utf-8",mode="r") as fr:
        for line in fr:
            is_playlist = regex_playlist.findall(line) # 视频播放页url
            is_series = regex_series.findall(line) # up主合集url
            if not line: # 空行
                continue
            elif is_playlist:
                download_playlist(is_playlist[0],download_path)
                print("下载播放列表： " + line.strip())
            elif is_series:
                download_series(is_series[0],download_path)
                print("下载up主合集： " + line.strip())
            else:
                print("url解析失败，暂不支持： " + line.strip())


if __name__ == "__main__":
    urls_txt = str(Path(sys.argv[0]).resolve().parent) + "/url.txt"
    main(urls_txt)
