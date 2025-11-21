import time

from pywinauto import Application
from pywinauto.controls import uiawrapper
from playwright.sync_api import sync_playwright

app = Application(backend="win32").start(r"D:\LiuYunKu4\LiuYunKu.exe")
print("应用启动成功")

time.sleep(8)

try:
    windows = app.windows()
    if windows:
        main_window = windows[0]
        print(f"通过app对象找到窗口: {main_window.window_text()}")
        return app,main_window
except Exception as e:
    print(f"通过app对象获取窗口失败: {e}")
"""
try:
    radio_button = dlg.child_window(title="在线素材")
    radio_button.click()
    print("通过.click()点击成功。")
except Exception as e:
    print(f".click() 失败: {e}")
"""