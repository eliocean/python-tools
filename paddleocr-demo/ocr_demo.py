from paddleocr import PaddleOCR, draw_ocr

ocr = PaddleOCR(use_angle_cls=True, lang="ch",
                show_log=False)  # need to run only once to download and load model into memory, 不打印日志show_log=False


def ocr_text(img='1.jpg'):
    """
    :param img:support ndarray, img_path and list or ndarray
    :return:result_text_list
    """
    result_text_list = []
    result = ocr.ocr(img, cls=False)  # cls=False 不做文本方向检测分类
    for idx in range(len(result)):
        res = result[idx]
        for i in range(len(res)):
            result_text_list.append(res[i][1][0])
            print(f"【第{i + 1}行】:", res[i][1][0])

    return result_text_list


"""
# 显示结果
# 如果本地没有simfang.ttf，可以在doc/fonts目录下下载
from PIL import Image
result = result[0]
image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in result]
txts = [line[1][0] for line in result]
scores = [line[1][1] for line in result]
im_show = draw_ocr(image, boxes, txts, scores, font_path='doc/fonts/simfang.ttf')
im_show = Image.fromarray(im_show)
im_show.save('ocr-detect-result.jpg')

"""

if __name__ == '__main__':
    ocr_text()
