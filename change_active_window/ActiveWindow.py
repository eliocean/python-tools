import datetime
import re
import time
import mouse
import win32gui, win32con, win32com.client


class ActiveWindow():
    def __init__(self):
        self.hwnd_map = dict()
        self.__update_desktop_hwnd()
        self.update()

    def __update_desktop_hwnd(self):
        """
        获取桌面工作页面的窗口句柄
        :return:(active_class, active_hwnd)
        """
        mouse.move(0, 0)
        mouse.click()
        time.sleep(1)
        active_hwnd, active_text, active_class = self.get_active_hwnd()
        self.hwnd_map.update({"Desktop": active_hwnd})

    def __change_active_window_with_hwnd(self, hwnd):
        """
        把窗口设置为活动(最前置)窗口
        :param hwnd:窗口句柄
        # 先发送一个sendKey事件，否则会报错导致后面的设置活动窗口无效：pywintypes.error
        # 虚拟键代码: https://learn.microsoft.com/zh-cn/office/vba/language/reference/user-interface-help/sendkeys-statement
        # shell.SendKeys('%')
        """

        shell = win32com.client.Dispatch("WScript.Shell")
        shell.SendKeys('^')
        win32gui.SetForegroundWindow(hwnd)  # 被其他窗口遮挡，调用后放到最前面
        win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)  # 解决被最小化最大化的情况
        win32gui.ShowWindow(hwnd, win32con.SW_SHOW)

    @staticmethod
    def _update_hwnds_callback(hwnd, hwnd_map: dict):
        """
        :param hwnd: 回调函数的参数，每一个窗口句柄
        :param hwnd_map:存储hwnd{text:hwnd}数据的字典
        :return: 更新hwnd_map 中存储的数据
        :use-example:
            hwnd_map = {}
            win32gui.EnumWindows(get_all_hwnd, 0)
        """
        text = win32gui.GetWindowText(hwnd)
        if (text and win32gui.IsWindow(hwnd) and
                win32gui.IsWindowEnabled(hwnd) and
                win32gui.IsWindowVisible(hwnd)):
            hwnd_map.update({text: hwnd})

    def set_active_window(self, window_text_regex: str):
        """
        把目标窗口设置为活动(最前置)窗口
        :param hwnd_map:
        :param window_text_regex:
        :return:
        :use-example:
            hwnd_map = {}
            win32gui.EnumWindows(_update_hwnds_callback, hwnd_map)
            # print(hwnd_map)
            _set_active_window(hwnd_map, "阿里云")
        """
        for text, hwnd in self.hwnd_map.items():
            if re.match(window_text_regex, text) is not None:
                self.__change_active_window_with_hwnd(hwnd)
                return True  # 活动窗口更改成功
        # 如果没有搜索到想要的窗口，自动更新一次窗口句柄，再次搜索一次
        self.update()
        for text, hwnd in self.hwnd_map.items():
            if re.match(window_text_regex, text) is not None:
                self.__change_active_window_with_hwnd(hwnd)
                return True  # 活动窗口更改成功

        return False  # 活动窗口更改失败

    def update(self):
        win32gui.EnumWindows(self._update_hwnds_callback, self.hwnd_map)

    def get_active_hwnd(self):
        """
        输出当前活动窗体句柄
        :return: 元组 (hwnd,title,class)
        :use-example:
            active_hwnd, active_text, active_class = get_active_hwnd()
            print('活动窗体句柄 hwnd:', active_hwnd)
            print('活动窗体标题 text:', active_text)
            print('活动窗体类 class:', active_class)
        """
        hwnd_active = win32gui.GetForegroundWindow()
        # print('活动窗体句柄 hwnd:', hwnd_active)
        # print('活动窗体标题 text:', win32gui.GetWindowText(hwnd_active))
        # print('活动窗体类 class:', win32gui.GetClassName(hwnd_active))
        return_tuple = (hwnd_active, win32gui.GetWindowText(hwnd_active), win32gui.GetClassName(hwnd_active))
        return return_tuple

    def print_active_hwd(self):
        """
        打印当前活动窗体句柄
        """
        active_hwnd, active_text, active_class = self.get_active_hwnd()
        print("=" * 20, datetime.datetime.now(), "=" * 20)
        print('活动窗体句柄 hwnd:', active_hwnd)
        print('活动窗体标题 text:', active_text)
        print('活动窗体类 class:', active_class)


if __name__ == '__main__':
    aw = ActiveWindow()
    print(aw.hwnd_map)
    aw.set_active_window("青儿")
