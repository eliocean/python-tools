import time
import win32gui, win32ui, win32api, win32con


def winsst(argw=0, argh=0, argtopleft=(0, 0), filename=None):
    '''截图，输出Bitmapsbits的列表
    argw=0表示全宽，argh=0表示全高
    '''
    hwnd = 0  # 窗口的编号，0号表示当前活跃窗口
    hwndDC = win32gui.GetWindowDC(hwnd)  # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)  # 根据窗口的DC获取mfcDC
    saveDC = mfcDC.CreateCompatibleDC()  # mfcDC创建可兼容的DC
    saveBitMap = win32ui.CreateBitmap()  # 创建bigmap准备保存图片
    MoniterDev = win32api.EnumDisplayMonitors(None, None)  # 获取监控器信息
    # 判断是否设置截图区域
    w = MoniterDev[0][2][2] if argw == 0 else argw
    h = MoniterDev[0][2][3] if argh == 0 else argh
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)  # 为bitmap开辟空间
    saveDC.SelectObject(saveBitMap)  # 高度saveDC，将截图保存到saveBitmap中
    # 截取从左上角（0，0）或者 tmptl 长宽为（w，h）的图片
    tx = 0 if argtopleft[0] <= 0 else argtopleft[0]
    ty = 0 if argtopleft[1] <= 0 else argtopleft[1]
    tmptl = (tx, ty)
    saveDC.BitBlt((0, 0), (w, h), mfcDC, tmptl, win32con.SRCCOPY)  # 目标矩形顶点(0,0)长宽(w,h),源设备mfcDC,源矩形顶点tmptl
    saveBitMap.GetBitmapBits()
    if filename:
        saveBitMap.SaveBitmapFile(saveDC, filename)
    ###获取位图信息
    # # 绘制辅助框 暂时未解决透明问题
    hPen = win32gui.CreatePen(win32con.PS_SOLID, 5, win32api.RGB(236, 110, 108))  # 定义框颜色
    win32gui.SelectObject(hwndDC, hPen)
    hbrush = win32gui.GetStockObject(win32con.NULL_BRUSH)  # 定义透明画刷，这个很重要！！
    prebrush = win32gui.SelectObject(hwndDC, hbrush)
    win32gui.Rectangle(hwndDC, tx - 1, ty - 1, tx + w + 2, ty + h + 2)  # 左上到右下的坐标
    win32gui.SelectObject(hwndDC, prebrush)
    # # 回收资源
    mfcDC.DeleteDC()
    saveDC.DeleteDC()
    win32gui.DeleteObject(hPen)
    win32gui.DeleteObject(hbrush)
    win32gui.DeleteObject(prebrush)
    win32gui.ReleaseDC(hwnd, hwndDC)


def capture(left_up: tuple, right_down: tuple, filename=None):
    """
    区域截图
    :param left_up: 左上角坐标
    :param right_down:右下角坐标
    """
    argtopleft = left_up
    argw = right_down[0] - left_up[0]
    argh = right_down[1] - left_up[1]
    winsst(argw, argh, argtopleft, filename)


if __name__ == '__main__':
    time.sleep(1)
    capture((300, 500), (700, 800), filename='../图像相似度比较/test2.jpg')
