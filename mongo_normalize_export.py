#!/home/appadmin/python361/bin/python3
"""
# 展平json数据，输出文件
./mongo_normalize_export.py --collection='jobs' --filepath='/data/dt/' \
--conn=ABC --limit=500 \
--columns='{"jobs":["_id", "_class", "col1", "col2"]}'
"""



import ast
import datetime
import json
import sys
from copy import deepcopy
import subprocess
import pandas as pd
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import CursorNotFound
import os
import argparse

"""
注意，MongoReader的query条件转化为可支持 mongoexport 格式的$date数据类型
qstr = '{"predict_time":{"$gte" :{ "$date": "2019-09-25T00:00:00.000Z" } ,"$lte": { "$date": "2019-09-28T00:00:00.000Z" }}}'
"""


class MongoReader():
    """
    按查询条件分批次读取mongodb数据
    """

    def __init__(self, conn, collectionName: str, **kwargs):
        """
        :param conn: str | dict
        :param collectionName:
        :param kwargs:
        """
        self.read_config = {}
        self.read_config['mechanism'] = 'SCRAM-SHA-1'  # 身份验证方式 [默认SCRAM-SHA-1]
        self.read_config['query'] = self.__fmt_query(kwargs.get('query', {}))  # 数据查询条件 [默认全部]
        self.read_config['batch'] = kwargs.get('batch', 30000)  # 分批次读取数据，一次处理的数据量 [默认3W]
        self.read_config['limit'] = kwargs.get('limit', None)  # int 数据量解析限制，只处理limit条数据 [默认无限制]
        self.read_config['columns'] = kwargs.get('columns', None)  # mongo导出数据字段 [默认全部]
        self.read_config.update(kwargs)
        # 接下来连接db
        conndict = self.__fmt_conn(conn)
        self.read_config['conn'] = conndict  # 连接配置信息，账号密码等
        try:
            cliect = MongoClient(host=conndict.get('ip'), port=conndict.get('port'))
            database = cliect.get_database(conndict.get('dbname'))
            database.authenticate(conndict.get('username'),
                                  conndict.get('password'),
                                  mechanism=self.read_config.get('mechanism'))
            self.read_config['cliect'] = cliect  # MongoClient
            self.read_config['database'] = database  # DatabaseName
            self.read_config['collection'] = collectionName  # CollectionName
        except Exception as e:
            print("Mongodb数据库连接失败，错误信息:\n", e)

    def __del__(self):
        cliect: MongoClient = self.read_config.get('cliect', None)
        if cliect:
            cliect.close()

    def __fmt_conn(self, conn):
        if isinstance(conn, str):
            conndict = {}
            conndict['ip'] = conn.split(':')[0].replace('mongo', '').strip()
            conndict['port'] = int(conn.split(':')[1].split('/')[0].strip())
            conndict['dbname'] = conn.split('/')[1].split('-u')[0].strip()
            conndict['username'] = conn.split('-u')[1].split('-p')[0].strip()
            conndict['password'] = conn.split('-u')[1].split('-p')[1].strip()
        elif isinstance(conn, dict):
            conndict = conn
        else:
            print("非法conn")
            return None
        return conndict

    def __fmt_query(self, x):
        """
        json 字符串中的函数解析为python 对象
        qstr = '{"predict_time":{"$gte" :{ "$date": "2019-09-25T00:00:00.000Z" } ,"$lte": { "$date": "2019-09-28T00:00:00.000Z" }}}'
        :param x: json_dict
        :return:json_dict ,函数字符串转换对象
        """
        if isinstance(x, dict):  # 解决datetime,bool数据类型
            for k in x.keys():
                if k == "$date":
                    ts = x[k]  # {"$gte" :{ "$date": "2019-09-25T00:00:00.000Z" } }
                    x = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S.000Z")
                else:
                    x[k] = self.__fmt_query(x[k])
        elif isinstance(x, list):
            for k in range(len(x)):
                x[k] = self.__fmt_query(x[k])

        return x

    def get_cnt(self):
        query_dict = self.read_config.get('query', {})
        collectionClient: Collection = self.get_collection_cliect()
        maxLineNum = collectionClient.find(query_dict).count()
        print("查询[{}]，总记录数:{}".format(str(collectionClient.full_name), maxLineNum))
        return maxLineNum

    def get_collection_cliect(self, **config):
        """
        切换collection
        :param collectionName:
        :param config:
        :return:
        """
        self.read_config.update(config)
        database: Database = self.read_config.get('database', None)
        collectionClient: Collection = database.get_collection(self.read_config.get('collection'))
        return collectionClient

    def __iter__(self) -> list:
        query_dict = self.read_config.get('query', {})
        limit = self.read_config.get('limit', None)
        batchSize = self.read_config.get('batch', None)
        columns = self.read_config.get('columns', None)
        # 从mongodb collection 读取数据
        maxLineNum = self.get_cnt()
        if limit:  # 如果指定了limit,就只导出limit数据
            maxLineNum = min(limit, maxLineNum)
        batchSize = min(maxLineNum, batchSize)
        if batchSize <= 0:
            print("数据为空，程序结束.")
            exit(0)
        print("待读取记录数:{},需要读取批次:{},一次读取:{}".format(maxLineNum, ((maxLineNum - 1) // batchSize + 1),
                                                                   batchSize))

        skip_line_num: int = 0
        while skip_line_num < maxLineNum:
            collectionClient: Collection = self.get_collection_cliect()
            batch_data = collectionClient.find(query_dict, columns).skip(skip_line_num).limit(batchSize)
            df_json_data = list(batch_data)
            yield df_json_data
            skip_line_num += batchSize


class MongoExporter():
    """
    按查询条件分批次导出mongodb数据到文件
    """

    def __init__(self, conn, collectionName: str, filename: str, **kwargs):
        """
        :param conn: str | dict
        :param collectionName:
        :param kwargs:
        """
        self.exp_config = {}
        self.exp_config['mechanism'] = 'SCRAM-SHA-1'  # 身份验证方式 [默认SCRAM-SHA-1]
        self.exp_config['query'] = kwargs.get('query', {})  # 数据查询条件 [默认全部]
        self.exp_config['limit'] = kwargs.get('limit', None)  # int 数据量解析限制，只处理limit条数据 [默认无限制]
        self.exp_config['collection'] = collectionName  # 表名/集合名词
        self.exp_config['filename'] = filename  # 文件路径
        self.exp_config['columns'] = kwargs.get('columns', None)  # 导出字段
        self.exp_config.update(kwargs)
        # 接下来连接db
        conndict = self.__fmt_conn(conn)
        self.exp_config['conn'] = conndict  # 连接配置信息，账号密码等

    def __fmt_conn(self, conn):
        if isinstance(conn, str):
            conndict = {}
            conndict['ip'] = conn.split(':')[0].replace('mongo', '').strip()
            conndict['port'] = int(conn.split(':')[1].split('/')[0].strip())
            conndict['dbname'] = conn.split('/')[1].split('-u')[0].strip()
            conndict['username'] = conn.split('-u')[1].split('-p')[0].strip()
            conndict['password'] = conn.split('-u')[1].split('-p')[1].strip()
        elif isinstance(conn, dict):
            conndict = conn
        else:
            print("非法conn")
            return None
        return conndict

    def __run_shell(self, shell):
        """执行shell并随时打印输出"""
        cmd = subprocess.Popen(shell, stdin=subprocess.PIPE, stderr=sys.stderr, close_fds=True,
                               stdout=sys.stdout, universal_newlines=True, shell=True, bufsize=1)

        cmd.communicate()
        return cmd.returncode

    def export_json(self):
        query_dict = self.exp_config.get('query', {})
        limit = self.exp_config.get('limit', None)
        collectionName = self.exp_config.get('collection')
        conndict = self.exp_config.get('conn', None)
        columns = self.exp_config.get('columns', None)
        # MongoReader的__fmt_query 改变了 query_dict，所以必须使用深拷贝
        tmpMongoReader = MongoReader(conn=conndict, collectionName=collectionName, query=deepcopy(query_dict))
        maxLineNum = tmpMongoReader.get_cnt()

        filename = self.exp_config.get('filename', collectionName)
        if os.path.exists(filename):
            os.remove(filename)  # 删除文件，以便输入新文件
        mongoexport_cmd = "mongoexport -h"
        mongoexport_cmd += " {ip}:{port}".format(ip=conndict.get('ip'), port=conndict.get('port'))
        mongoexport_cmd += " -u {u} -p {p}".format(u=conndict.get('username'), p=conndict.get('password'))
        mongoexport_cmd += " --db {db} --collection {collection}".format(db=conndict.get('dbname'),
                                                                         collection=collectionName)
        mongoexport_cmd += " --type=json --query='{query}'".format(query=json.dumps(query_dict))
        if columns:
            mongoexport_cmd += " --fields={fields} ".format(fields=','.join(columns))
        if limit:  # 如果指定了limit,就只导出limit数据
            mongoexport_cmd += " --limit={limit} ".format(limit=limit)
            maxLineNum = min(limit, maxLineNum)

        mongoexport_cmd += " --out={out}".format(out=filename)
        print("导出文件[{}]，数据量:{}".format(filename, maxLineNum))
        rescode = self.__run_shell(mongoexport_cmd)
        if rescode != 0:
            print("mongoexport 命令执行失败！请核验 mongoexport 命令参数")
            print(mongoexport_cmd)
            sys.exit(-1)

        return 0


class FileReader():
    """
    文件分批次读取，可以指定batch 和 limit
    """

    def __init__(self, fileName, **kwargs):
        self.config = {}
        self.config['encoding'] = 'utf-8'  # 文件编码
        self.config['batch'] = 30000  # 分批次读取数据，一次处理的数据量 [默认3W]
        self.config['limit'] = 0  # int 数据量解析限制，只处理limit条数据。此处只是做一下配置信息记录，处理在__iter__中 [默认全部]
        self.config.update(kwargs)
        self.config['fileName'] = fileName

    @staticmethod
    def fileCountLine(fileName, encoding) -> int:
        """
        计算大文件一共有多少行
        :param fileName:
        :return:文件行数
        """
        from itertools import (takewhile, repeat)
        buffer = 1024 * 1024
        try:
            with open(fileName, encoding=encoding, mode='r') as fr:
                buf_gen = takewhile(lambda x: x, (fr.read(buffer) for _ in repeat(None)))
                return sum(buf.count('\n') for buf in buf_gen)
        except Exception as e:
            print("[{}] 文件读取错误，错误信息:\n{}".format(fileName, e))
            return 0

    def __iter__(self) -> list:
        fileName = self.config.get('fileName', None)
        encode = self.config.get('encoding', None)
        limit = self.config.get('limit', None)
        batchSize = self.config.get('batch', None)
        maxLineNum = self.fileCountLine(fileName, encoding=encode)
        print("查询文件:{}，总记录数:{}".format(fileName, maxLineNum))
        if limit:  # 如果指定了limit,就只导出limit数据
            maxLineNum = min(limit, maxLineNum)
        batchSize = min(maxLineNum, batchSize)
        # self.config['batch'] = batchSize
        # self.config['limit'] = maxLineNum
        # print("读取FileReader配置信息:", self.config)
        print("待读取记录数:{},需要读取批次:{},一次读取:{}".format(maxLineNum, ((maxLineNum - 1) // batchSize + 1),
                                                                   batchSize))
        lines = []
        lines_num: int = 0
        with open(fileName, encoding=encode, mode='r') as fr:
            for line in fr:
                lines.append(line)
                lines_num += 1
                if lines_num > maxLineNum:
                    break
                if lines_num % batchSize == 0 or lines_num == maxLineNum:
                    yield lines
                    lines.clear()


class JsonNormalizer():
    """
    接受list[dict,dict,dict]格式的json-list数据，按配置条件将其中的json数据拉平
    一些配置说明：
    【primary_keys】
    tablename = [{"_id":111,"id2":10,"list2":[2,3,4]},
                {"_id":222,"id2":20,"list2":[2,3,4,5]}]
    如果：self.config['primary_keys'] = {"tablename":'_id'}
    》》》tablename = [_id,id2
        111,10,
        222,20
        ]
    》》》tablename_list2:[_id,list2
        111,2
        111,3
        111,4
        222,2
        222,3
        222,4
        222,5
        ]
    如果：self.config['primary_keys'] = {"tablename":'_id'}
    》》》tablename = [_id,id2
        111,10,
        222,20
        ]
    》》》tablename_list2:[id2,list2
        10,2
        10,3
        10,4
        20,2
        20,3
        20,4
        20,5
        ]
    【denest_listcolumn_list】
    tablename = [{"_id":111,"list1":[1,2,3],"list2":[2,3,4]},
                {"_id":222,"list1":[1,2,3,4],"list2":[2,3,4,5]}]
    如果：self.config['primary_keys'] = {"tablename":'_id'}
        self.config['denest_listcolumn_list'] = ["list1",]
    》》》tablename = [_id,list2
        111,[2,3,4],
        222,[2,3,4,5]
        ]
    》》》tablename_list1:[_id,list1
        111,1
        111,2
        111,3
        222,1
        222,2
        222,3
        222,4
        ]
    如果：self.config['primary_keys'] = {"tablename":'_id'}
        self.config['denest_listcolumn_list'] = ["list1","list2"] # 默认是list全展开，这个和[] 效果一样
    》》》tablename = [_id
        111,
        222,
        ]
    》》》tablename_list1:[_id,list2
        111,1
        111,2
        111,3
        222,1
        222,2
        222,3
        222,4
        ]
    》》》tablename_list2:[_id,list2
        111,2
        111,3
        111,4
        222,2
        222,3
        222,4
        222,5
        ]
    """

    def __init__(self, **kwargs):
        self.resultDataFramedict: dict = {}  # 保存处理后的数据{'tab1':df1,'tab2':df2}
        self.config = {}  # 其他配置项
        self.config['sep'] = '_'  # 生成新字段的命名规则
        self.config['dict_max_level'] = None  # list嵌套最大展开层数，None表示完全展开 [默认,完全展开]
        self.config['list_max_level'] = None  # list嵌套最大展开层数，None表示完全展开 [默认,完全展开]
        # list_max_level 是受 dict_max_level 限制的，因为先展开dict_max_level层后，再判断当前层的 list
        self.config['primary_keys'] = {}  # list 数据展开时，选择此表的字段作为主键
        self.config['denest_listcolumn_list'] = []  # 指定需要展开的 list字段 ，空表示完全展开 [默认,完全展开]
        self.config['formate_null_data'] = True  # 是否格式化空值，例如字段data，部分是dict/list，另一部分是空字符串''。[默认,格式化]
        self.config['multi_table'] = True  # list是否展开成新表 or 与原表合并
        # 注意： multi_table -> False 原表合并(可能导致大量数据重复，导致内存溢出，尤其当多个list同时展开时) [默认，展开成新表]
        self.config['del_listcolumn'] = True  # 解析完列表字段后,是否删除原表中已经解析的这一个字段的数据 [默认,删除]
        self.config.update(kwargs)

    def _todict(self, data):
        """
        将数据类型转化为dict
        :param data:str | dict data in pd.dataFrame
        :return:Data of type Dict
        """
        if isinstance(data, dict):
            return data
        else:
            try:
                return json.loads(str(data))
            except Exception as e:
                print(e)
                print(data)
                sys.exit(-1)

    def normalize(self, tableName: str, jsonList: list, **config) -> dict:
        """
        将嵌套多层的json数据拉平
        :param tableName:表名字
        :param jsonList:json-list 格式的数据
        :param config:更新config
        :return:dict[str, pd.DataFrame]
        """
        self.config.update(config)
        # print("JsonNormalizer配置信息:", self.config)
        dict_max_level = self.config.get('dict_max_level', None)
        sep = self.config.get('sep', '_')
        tabledf = pd.json_normalize([self._todict(data) for data in jsonList], max_level=dict_max_level, sep=sep)
        table_df_dict: dict = {tableName: tabledf}  # table_df_dict 中第一张表
        # 嵌套字典类型可以直接使用pd.json_normalize展开到指定max_level。
        # 嵌套的list类型，必须单独处理，且多次处理，一次展开一层list
        list_max_level = self.config.get('list_max_level', None)
        list_max_level = list_max_level if list_max_level is not None else sys.maxsize
        # 递归多层展开list
        table_df_dict = self.normalize_maxlevel_listcolumns(tableName, table_df_dict, list_max_level)
        # 格式化结果表名，collectioin_collev1_collev2_collev3
        tables = list(table_df_dict.keys())
        tables.remove(tableName)
        for k in tables:
            table_df_dict[tableName + sep + k] = table_df_dict[k]
            del table_df_dict[k]
        self.resultDataFramedict.update(table_df_dict)  # 处理好的数据，存储到resultDataFramedict中
        return table_df_dict

    def normalize_maxlevel_listcolumns(self, tableName: str,
                                       table_df_dict: dict,
                                       max_level: int) -> dict:
        """
        将字段为list类型的数据拉平，展开多个list 类型的字段，一次调用展开一层
        :param tableName:
        :param table_df_dict:
        :param sep:
        :param max_level:
        :param denest_listcolumn_list:
        :param listcolumn2multi_table:
        :return:dict[str, pd.DataFrame]
        """
        denest_listcolumn_list = self.config.get('denest_listcolumn_list', None)
        formate_null_data = self.config.get('formate_null_data', True)
        tabledf: pd.DataFrame = table_df_dict.get(tableName)
        if formate_null_data:  # 如果格式化空数据
            tabledf = self.formate_null_data(tabledf)
        list_type_columns = tabledf.columns[tabledf.applymap(lambda x: isinstance(x, list)).all()].tolist()
        if denest_listcolumn_list:  # 如果指定了需要展开list的字段，取交集
            list_type_columns = [col for col in denest_listcolumn_list if col in list_type_columns]
        if (max_level <= 0) or (len(list_type_columns) == 0) or (tabledf.shape[0] == 0):  # 不需要解析
            return table_df_dict
        else:
            max_level -= 1
            # print(tableName, "待展开的list字段:", list_type_columns)
            old_tables = list(table_df_dict.keys())  # 保留解析前的tablenames
            for col in list_type_columns:  # 挨个字段解析
                table_df_dict = self.normalize_one_listcolumn(tableName, table_df_dict, col)

            # 新增加的表，继续解析list
            if self.config.get('multi_table', True):  # 如果生成多个新表,解析新表
                next_tablenames = list(table_df_dict.keys())
                next_tablenames = [tablename for tablename in next_tablenames if tablename not in old_tables]
            else:  # 如果合并到原表，继续解析原表
                next_tablenames = old_tables

            for tab in next_tablenames:
                table_df_dict = self.normalize_maxlevel_listcolumns(tab, table_df_dict, max_level)
            return table_df_dict

    def normalize_one_listcolumn(self, tableName: str, table_df_Dict: dict, list_column: str):
        """
        将字段为list类型的数据拉平，展开一个字段
        :param tableName:
        :param table_df_Dict:
        :param sep:
        :param list_column:
        :param new_table_column:
        :param primary_key:
        :param del_listcolumn:
        :param listcolumn2multi_table:
        :return:
        """
        sep = self.config.get('sep', '_')
        multi_table = self.config.get('multi_table', True)
        del_listcolumn = self.config.get('del_listcolumn', True)
        primary_keys = self.config.get('primary_keys').get(tableName, ['_id', ])
        tabledf: pd.DataFrame = table_df_Dict[tableName]
        tmp_df = tabledf[[k for k in primary_keys if k != list_column] + [list_column, ]]
        if tmp_df.shape[0] > 0:  # 有数据，进一步解析展开list
            tmp_jsonlist = tmp_df.to_dict(orient='records')  # 获取新的json-list 数据
            # print(str(json.dumps(tmp_jsonlist[0])))
            tmp_list_column_df = pd.json_normalize(data=tmp_jsonlist,
                                                   record_path=list_column,
                                                   meta=primary_keys,
                                                   record_prefix='{}{}'.format(list_column, sep),
                                                   sep=sep)
            if del_listcolumn:
                del tabledf[list_column]  # 解析完列表这一列后,删除原表中数据列为列表这一列
        else:  # 如果tmp_df没有数据，不进一步解析
            tmp_list_column_df = tmp_df
        if multi_table:  # 保存list展开的新表
            table_df_Dict[list_column] = tmp_list_column_df  # 以[字段名]命名新表
            table_df_Dict[tableName] = tabledf  # 旧表名
        else:  # 合并list展开的新表
            # print("合并表:", tabledf.shape, tmp_list_column_df.shape)
            tabledf = pd.merge(tabledf, tmp_list_column_df, on=primary_keys, how='left')
            # print("合并后:", tabledf.shape)
            table_df_Dict[tableName] = tabledf
        return table_df_Dict

    @staticmethod
    def formate_null_data(df: pd.DataFrame):
        """
        格式化部分为空的数据，但是此字段和其他有数据的数据类型不一致，例如空白数据 col:"",
        :param df:
        :return:
        """
        dict_type_columns = df.columns[df.applymap(lambda x: isinstance(x, dict)).any()].tolist()
        # print("字典字段补充：", dict_type_columns)
        for col in dict_type_columns:
            df[col] = df[col].apply(lambda x: {} if not isinstance(x, dict) and len(str(x)) < 5 else x)
            # len(str(x)) < 5 判断无用数据，舍弃的一种规则

        list_type_columns = df.columns[df.applymap(lambda x: isinstance(x, list)).any()].tolist()
        # print("数组字段补充：", list_type_columns)
        for col in list_type_columns:
            df[col] = df[col].apply(lambda x: [] if not isinstance(x, dict) and len(str(x)) < 5 else x)
            # len(str(x)) < 5 判断无用数据，舍弃的一种规则

        return df


class MyJsonEncoder(json.JSONEncoder):
    """
    重写构造json类，遇到日期特殊处理，其余默认
    """

    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, datetime.date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


class DataWash():
    """
    数据清洗类，可以传递新旧字符列表来数据清洗，同时还可以指定自己的数据清洗函数
    只需要调用wash就可以
    """

    def __init__(self, old_chars: list = None, new_chars: list = None):
        self.old_chars = []
        if old_chars:
            self.old_chars = old_chars
        self.new_chars = []
        if new_chars:
            self.new_chars = new_chars
        self.chars_num = len(self.old_chars)

    def wash(self, df: pd.DataFrame, func=None):
        if func:
            df = df.applymap(func)

        df.fillna('', inplace=True)  # NaN替换为空字符串
        # df = df.applymap(self._clear_null)  # 空数据转为空白字符串
        df = df.applymap(self._apply_dumps_dict)  # 转换 dict 为格式化的json字符串
        df = df.applymap(self._last_char_replace)  # 特殊字符转换
        return df

    def _apply_dumps_dict(self, x):
        if isinstance(x, dict):
            return json.dumps(x, ensure_ascii=False, cls=MyJsonEncoder)  # 重写构造json类，遇到日期特殊处理，其余默认
        elif isinstance(x, list):
            return json.dumps(x, ensure_ascii=False, cls=MyJsonEncoder)
        elif isinstance(x, datetime.datetime):
            return x.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(x, datetime.date):
            return x.strftime('%Y-%m-%d')
        else:
            return x

    def _clear_null(self, x):
        if str(x).lower() in ('null', 'none'):  # 去掉表示空数据的数据
            return ''
        else:
            return x

    def _last_char_replace(self, x):
        for i in range(self.chars_num):
            x = str(x).replace(self.old_chars[i], self.new_chars[i])
        return x


class TableCsvWriter():
    """
    将table_df_dict 中的表写入csv文件，
    第一批次mode='w',且保存columns
    后面的批次mode='a',使用前面保存的columns
    """

    def __init__(self, **kwargs):
        self.default_to_csv_kwargs = {}  # 导出csv文件，默认配置项
        self.table_columnlist_dict = {}
        self.batch_counter: int = 0  # 第一批导出的数据
        self.default_to_csv_kwargs["header"] = False
        self.default_to_csv_kwargs["index"] = False
        self.default_to_csv_kwargs["quoting"] = 3
        self.default_to_csv_kwargs["sep"] = '\001'
        self.default_to_csv_kwargs["escapechar"] = "\\"
        self.default_to_csv_kwargs.update(kwargs)

    def table_df_dict_tocsv(self, table_df_dict: dict,
                            path: str = '',
                            table_columnlist_dict: dict = None):
        self.batch_counter += 1
        print("第 {} 批次数据,写入文件".format(self.batch_counter))
        if table_columnlist_dict:
            self.table_columnlist_dict.update(table_columnlist_dict)
        if self.batch_counter == 1:
            os.makedirs(path.rsplit('/', 1)[0], exist_ok=True)  # 如果文件路径不存在，创建
            for table, df in table_df_dict.items():
                columns = self.table_columnlist_dict.get(table, df.columns.tolist())
                self.table_columnlist_dict.update({table: columns})  # 存储字段
                filename = "{}{}.txt".format(path, table)
                print(f"[{table}]字段:", json.dumps(columns, ensure_ascii=False))
                print(f"[{filename}]数据量:", df.shape[0])
                self.to_csv(df, filename, mode='w', columns=columns)
        else:
            for table, df in table_df_dict.items():
                columns = self.table_columnlist_dict.get(table, df.columns.tolist())
                filename = "{}{}.txt".format(path, table)
                print(f"[{filename}]数据量:", df.shape[0])
                self.to_csv(df, filename, mode='a', columns=columns)

    def to_csv(self, tabledf: pd.DataFrame,
               filename: str,
               mode: str,
               columns: list,
               **tocsv_kwargs):
        self.default_to_csv_kwargs.update(tocsv_kwargs)  # 更新参数信息
        self.default_to_csv_kwargs['mode'] = mode
        self.default_to_csv_kwargs['columns'] = columns
        cols_subset = [val for val in columns if val not in tabledf.columns.tolist()]
        for col in cols_subset:  # 填充缺失列
            print("{} 字段为空".format(col))
            tabledf[col] = ""
        # print("[shape:]", tabledf.shape)
        # print("[columns:]", tabledf.columns.tolist())
        tabledf.to_csv(filename, **self.default_to_csv_kwargs)


class TableExcelWriter():
    """
    将table_df_dict 中的表写入excel文件，
    """

    def __init__(self, **kwargs):
        self.table_columnlist_dict = {}
        self.default_to_excel_kwargs = {}  # 导出csv文件，默认配置项
        self.default_to_excel_kwargs["header"] = True
        self.default_to_excel_kwargs["index"] = True
        self.default_to_excel_kwargs.update(kwargs)

    def table_df_dict_toexcel(self, table_df_dict: dict,
                              path: str = '',
                              table_columnlist_dict: dict = None):
        if table_columnlist_dict:
            self.table_columnlist_dict.update(table_columnlist_dict)
        os.makedirs(path.rsplit('/', 1)[0], exist_ok=True)  # 如果文件路径不存在，创建
        for table, df in table_df_dict.items():
            columns = self.table_columnlist_dict.get(table, df.columns.tolist())
            self.table_columnlist_dict.update({table: columns})  # 存储字段
            filename = "{}{}.xlsx".format(path, table)
            self.to_excel(df, filename, columns=columns)
        self.first_batch = False

    def to_excel(self, tabledf: pd.DataFrame,
                 filename: str,
                 columns: list,
                 **tocsv_kwargs):
        self.default_to_excel_kwargs.update(tocsv_kwargs)  # 更新参数信息
        self.default_to_excel_kwargs['columns'] = columns
        cols_subset = [val for val in columns if val not in tabledf.columns.tolist()]
        for col in cols_subset:  # 填充缺失列
            print("{} 字段为空".format(col))
            tabledf[col] = ""
        # print(self.default_to_excel_kwargs)
        tabledf.to_excel(filename, **self.default_to_excel_kwargs)


def demo1():
    reader = FileReader(fileName='./paperP.jl', encoding='utf-8', batch=15, limit=50)
    tablename = 'collectionName'
    primary_keys = {
        tablename: ["_id"]
    }
    json_normalizer = JsonNormalizer(primary_keys=primary_keys, list_max_level=0, dict_max_level=0,
                                     del_listcolumn=False)
    washer = DataWash()
    writer = TableExcelWriter()

    def __my_data_wash_func(x):
        return str(x).replace("'", '"').replace('\001', '').replace('\r', '').replace('\n', '')

    for batch_data in reader:
        # print(len(batch_data), type(batch_data))
        print("示例数据:", str(batch_data[0]))
        table_df_dict = json_normalizer.normalize(tablename, batch_data)
        for k in table_df_dict.keys():
            table_df_dict[k] = washer.wash(table_df_dict[k], func=__my_data_wash_func)
        writer.table_df_dict_toexcel(table_df_dict, path='./res/')


def demo2():
    conn = 'mongo 127.0.0.1:27017/dbname -u username -p password'
    collectionName = 'collectionName'
    path = '/data/dt/'
    reader = MongoReader(conn, collectionName, batch=5, limit=5)
    tablename = collectionName
    primary_keys = {
        tablename: ["_id", ]
    }
    json_normalizer = JsonNormalizer(primary_keys=primary_keys, dict_max_level=0, list_max_level=0,
                                     del_listcolumn=True)
    washer = DataWash(old_chars=["\n", "\r", "\001"],
                      new_chars=["/n", "/r", "//"])
    writer = TableCsvWriter()

    for batch_data in reader:
        # print(len(batch_data), type(batch_data))
        # print("示例数据:", str(batch_data[0]))
        table_df_dict = json_normalizer.normalize(tablename, batch_data)
        for k in table_df_dict.keys():
            table_df_dict[k] = washer.wash(table_df_dict[k])
        writer.table_df_dict_tocsv(table_df_dict, path=path)


def demo3():
    conn = 'mongo 127.0.0.1:27017/dbname -u username -p password'
    collectionName = 'collectionName'
    path = '/data/dt/'
    reader = MongoReader(conn, collectionName, batch=5000, limit=12000)
    tablename = collectionName
    primary_keys = {
        tablename: ["_id", ]
    }
    json_normalizer = JsonNormalizer(primary_keys=primary_keys, dict_max_level=None, list_max_level=None,
                                     del_listcolumn=True)
    washer = DataWash(old_chars=["\n", "\r", "\001"],
                      new_chars=["/n", "/r", "//"])
    writer = TableCsvWriter()

    for batch_data in reader:
        # print(len(batch_data), type(batch_data))
        # print("示例数据:", str(batch_data[0]))
        table_df_dict = json_normalizer.normalize(tablename, batch_data)
        for k in table_df_dict.keys():
            table_df_dict[k] = washer.wash(table_df_dict[k])
        writer.table_df_dict_tocsv(table_df_dict, path=path)


def export_with_normalize():
    parser = argparse.ArgumentParser(description="""
    导出mongo数据到文件.[by:yinyl08]
    """)
    parser.add_argument('--collection', type=str, required=True, help='mongo集合名称[必填]')
    parser.add_argument('--conn', type=str, required=True, help='mongo数据库连接串配置文件[必填]')
    parser.add_argument('--filepath', type=str, help='数据导出文件路径[必填]')
    parser.add_argument('--keys', type=str, default='_id', help='主键字段[可选]')
    parser.add_argument('--dellist', type=bool, default=True,
                        help='list展开成新表后,是否删除原表中对应字段,默认True[可选]')
    parser.add_argument('--batch', type=int, default=100000, help='一次导出数据量,默认100000[可选]')
    parser.add_argument('--dict_max', type=int, default=0,
                        help='字典嵌套最大展开层数,默认为0[可选]')
    parser.add_argument('--list_max', type=int, default=0,
                        help='list嵌套最大展开层数,默认为0[可选]')
    parser.add_argument('--query', type=str, default='{}', help='数据筛选条件[可选]')
    parser.add_argument('--limit', type=int, default=0, help='数据量导出限制[可选]')
    parser.add_argument('--columns', type=str, default='{}',
                        help='指定每张表的字段')
    args = parser.parse_args()

    COLLECTION_NAME = args.collection  # 集合名
    CONNECT_STR_FILE = "/home/user1/conf/" + args.connstr + ".conf"  # 数据库连接串配置文件
    FILENAME_EXPORT_PATH = args.filepath
    ID_KEYS = args.keys.split(',')  # 主键字段
    BATCH_SIZE = args.batch  # 一次导出数据量
    DICT_MAX = args.dict_max  # DICT嵌套最大展开层数
    LIST_MAX = args.list_max  # LIST嵌套最大展开层数
    QUERY_DICT = json.loads(args.query, strict=False)  # mongo筛选条件
    LIMIT = args.limit
    DELLIST = args.dellist
    COLUMNS_DICT = json.loads(args.columns, strict=False)  # 指定每张表的字段

    print("[开始时间]:", datetime.datetime.now())
    with open(CONNECT_STR_FILE, encoding="utf-8", mode="r") as fr:
        conn = fr.read().strip()

    reader_columns = COLUMNS_DICT.get(COLLECTION_NAME, None)
    reader = MongoReader(conn, COLLECTION_NAME, batch=BATCH_SIZE, limit=LIMIT, query=QUERY_DICT, columns=reader_columns)
    primary_keys = {
        COLLECTION_NAME: ID_KEYS
    }
    json_normalizer = JsonNormalizer(primary_keys=primary_keys, dict_max_level=DICT_MAX, list_max_level=LIST_MAX,
                                     del_listcolumn=DELLIST)
    washer = DataWash(old_chars=["\n", "\r", "\001"],
                      new_chars=["/n", "/r", "//"])
    writer = TableCsvWriter()

    for batch_data in reader:
        # print(len(batch_data), type(batch_data))
        # print("示例数据:", str(batch_data[0]))
        table_df_dict = json_normalizer.normalize(COLLECTION_NAME, batch_data)
        for k in table_df_dict.keys():
            table_df_dict[k] = washer.wash(table_df_dict[k])
        if COLUMNS_DICT:
            writer.table_df_dict_tocsv(table_df_dict, path=FILENAME_EXPORT_PATH,
                                       table_columnlist_dict=COLUMNS_DICT)
        else:
            writer.table_df_dict_tocsv(table_df_dict, path=FILENAME_EXPORT_PATH)

    print("[结束时间]:", datetime.datetime.now())
    return 0


def export_then_normalize():
    parser = argparse.ArgumentParser(description="""
    导出mongo数据到文件.[by:eli]
    """)
    parser.add_argument('--collection', type=str, required=True, help='mongo集合名称[必填]')
    parser.add_argument('--conn', type=str, required=True, help='mongo数据库连接串配置文件[必填]')
    parser.add_argument('--filepath', type=str, help='数据导出文件路径[必填]')
    parser.add_argument('--keys', type=str, default='_id', help='主键字段[可选]')
    parser.add_argument('--dellist', type=bool, default=True,
                        help='list展开成新表后,是否删除原表中对应字段,默认True[可选]')
    parser.add_argument('--batch', type=int, default=0, help='一次解析数据量,默认0,不分批[可选]')
    parser.add_argument('--dict_max', type=int, default=0,
                        help='字典嵌套最大展开层数,默认为0[可选]')
    parser.add_argument('--list_max', type=int, default=0,
                        help='list嵌套最大展开层数,默认为0[可选]')
    parser.add_argument('--query', type=str, default='{}', help='数据筛选条件[可选]')
    parser.add_argument('--limit', type=int, default=0, help='数据量导出限制[可选]')
    parser.add_argument('--columns', type=str, default='{}',
                        help='指定每张表的字段')
    args = parser.parse_args()

    COLLECTION_NAME = args.collection  # 集合名
    CONNECT_STR_FILE = "/home/user1/conf/" + args.connstr + ".conf"  # 数据库连接串配置文件
    FILENAME_EXPORT_PATH = args.filepath
    ID_KEYS = args.keys.split(',')  # 主键字段
    BATCH = args.batch  # 一次处理数据量
    DICT_MAX = args.dict_max  # DICT嵌套最大展开层数
    LIST_MAX = args.list_max  # LIST嵌套最大展开层数
    QUERY_DICT = json.loads(args.query, strict=False)  # mongo筛选条件
    LIMIT = args.limit
    DELLIST = args.dellist
    COLUMNS_DICT = json.loads(args.columns, strict=False)  # 指定每张表的字段

    print("[开始时间]:", datetime.datetime.now())
    with open(CONNECT_STR_FILE, encoding="utf-8", mode="r") as fr:
        conn = fr.read().strip()

    exporter_columns = COLUMNS_DICT.get(COLLECTION_NAME, None)
    export_jsonfile = FILENAME_EXPORT_PATH + COLLECTION_NAME + '.json'
    exporter = MongoExporter(conn, COLLECTION_NAME,
                             filename=export_jsonfile,
                             limit=LIMIT,
                             query=QUERY_DICT,
                             columns=exporter_columns)
    exporter.export_json()
    reader = FileReader(fileName=export_jsonfile, encoding='utf-8', batch=BATCH, limit=LIMIT)
    primary_keys = {
        COLLECTION_NAME: ID_KEYS
    }
    json_normalizer = JsonNormalizer(primary_keys=primary_keys, dict_max_level=DICT_MAX, list_max_level=LIST_MAX,
                                     del_listcolumn=DELLIST)
    washer = DataWash(old_chars=["\n", "\r", "\001"],
                      new_chars=["/n", "/r", "//"])
    writer = TableCsvWriter()

    for batch_data in reader:
        # print(len(batch_data), type(batch_data))
        # print("示例数据:", str(batch_data[0]))
        table_df_dict = json_normalizer.normalize(COLLECTION_NAME, batch_data)
        for k in table_df_dict.keys():
            table_df_dict[k] = washer.wash(table_df_dict[k])
        if COLUMNS_DICT:
            writer.table_df_dict_tocsv(table_df_dict, path=FILENAME_EXPORT_PATH,
                                       table_columnlist_dict=COLUMNS_DICT)
        else:
            writer.table_df_dict_tocsv(table_df_dict, path=FILENAME_EXPORT_PATH)

    os.remove(export_jsonfile)  # 删除临时文件 export_jsonfile
    print("[结束时间]:", datetime.datetime.now())
    return 0


if __name__ == '__main__':
    # export_then_normalize()
    export_with_normalize()
