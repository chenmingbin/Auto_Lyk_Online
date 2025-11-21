from itertools import count
from playwright.sync_api import sync_playwright
from pywinauto import Application, Desktop
import time
import psutil

class LiuYunKuAutomator:
    """溜云库自动化器"""

    def __init__(self, exe_path=r"D:\LiuYunKu4\LiuYunKu.exe"):
        self.exe_path = exe_path
        self.app = None
        self.main_window = None

    def start(self):
        """启动应用"""
        print("正在启动溜云库...")
        self.app = Application(backend="uia").start(self.exe_path)
        return self.wait_for_window(30)

    def wait_for_window(self, timeout=30):
        """等待主窗口出现"""
        start_time = time.time()
        desktop = Desktop(backend="uia")

        while time.time() - start_time < timeout:
            for window in desktop.windows():
                if window.is_visible():
                    try:
                        text = window.window_text()
                        if "溜云库" in text:
                            self.main_window = window
                            print(f"找到主窗口: {text}")
                            return True
                    except:
                        continue

            print("等待窗口加载...")
            time.sleep(2)

        print("等待窗口超时")
        return False

    def click_online_material(self):
        """点击在线素材"""
        if not self.main_window:
            print("没有找到窗口")
            return False

        # 设置焦点
        self.main_window.set_focus()
        time.sleep(1)

        # 查找在线素材RadioButton
        try:
            radio_buttons = self.main_window.descendants(control_type="RadioButton")
            for radio in radio_buttons:
                try:
                    text = radio.window_text()
                    if "在线素材" in text:
                        print(f"找到在线素材: {text}")
                        radio.click_input()
                        print("点击成功!")
                        return True
                except:
                    continue
        except Exception as e:
            print(f"查找RadioButton失败: {e}")

        return False

    def check_online(self):
        try:
            Text_Block = self.main_window.descendants(control_type="Text")
            for Block in Text_Block:
                try:
                    text = Block.window_text()
                    if "模型库" in text:
                        print(f"已处于在线素材: {text}")
                        return True
                except:
                    continue
        except Exception as e:
            print(f"查找TextBlock失败: {e}")


    def close(self):
        """关闭应用"""
        if self.main_window:
            try:
                self.main_window.close()
                print("应用已关闭")
            except:
                pass


def connect_with_playwright_correct():
    """正确的CDP连接方法"""

    with sync_playwright() as p:
        # 方法1: 连接到本地运行的Chrome浏览器（需要先启动带调试端口的Chrome）
        try:
            # 首先确保Chrome以调试模式启动：
            # chrome.exe --remote-debugging-port=9222

            browser = p.chromium.connect_over_cdp("http://localhost:9222")
            print("成功连接到本地Chrome")

            # 获取页面
            page = browser.contexts[0].pages[0] if browser.contexts else browser.new_page()
            print("获取页面信息成功")
            # 完成点击
            page.locator("p[class*='mantine-Text-root'][datatype='6']").click()
            """
            page.mouse.down()
            page.locator("//span[text()='沙发']").hover()
            page.mouse.up()
            page.locator("//span[text()='沙发']").click()
            """
            page.wait_for_timeout(1000)

            # 截图
            page.screenshot(path='page_screenshot.png')
            return browser

        except Exception as e:
            print(f"CDP连接失败: {e}")
            return None


# 使用示例
def main():
    automator = LiuYunKuAutomator()

    # 启动应用
    if automator.start():
        # 点击在线素材
        if automator.click_online_material():
            print("点击操作成功!")
        if automator.check_online():
            print("正确进入在线素材")

        connect_with_playwright_correct()

        # 保持应用运行，或者关闭
        # automator.close()


if __name__ == "__main__":
    main()