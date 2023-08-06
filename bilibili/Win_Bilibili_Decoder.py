"""
windows 桌面版 Bilibili 下载的视频缓存文件解析
参考：https://github.com/TeggySkye/BilibiliDenamer-win
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from numpy import fromfile, uint8


DELETE_TMP_FILE = False # 是否删除解密中间文件
DOWNLOAD_DIR = Path(sys.argv[0]).resolve().parent  # bili缓存路径，默认脚本文件所在路径


TMP_VIDEO_FILE = "video.m4s.tmp"
TMP_AUDIO_FILE = "audio.m4s.tmp"

def create_folder(folder_path):
    """创建文件夹"""
    try:
        os.makedirs(folder_path)
        print(f"创建文件夹 {folder_path}")
    except FileExistsError:
        pass
        # print(f"文件夹 {folder_path} 已存在！")
    except Exception as e:
        print(f"创建文件夹时发生错误：{str(e)}")


def run_shell(shell):
    """执行shell并不打印正常输出"""
    print("执行命令：",shell)
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=subprocess.DEVNULL, close_fds=True,
                           stdout=subprocess.DEVNULL, universal_newlines=True, shell=True, bufsize=1)

    cmd.communicate()
    return cmd.returncode


def ffmpeg_mp4(file1, file2,outfile,del_tmp=DELETE_TMP_FILE):
    """使用ffmpeg合并m4s文件"""
    try:
        create_folder(os.path.dirname(outfile)) # 创建文件夹
        # 执行命令并等待其完成
        shell_argv = ['ffmpeg', '-i',f'"{file1}"', '-i',f'"{file2}"','-c','copy',f'"{outfile}"']
        returncode = run_shell(" ".join(shell_argv))
        if returncode == 0:
            print("生成文件：",outfile)
        else:
            print("文件生成失败： ",outfile)
    except:
        print(f'{outfile} 合并失败。')
    if del_tmp:
        try:
            os.remove(file1)
            os.remove(file2)
            print(f'删除缓存文件：{file1},{file2}')
        except:
            print('缓存文件删除失败！')

"""遍历文件"""
for f_path, dir_name, f_names in os.walk(DOWNLOAD_DIR):
    print("当前路径:", f_path)
    # print(dir_name) # 当前路径下文件夹列表
    # print(f_names)  # 当前路径下文件列表

    if TMP_AUDIO_FILE in f_names and TMP_VIDEO_FILE in f_names:
        # print("发现已解密m4s临时文件：",os.path.join(f_path,TMP_AUDIO_FILE))
        # print("发现已解密m4s临时文件：",os.path.join(f_path,TMP_VIDEO_FILE))
        pass
    else: # 解密m4s文件
        for filename in f_names: # 遍历解析文件
            if filename.endswith(".m4s") :
                '''解密操作'''
                try:
                    file_stream = fromfile(os.path.join(f_path,filename), dtype=uint8)
                    if file_stream[317:318] == 2: # 2 是video
                        file_stream[9:].tofile(os.path.join(f_path,TMP_VIDEO_FILE))
                    elif file_stream[317:318] == 1:
                        file_stream[9:].tofile(os.path.join(f_path,TMP_AUDIO_FILE))
                    else:
                        print("未知类型m4s文件：",)
                except Exception as e:
                    print(e)
    
    if os.path.exists(os.path.join(f_path,TMP_AUDIO_FILE)) and os.path.exists(os.path.join(f_path,TMP_VIDEO_FILE)):
        try:
            with open(os.path.join(f_path,".videoInfo"), "r") as fr:
                json_read = json.load(fr)
            groupTitle = json_read.get("groupTitle").replace("/"," ").strip()
            tabName = json_read.get("tabName")
            out_filename = os.path.join(DOWNLOAD_DIR,f"{groupTitle}/{tabName}.mp4")
            if os.path.exists(out_filename):
                print("已存在mp4文件，如要重新生成，请删除文件：",out_filename)
            else:
                ffmpeg_mp4(os.path.join(f_path,TMP_VIDEO_FILE),
                        os.path.join(f_path,TMP_AUDIO_FILE),
                        out_filename)
        except Exception as e:
            print(e)

    

