"""
替换一段代码中,中文标点符号.
"""

FILENAME = "transfile.txt"

TRANS_DICT = {
    "。": ".",
    "，": ",",
    "：": ":",
    "（": "(",
    "）": ")",
    "；": ";",
    "！": "!",
    "￥": "$",
    "”": '"',
    "’": "'",
    "？": "?"
}


def trans_punctuation(transtr: str, trans_dict: dict):
    for k, v in trans_dict.items():
        transtr = transtr.replace(k, v)

    return transtr


with open(FILENAME, encoding="utf-8", mode="r") as fr:
    lines = fr.readlines()

with open(FILENAME, encoding="utf-8", mode="w") as fw:
    for line in lines:
        fw.write(trans_punctuation(line, TRANS_DICT))
