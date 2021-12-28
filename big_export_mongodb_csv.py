#!/home/appadmin/python361/bin/python3
import pandas as pd
import sys
import datetime
import subprocess

"""
导出mongo数据库到csv文件,分隔符自己制定
"""

SEP_CHAR = '\001'
CHUNK_SIZE = 10000

"""校验参数,读取参数"""
if len(sys.argv) != 5:
    print('参数错误！',
          '''\n需要输入数据库,集合名,数据筛选条件,固定字段
          例如：mongo_add.py mongodb_name collection_name {} "col1,col2,col3"
          ''')
    sys.exit(-1)

IP = '127.0.0.1'
PORT = 12345
U_P = ['mogo_user', 'mongo_password']
DBNAME = sys.argv[1]
COLLECTION = sys.argv[2]
FILE_NAME = COLLECTION.lower() + ".csv"
QUERY_STR = sys.argv[3]
COLNUMS = sys.argv[4]


def run_shell(shell):
    """执行shell并随时打印输出"""
    cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                           stdout=sys.stdout, universal_newlines=True, shell=True, bufsize=1)

    cmd.communicate()
    return cmd.returncode


def export_mongo_to_file():
    """使用mongoexport命令导出到文件"""
    base_mongoexport_cmd = "mongoexport -h {ip}:{port} -u {u} -p {p} --db {db} --collection {collection} --type=csv --query='{query}'  --fields={fields} --out={out} --limit=20"
    # base_mongoexport_cmd = "mongoexport -h {ip}:{port} -u {u} -p {p} --db {db} --collection {collection} --type=csv --query='{query}'  --fields={fields} --out={out}"
    print('mongoexport:_开始时间：' + str(datetime.datetime.now()))

    mongoexport_cmd = base_mongoexport_cmd.format(
        ip=IP,
        port=PORT,
        u=U_P[0],
        p=U_P[1],
        db=DBNAME,
        collection=COLLECTION,
        query=QUERY_STR,
        fields=COLNUMS,
        out=FILE_NAME
    )

    print("执行命令:>", mongoexport_cmd)
    run_shell(mongoexport_cmd)
    print('mongoexport:_结束时间：{}\n'.format(str(datetime.datetime.now())))


def trans_file(filename=None):
    """使用pd批量转换csv文件"""
    print('转换csv文件:_开始时间：{}'.format(str(datetime.datetime.now())))
    df_chunk = pd.read_csv(filename, chunksize=CHUNK_SIZE, encoding="utf-8", iterator=True, quoting=0)
    # quoting=0(QUOTE_MINIMAL)读取选择读取双引号,默认就是quoting=0
    # 使用 chunksize 分块读取大型csv文件，这里每次读取 chunksize 为CHUNK_SIZE
    # QUOTE_ALL = 1
    # QUOTE_MINIMAL = 0
    # QUOTE_NONE = 3
    # QUOTE_NONNUMERIC = 2
    res_file = filename.rsplit(".")[0] + ".txt"
    Totle_lines = 0
    for chunk in df_chunk:
        Totle_lines += chunk.shape[0]
        print(Totle_lines)
        chunk.to_csv(res_file, header=None, index=None, na_rep='', sep=SEP_CHAR, quoting=3)
        # quoting=3(QUOTE_NONE) 保存时去除双引号

    print('转换csv文件:_结束时间：{}'.format(str(datetime.datetime.now())))
    print('_完成！_处理记录数：{}\n数据文件保存至>{}'.format(str(Totle_lines), res_file))


export_mongo_to_file()  # 使用mongoexport命令导出到文件
trans_file(FILE_NAME)
