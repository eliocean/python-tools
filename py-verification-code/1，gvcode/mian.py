from gvcode import VFCode
"""pip install gvcode"""
code = VFCode()
# code.generate("sdsa")#序列解包
# code.save("vcode.jpg")

code.generate_mix(5)
code.save("vcode.jpg")
