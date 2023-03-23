import time
import win32gui, win32ui, win32api, win32con
from PIL import Image
import numpy
from paddleocr import PaddleOCR


class CaptureAndOcr():
    def __init__(self, hwnd=0, look=True):
        self.look = look  # 是否显示截屏信息
        self.prebrush = None
        self.hbrush = None
        self.hPen = None
        self.hwnd = hwnd  # 窗口的编号，0号表示当前活跃窗口
        self.hwndDC = win32gui.GetWindowDC(hwnd)  # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
        self.mfcDC = win32ui.CreateDCFromHandle(self.hwndDC)  # 根据窗口的DC获取mfcDC
        self.saveDC = self.mfcDC.CreateCompatibleDC()  # mfcDC创建可兼容的DC

        self.ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)

    def __ocr_text(self, img='1.jpg') -> list:
        """
        :param img:support ndarray, img_path and list or ndarray
        :return:result_text_list
        """
        result_text_list = []
        result = self.ocr.ocr(img, cls=False)  # cls=False 不做文本方向检测分类
        for idx in range(len(result)):
            res = result[idx]
            for i in range(len(res)):
                result_text_list.append(res[i][1][0])
                # print(f"【第{i + 1}行】:", res[i][1][0])
        return result_text_list

    def capture(self, left_up: tuple, right_down: tuple, filename=None):
        """
        区域截图
        :param left_up: 左上角坐标
        :param right_down:右下角坐标
        """
        argw = right_down[0] - left_up[0]
        argh = right_down[1] - left_up[1]

        saveBitMap = win32ui.CreateBitmap()  # 创建bigmap准备保存图片
        MoniterDev = win32api.EnumDisplayMonitors(None, None)  # 获取监控器信息
        # 判断是否设置截图区域
        saveBitMap.CreateCompatibleBitmap(self.mfcDC, argw, argh)  # 为bitmap开辟空间
        self.saveDC.SelectObject(saveBitMap)  # 高度saveDC，将截图保存到saveBitmap中
        # 截取从左上角（0，0）或者 rect 长宽为（w，h）的图片
        rect = (left_up[0], left_up[1])
        self.saveDC.BitBlt((0, 0), (argw, argh), self.mfcDC, rect,
                           win32con.SRCCOPY)  # 目标矩形顶点(0,0)长宽(w,h),源设备mfcDC,源矩形顶点tmptl
        saveBitMap.GetBitmapBits()
        if filename:
            saveBitMap.SaveBitmapFile(self.saveDC, filename)
        if self.look:
            # 绘制辅助框
            hPen = win32gui.CreatePen(win32con.PS_SOLID, 3, win32api.RGB(236, 110, 108))  # 定义框颜色
            win32gui.SelectObject(self.hwndDC, hPen)
            hbrush = win32gui.GetStockObject(win32con.NULL_BRUSH)  # 定义透明画刷，这个很重要！！
            prebrush = win32gui.SelectObject(self.hwndDC, hbrush)
            win32gui.Rectangle(self.hwndDC, left_up[0], left_up[1], right_down[0], right_down[1])  # 左上到右下的坐标
            win32gui.SelectObject(self.hwndDC, prebrush)

        # 获取位图信息,并进行ocr识别
        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        im_PIL = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
        res_list = self.__ocr_text(numpy.array(im_PIL))
        print("\n".join(res_list))

    def __del__(self):
        # # 回收资源
        self.mfcDC.DeleteDC()
        self.saveDC.DeleteDC()
        win32gui.DeleteObject(self.hPen)
        win32gui.DeleteObject(self.hbrush)
        win32gui.DeleteObject(self.prebrush)
        win32gui.ReleaseDC(self.hwnd, self.hwndDC)


if __name__ == '__main__':
    cap = CaptureAndOcr()
    while True:
        time.sleep(3)
        cap.capture((300, 300), (500, 500))
