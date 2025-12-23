import time
import json
import os
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Browser, Page, ElementHandle
from pywinauto import Application, Desktop
import psutil
class LiuYunKuNavigationAutomator:
    """溜云库导航自动化器 - 最终优化版"""
    
    def __init__(self, exe_path=r"D:\LiuYunKu4\LiuYunKu.exe"):
        self.exe_path = exe_path
        self.app = None
        self.main_window = None
        self.playwright = None
        self.browser = None
        self.page = None
        self.navigation_data = {}
        
    def start_application(self, timeout=30) -> bool:
        """启动溜云库应用"""
        try:
            print("🚀 正在启动溜云库...")
            
            # 检查进程是否已存在
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == 'LiuYunKu.exe':
                    print("⚠️  检测到溜云库已在运行，尝试连接...")
                    return self.connect_to_existing_window()
            
            # 启动新应用
            self.app = Application(backend="uia").start(self.exe_path)
            success = self.wait_for_main_window(timeout)
            
            if success:
                print("✅ 溜云库启动成功")
                return True
            else:
                print("❌ 溜云库启动失败")
                return False
                
        except Exception as e:
            print(f"❌ 启动应用时出错: {e}")
            return False
    
    def connect_to_existing_window(self, timeout=30) -> bool:
        """连接到已运行的溜云库窗口"""
        try:
            desktop = Desktop(backend="uia")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                for window in desktop.windows():
                    if window.is_visible():
                        try:
                            text = window.window_text()
                            if "溜云库" in text:
                                self.main_window = window
                                print(f"✅ 连接到现有窗口: {text}")
                                return True
                        except:
                            continue
                time.sleep(2)
            
            print("❌ 未找到现有溜云库窗口")
            return False
            
        except Exception as e:
            print(f"❌ 连接现有窗口失败: {e}")
            return False
    
    def wait_for_main_window(self, timeout=30) -> bool:
        """等待主窗口出现"""
        try:
            desktop = Desktop(backend="uia")
            start_time = time.time()
            
            while time.time() - start_time < timeout:
                for window in desktop.windows():
                    if window.is_visible():
                        try:
                            text = window.window_text()
                            if "溜云库" in text:
                                self.main_window = window
                                print(f"✅ 找到主窗口: {text}")
                                return True
                        except:
                            continue
                
                print("⏳ 等待窗口加载...")
                time.sleep(2)
            
            print("❌ 等待窗口超时")
            return False
            
        except Exception as e:
            print(f"❌ 等待窗口失败: {e}")
            return False
    
    def navigate_to_online_material(self) -> bool:
        """导航到在线素材页面"""
        try:
            if not self.main_window:
                print("❌ 主窗口未找到")
                return False
            
            print("📍 设置窗口焦点...")
            self.main_window.set_focus()
            time.sleep(2)
            
            # 检查是否已经在在线素材页面
            if self.check_online_material():
                print("✅ 已处于在线素材页面")
                return True
            
            print("🔍 查找在线素材RadioButton...")
            radio_buttons = self.main_window.descendants(control_type="RadioButton")
            
            for radio in radio_buttons:
                try:
                    text = radio.window_text()
                    print(f"发现RadioButton: {text}")
                    
                    if "在线" in text:
                        print(f"✅ 找到在线素材: {text}")
                        radio.click_input()
                        print("✅ 点击在线素材成功!")
                        time.sleep(3)  # 等待页面加载
                        
                        # 验证是否成功切换
                        if self.check_online_material():
                            return True
                        else:
                            print("⚠️  点击后验证失败，尝试重试...")
                            radio.click_input()
                            time.sleep(3)
                            return self.check_online_material()
                            
                except Exception as e:
                    print(f"处理RadioButton时出错: {e}")
                    continue
            
            print("❌ 未找到在线素材RadioButton")
            return False
            
        except Exception as e:
            print(f"❌ 导航到在线素材失败: {e}")
            return False
    
    def check_online_material(self) -> bool:
        """检查是否已处于在线素材页面"""
        try:
            if not self.main_window:
                return False
            
            text_blocks = self.main_window.descendants(control_type="Text")
            for block in text_blocks:
                try:
                    text = block.window_text()
                    if "模型库" in text or "在线素材" in text:
                        print(f"✅ 检测到在线素材页面: {text}")
                        return True
                except:
                    continue
            
            return False
            
        except Exception as e:
            print(f"❌ 检查在线素材状态失败: {e}")
            return False
    
    def connect_to_browser(self, max_retries=3) -> bool:
        """连接到溜云库内的浏览器"""
        try:
            print("🌐 尝试连接到浏览器...")
            
            # 初始化Playwright（同步模式）
            self.playwright = sync_playwright().start()
            
            for attempt in range(max_retries):
                try:
                    # 尝试不同的CDP端口
                    ports = ['9222', '9333', '9444', '9555']
                    
                    for port in ports:
                        try:
                            cdp_url = f"http://localhost:{port}"
                            print(f"🔗 尝试连接CDP: {cdp_url}")
                            
                            # 连接CDP
                            self.browser = self.playwright.chromium.connect_over_cdp(cdp_url)
                            print("✅ 成功连接到浏览器")
                            
                            # 获取页面
                            if self.browser.contexts and self.browser.contexts[0].pages:
                                self.page = self.browser.contexts[0].pages[0]
                            else:
                                self.page = self.browser.new_page()
                            
                            # 设置页面超时
                            self.page.set_default_timeout(15000)
                            self.page.set_default_navigation_timeout(15000)
                            
                            print("✅ 获取页面成功")
                            return True
                            
                        except Exception as e:
                            print(f"端口 {port} 连接失败: {e}")
                            continue
                    
                    print(f"⚠️  第 {attempt + 1} 次尝试失败，等待重试...")
                    time.sleep(3)
                    
                except Exception as e:
                    print(f"连接尝试 {attempt + 1} 失败: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(3)
            
            print("❌ 所有连接尝试都失败了")
            return False
            
        except Exception as e:
            print(f"❌ 连接浏览器失败: {e}")
            return False
    
    def get_main_navigation_items(self) -> List[Dict]:
        """获取主导航项"""
        try:
            if not self.page:
                print("❌ 页面未初始化")
                return []
            
            print("🔍 获取主导航项...")
            
            # 等待导航加载
            self.page.wait_for_selector("ul[data-rfd-droppable-id='nav-list']", timeout=10000)
            
            nav_items = self.page.query_selector_all("ul[data-rfd-droppable-id='nav-list'] li")
            
            main_navs = []
            
            for idx, item in enumerate(nav_items):
                try:
                    text_elem = item.query_selector("p")
                    if not text_elem:
                        continue
                    
                    text = text_elem.text_content()
                    if not text:
                        continue
                    
                    data_id = item.get_attribute("data-rfd-draggable-id")
                    data_type = text_elem.get_attribute("datatype")
                    is_active = "maxClassList_active__9kpsY" in (item.get_attribute("class") or "")
                    
                    main_navs.append({
                        "index": idx,
                        "text": text.strip(),
                        "data_id": data_id,
                        "data_type": data_type,
                        "is_active": is_active,
                        "element": item,
                        "text_element": text_elem
                    })
                    
                    print(f"  {idx + 1}. {text.strip()} (类型: {data_type}, 激活: {is_active})")
                    
                except Exception as e:
                    print(f"解析第 {idx} 个主导航项时出错: {e}")
                    continue
            
            print(f"✅ 找到 {len(main_navs)} 个主导航项")
            return main_navs
            
        except Exception as e:
            print(f"❌ 获取主导航项失败: {e}")
            return []
    
    def open_dropdown_menu(self, nav_item: Dict) -> bool:
        """打开下拉菜单 - 优化版"""
        try:
            if not self.page:
                return False
            
            print(f"📂 打开下拉菜单: {nav_item['text']}")
            
            # 点击主导航项
            nav_item["text_element"].click()
            
            # 等待下拉菜单出现（使用多种方式尝试）
            print("⏳ 等待下拉菜单加载...")
            
            # 方式1：等待任何可见的下拉菜单
            try:
                dropdown = self.page.wait_for_selector(
                    "div.mantine-HoverCard-dropdown[role='dialog']", 
                    timeout=5000,
                    state="visible"
                )
                if dropdown:
                    print("✅ 下拉菜单已打开（方式1）")
                    return True
            except:
                pass
            
            # 方式2：等待特定样式
            try:
                dropdown = self.page.wait_for_selector(
                    "div.mantine-HoverCard-dropdown[role='dialog'][style*='display: block']", 
                    timeout=5000
                )
                if dropdown:
                    print("✅ 下拉菜单已打开（方式2）")
                    return True
            except:
                pass
            
            # 方式3：直接查找可见的下拉菜单
            time.sleep(2)
            dropdowns = self.page.query_selector_all("div.mantine-HoverCard-dropdown[role='dialog']")
            
            for dropdown in dropdowns:
                style = dropdown.get_attribute("style") or ""
                if "display: none" not in style:
                    print("✅ 下拉菜单已打开（方式3）")
                    return True
            
            # 方式4：查找所有可能的下拉菜单，选择最大的一个
            all_dropdowns = self.page.query_selector_all("div[class*='mantine-HoverCard-dropdown']")
            if all_dropdowns:
                print(f"⚠️  找到 {len(all_dropdowns)} 个下拉菜单，选择第一个")
                return True
            
            print("❌ 所有方式都无法定位下拉菜单")
            return False
            
        except Exception as e:
            print(f"❌ 打开下拉菜单失败: {e}")
            return False
    
    def get_all_categories_and_subcategories(self) -> List[Dict]:
        """
        获取所有大类和细分项（包含三级结构）
        
        优化：使用更通用的选择器，避免依赖特定类名
        """
        try:
            print("📋 获取所有大类和细分项...")
            
            # 查找所有可能的容器
            containers = self.page.query_selector_all("div[class*='maxClassList_max_children_class__']")
            
            if not containers:
                print("❌ 未找到任何分类容器")
                return []
            
            all_categories = []
            
            for container_idx, container in enumerate(containers):
                try:
                    # 获取大类标题
                    title_elem = container.query_selector("span[class*='maxClassList_max_title__']")
                    if not title_elem:
                        continue
                    
                    title = title_elem.text_content()
                    if not title:
                        continue
                    
                    print(f"  📁 {title}")
                    
                    # 获取第一级细分项
                    first_level_items = container.query_selector_all("ul li")
                    
                    first_level_subcategories = []
                    
                    for item_idx, item in enumerate(first_level_items):
                        try:
                            text_elem = item.query_selector("span")
                            if not text_elem:
                                continue
                            
                            text = text_elem.text_content()
                            if not text:
                                continue
                            
                            is_active = "maxClassList_active__9kpsY" in (item.get_attribute("class") or "")
                            has_close_btn = item.query_selector("span[class*='maxClassList_close__']") is not None
                            
                            first_level_subcategories.append({
                                "text": text.strip(),
                                "index": item_idx,
                                "is_active": is_active,
                                "has_close_btn": has_close_btn,
                                "element": item
                            })
                            
                            print(f"    {item_idx + 1}. {text.strip()} {'✅' if is_active else ''}")
                            
                        except Exception as e:
                            print(f"解析第一级细分项 {container_idx}-{item_idx} 时出错: {e}")
                            continue
                    
                    category_data = {
                        "title": title.strip(),
                        "container_index": container_idx,
                        "first_level": first_level_subcategories,
                        "second_level": []  # 暂时为空，需要点击后获取
                    }
                    
                    all_categories.append(category_data)
                    
                except Exception as e:
                    print(f"解析容器 {container_idx} 时出错: {e}")
                    continue
            
            print(f"✅ 找到 {len(all_categories)} 个大类")
            return all_categories
            
        except Exception as e:
            print(f"❌ 获取分类结构失败: {e}")
            return []
    
    def click_first_level_and_get_second_level(self, first_level_item: Dict, category_title: str) -> List[Dict]:
        """
        点击第一级细分项，获取第二级细分项
        
        优化：点击后等待新内容出现，然后获取
        """
        try:
            print(f"🖱️  点击第一级细分项: [{category_title}] > {first_level_item['text']}")
            
            # 记录点击前的页面状态
            before_click_html = self.page.content()
            
            # 点击第一级细分项
            first_level_item["element"].click()
            
            # 等待新内容加载
            print("⏳ 等待第二级内容加载...")
            time.sleep(2)
            
            # 方式1：查找新出现的第二级容器
            second_level_containers = self.page.query_selector_all(
                "div[class*='maxClassList_max_children_class__']"
            )
            
            # 找到新增的容器（通过对比）
            new_containers = []
            for container in second_level_containers:
                # 检查是否包含"细分："标题
                title_elem = container.query_selector("span")
                if title_elem and "细分" in title_elem.text_content():
                    new_containers.append(container)
            
            if not new_containers:
                print("⚠️  未检测到第二级内容")
                return []
            
            # 获取第二级细分项
            second_level_subcategories = []
            
            for container in new_containers:
                # 验证标题
                title_elem = container.query_selector("span")
                if title_elem:
                    title_text = title_elem.text_content()
                    if "细分" in title_text:
                        print(f"      ✅ 找到第二级细分容器: {title_text}")
                        
                        # 获取第二级细分项
                        second_level_items = container.query_selector_all("ul li")
                        
                        for idx, item in enumerate(second_level_items):
                            try:
                                text_elem = item.query_selector("span")
                                if not text_elem:
                                    continue
                                
                                text = text_elem.text_content()
                                if not text:
                                    continue
                                
                                is_active = "maxClassList_active__9kpsY" in (item.get_attribute("class") or "")
                                has_close_btn = item.query_selector("span[class*='maxClassList_close__']") is not None
                                
                                second_level_subcategories.append({
                                    "text": text.strip(),
                                    "index": idx,
                                    "is_active": is_active,
                                    "has_close_btn": has_close_btn,
                                    "element": item
                                })
                                
                                print(f"        {idx + 1}. {text.strip()} {'✅' if is_active else ''}")
                                
                            except Exception as e:
                                print(f"解析第二级细分项 {idx} 时出错: {e}")
                                continue
            
            return second_level_subcategories
            
        except Exception as e:
            print(f"❌ 点击第一级细分项失败: {e}")
            return []
    
    def click_subcategory_and_verify(self, subcategory: Dict, screenshot_name: str) -> bool:
        """
        点击细分项并验证操作
        
        Args:
            subcategory: 细分项信息
            screenshot_name: 截图文件名
            
        Returns:
            bool: 是否成功
        """
        try:
            if not self.page:
                return False
            
            text = subcategory["text"]
            
            print(f"🖱️  点击细分项: {text}")
            
            # 点击细分项
            subcategory["element"].click()
            
            # 等待页面响应
            self.page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)  # 额外等待确保加载完成
            
            # 截图验证
            screenshot_path = f"screenshots/{screenshot_name}.png"
            os.makedirs("screenshots", exist_ok=True)
            
            if self.take_screenshot(screenshot_path):
                print(f"✅ 成功点击并截图: {text} -> {screenshot_path}")
                return True
            else:
                print(f"✅ 成功点击: {text} (截图失败)")
                return True
            
        except Exception as e:
            print(f"❌ 点击细分项失败: {e}")
            return False
    
    def process_all_navigations(self) -> Dict:
        """
        完整处理所有导航
        
        流程：
        1. 遍历每个主导航项
        2. 打开下拉菜单
        3. 获取所有大类和第一级细分项
        4. 对每个大类，点击第一级细分项获取第二级
        5. 点击所有细分项并截图验证
        """
        try:
            print("🚀 开始完整导航遍历和测试...")
            
            navigation_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "main_navigation": []
            }
            
            # 获取主导航
            main_navs = self.get_main_navigation_items()
            if not main_navs:
                return navigation_data
            
            # 遍历每个主导航项
            for nav_idx, nav_item in enumerate(main_navs):
                try:
                    print(f"\n{'='*70}")
                    print(f"📂 [{nav_idx + 1}/{len(main_navs)}] 处理主导航: {nav_item['text']}")
                    print(f"{'='*70}")
                    
                    nav_data = {
                        "text": nav_item["text"],
                        "data_id": nav_item["data_id"],
                        "data_type": nav_item["data_type"],
                        "is_active": nav_item["is_active"],
                        "categories": []
                    }
                    
                    # 打开下拉菜单
                    if not self.open_dropdown_menu(nav_item):
                        print(f"❌ 无法打开 {nav_item['text']} 的下拉菜单，跳过")
                        continue
                    
                    # 获取所有大类和第一级细分项
                    categories = self.get_all_categories_and_subcategories()
                    
                    if not categories:
                        print(f"⚠️  未找到分类数据，跳过 {nav_item['text']}")
                        continue
                    
                    # 遍历每个大类
                    for cat_idx, category in enumerate(categories):
                        try:
                            print(f"\n  📁 [{cat_idx + 1}/{len(categories)}] 大类: {category['title']}")
                            
                            category_data = {
                                "title": category["title"],
                                "first_level": [],
                                "second_level": []
                            }
                            
                            # 遍历第一级细分项
                            for first_idx, first_level_item in enumerate(category["first_level"]):
                                try:
                                    print(f"    🎯 [{first_idx + 1}/{len(category['first_level'])}] 第一级: {first_level_item['text']}")
                                    
                                    # 保存第一级数据
                                    category_data["first_level"].append({
                                        "text": first_level_item["text"],
                                        "is_active": first_level_item["is_active"],
                                        "has_close_btn": first_level_item["has_close_btn"]
                                    })
                                    
                                    # 点击第一级细分项，获取第二级
                                    second_level_items = self.click_first_level_and_get_second_level(
                                        first_level_item, category["title"]
                                    )
                                    
                                    # 如果有第二级，遍历并点击
                                    if second_level_items:
                                        print(f"      📋 找到 {len(second_level_items)} 个第二级细分项")
                                        
                                        for second_idx, second_level_item in enumerate(second_level_items):
                                            try:
                                                # 保存第二级数据
                                                category_data["second_level"].append({
                                                    "text": second_level_item["text"],
                                                    "is_active": second_level_item["is_active"],
                                                    "has_close_btn": second_level_item["has_close_btn"]
                                                })
                                                
                                                # 点击第二级细分项并截图验证
                                                screenshot_name = f"{nav_item['text']}_{category['title']}_{first_level_item['text']}_{second_level_item['text']}"
                                                self.click_subcategory_and_verify(second_level_item, screenshot_name)
                                                
                                                # 等待一下，准备下一次操作
                                                time.sleep(1)
                                                
                                            except Exception as e:
                                                print(f"❌ 处理第二级细分项 {second_idx} 时出错: {e}")
                                                continue
                                    else:
                                        # 没有第二级，直接点击第一级细分项
                                        screenshot_name = f"{nav_item['text']}_{category['title']}_{first_level_item['text']}"
                                        self.click_subcategory_and_verify(first_level_item, screenshot_name)
                                        
                                        time.sleep(1)
                                        
                                except Exception as e:
                                    print(f"❌ 处理第一级细分项 {first_idx} 时出错: {e}")
                                    continue
                            
                            nav_data["categories"].append(category_data)
                            
                        except Exception as e:
                            print(f"❌ 处理大类 {cat_idx} 时出错: {e}")
                            continue
                    
                    navigation_data["main_navigation"].append(nav_data)
                    
                    # 关闭下拉菜单，准备处理下一个主导航
                    self.page.keyboard.press("Escape")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ 处理主导航 {nav_item['text']} 时出错: {e}")
                    continue
            
            print(f"\n✅ 完整遍历和测试完成，共处理 {len(navigation_data['main_navigation'])} 个主导航项")
            return navigation_data
            
        except Exception as e:
            print(f"❌ 完整遍历失败: {e}")
            return {}
    
    def take_screenshot(self, filename: str) -> bool:
        """截图"""
        try:
            if self.page:
                self.page.screenshot(path=filename)
                return True
        except Exception as e:
            print(f"❌ 截图失败: {e}")
        return False
    
    def save_navigation_data(self, data: Dict, filename: str = "liuyunku_navigation.json") -> bool:
        """保存导航数据到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 导航数据已保存到: {filename}")
            return True
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")
            return False
    
    def close(self):
        """关闭应用和浏览器"""
        try:
            if self.page:
                self.page.close()
                print("✅ 页面已关闭")
        except:
            pass
        
        try:
            if self.browser:
                self.browser.close()
                print("✅ 浏览器已关闭")
        except:
            pass
        
        try:
            if self.playwright:
                self.playwright.stop()
                print("✅ Playwright已停止")
        except:
            pass
        
        try:
            if self.main_window:
                self.main_window.close()
                print("✅ 溜云库应用已关闭")
        except:
            pass
def main():
    """主函数"""
    automator = LiuYunKuNavigationAutomator()
    
    try:
        print("🚀 启动溜云库导航自动化器")
        print("=" * 60)
        
        # 1. 启动应用
        if not automator.start_application():
            print("❌ 应用启动失败")
            return
        
        # 2. 导航到在线素材
        if not automator.navigate_to_online_material():
            print("❌ 无法导航到在线素材")
            return
        
        # 3. 连接到浏览器
        if not automator.connect_to_browser():
            print("❌ 无法连接到浏览器")
            return
        
        # 4. 截图确认页面状态
        automator.take_screenshot("screenshots/initial_page.png")
        
        # 5. 完整遍历所有导航并测试
        print("\n🔍 开始完整导航遍历和测试...")
        navigation_data = automator.process_all_navigations()
        
        if navigation_data["main_navigation"]:
            automator.save_navigation_data(navigation_data)
            
            # 打印统计信息
            total_main = len(navigation_data["main_navigation"])
            total_categories = sum(len(nav["categories"]) for nav in navigation_data["main_navigation"])
            total_first_level = sum(
                sum(len(cat["first_level"]) for cat in nav["categories"]) 
                for nav in navigation_data["main_navigation"]
            )
            total_second_level = sum(
                sum(len(cat["second_level"]) for cat in nav["categories"]) 
                for nav in navigation_data["main_navigation"]
            )
            
            print(f"\n📊 最终统计:")
            print(f"  主导航项: {total_main}")
            print(f"  大类: {total_categories}")
            print(f"  第一级细分项: {total_first_level}")
            print(f"  第二级细分项: {total_second_level}")
            print(f"  截图数量: {total_first_level + total_second_level}")
        
        print("\n✅ 自动化测试完成!")
        
    except Exception as e:
        print(f"❌ 主程序执行失败: {e}")
    
    finally:
        # 询问是否关闭应用
        try:
            user_input = input("\n是否关闭溜云库应用? (y/n): ").lower().strip()
            if user_input == 'y':
                automator.close()
            else:
                print("保持应用运行")
                # 仍然需要清理Playwright资源
                if automator.playwright:
                    automator.playwright.stop()
        except:
            automator.close()
if __name__ == "__main__":
    main()