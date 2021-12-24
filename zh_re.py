import re

text = "hello 你好 世界！ world!"

pattern  = re.compile(r'[\u4e00-\u9fa5]+')
result = pattern.findall(text)
print(result)

pattern  = re.compile(r'[\u4e00-\u9fa5\uff01]+') # 加！[\uff01]
result = pattern.findall(text)
print(result)
"""
中文符号    规则
汉字字符     [\u4e00-\u9fa5]
（			\uff08
〈			\u3008
《			\u300a
「			\u300c
『			\u300e
﹃			\ufe43
〔			\u3014
…			\u2026
～			\uff5e
￥			\uffe5
【			\u3010
，			\uff0c
？			\uff1f
：			\uff1a
“			\u201c
‘			\u2018
）			\uff09
〉			\u3009
》			\u300b
」			\u300d
』			\u300f
﹄			\ufe44
〕			\u3015
—			\u2014
﹏			\ufe4f
、			\u3001
】			\u3011
。			\u3002
！			\uff01
；			\uff1b
”			\u201d
’			\u2019
"""