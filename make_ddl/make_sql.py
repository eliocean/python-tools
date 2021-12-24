#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author:Eli
# datetime:2021/8/10 16:38
# software: PyCharm

# 读取sql字段名
def read_keys_file(keys_file="columns.txt"):
    with open(keys_file, "r") as fr:
        line = fr.read().strip()

    keys_list = line.split(',')

    # for key in keys_list:
    #     print(key)

    return keys_list


# 字段设置默认字段类型，返回字段-类型字典
def make_dict(keys_list: [], default_dtype="string"):
    if keys_list is None:
        keys_list = []
    if keys_list is None:
        keys_list = []
    keys_dict = {}
    for k in keys_list:
        if not keys_dict.get(k):
            keys_dict.update({k: default_dtype})
        else:
            print(k, "---键已经存在！！！请检查！！！")

    return keys_dict


# 修改某些字段的数据类型
def update_col_type(key_type_dict: {}, key="col", dtype="string"):
    if key_type_dict.get(key):
        key_type_dict[key] = dtype
    else:
        print(key, "---字段名称不存在，请检查！！！")


# 根据keys_dict字典，生成sql语句
def make_sql(col_dtype_dict: {}):
    keys = read_keys_file()

    key_formate_str = "{col_name} {dtype},"
    keys_str = ""
    # 解析设置 col-dtype
    for col, dtype in col_dtype_dict.items():
        keys_str += key_formate_str.format(col_name=col, dtype=dtype)

    keys_str = keys_str.strip(',')  # 去掉最后的,
    # print(keys_str)
    # 整合最后的sql语句
    sql_str = 'create table IF NOT EXISTS TABLE_NAME({keys_str})'.format(keys_str=keys_str)

    # print(sql_str)
    return sql_str


def go_main(keys_file="columns.txt"):
    keys_list = read_keys_file(keys_file)  # 读取字段名
    col_dtype_dict = make_dict(keys_list, default_dtype="string")  # 生成key-dtype字典,默认所有数据类型为string
    update_col_type(col_dtype_dict, key="MAKEDATE", dtype="date")  # 修改某些字段的数据类型,非string
    update_col_type(col_dtype_dict, key="SUM_PREM", dtype="double")  # 修改某些字段的数据类型,非string
    update_col_type(col_dtype_dict, key="MEMBER_WEL_DISC", dtype="double")  # 修改某些字段的数据类型,非string
    update_col_type(col_dtype_dict, key="AMNT", dtype="double")  # 修改某些字段的数据类型,非string
    update_col_type(col_dtype_dict, key="PEOPLES2", dtype="int")  # 修改某些字段的数据类型,非string
    update_col_type(col_dtype_dict, key="CVALIDATE", dtype="date")  # 修改某些字段的数据类型,非string
    update_col_type(col_dtype_dict, key="BUSIRATE", dtype="double")  # 修改某些字段的数据类型,非string
    update_col_type(col_dtype_dict, key="MANAGEMENT_EXPENSE", dtype="double")  # 修改某些字段的数据类型,非string

    for k, v in col_dtype_dict.items():  # 打印所有字段和字段类型
        print("{k} : {v}".format(k=k, v=v))

    print("共有字段{}个,ddl如下:\n".format(len(col_dtype_dict)))  # 打印字段总数统计

    sql_str = make_sql(col_dtype_dict)  # 根据col_dtype字典，make_ddl
    print(sql_str)  # 打印生成的sql语句


if __name__ == '__main__':
    go_main()
