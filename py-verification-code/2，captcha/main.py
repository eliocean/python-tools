from captcha.image import ImageCaptcha
"""pip install captcha"""
from random import randint
char_list = list("0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ")
chars = ''
for i in range(4):
    chars += char_list[randint(0, 62)]
image = ImageCaptcha().generate_image(chars)

image.show()
image.save("vcode.jpg")
print(chars)