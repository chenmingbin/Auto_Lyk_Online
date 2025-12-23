import time
import json
import os
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Browser, Page, ElementHandle
from pywinauto import Application, Desktop
import psutil
class LiuYunKuNavigationAutomator:
    """溜云库导航自动化器 - 优化版"""
    
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
                        "element": item
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
    
    def open_dropdown_menu(self, nav_item: Dict) -> Optional[ElementHandle]:
        """打开下拉菜单 - 优化版（只使用备用方式）"""
        try:
            if not self.page:
                return None
            
            print(f"📂 打开下拉菜单: {nav_item['text']}")
            
            text_elem = nav_item["element"].query_selector("p")
            if not text_elem:
                return None
            
            # 点击打开下拉菜单
            text_elem.click()
            
            # 优化：直接使用备用方式，等待2秒确保加载完成
            print("⏳ 等待下拉菜单加载...")
            time.sleep(2)
            
            # 查找下拉菜单（使用更通用的选择器）
            dropdown = self.page.query_selector("div.mantine-HoverCard-dropdown[role='dialog']")
            
            if dropdown:
                # 检查是否可见
                style = dropdown.get_attribute("style") or ""
                if "display: none" not in style:
                    print("✅ 下拉菜单已打开")
                    return dropdown
                else:
                    print("⚠️  下拉菜单存在但不可见")
                    return None
            else:
                print("❌ 未找到下拉菜单")
                return None
                
        except Exception as e:
            print(f"❌ 打开下拉菜单失败: {e}")
            return None
    
    def get_categories_and_subcategories(self, dropdown: ElementHandle) -> List[Dict]:
        """
        获取大类和细分项（二级遍历）
        
        结构：
        - 大类容器
          - 大类标题
          - 大类细分项列表
        """
        try:
            if not dropdown:
                return []
            
            print("📋 获取大类和细分项...")
            
            # 获取大类容器
            category_containers = dropdown.query_selector_all(
                "div[class*='maxClassList_max_children_class__']")
            
            all_categories = []
            
            for cat_idx, container in enumerate(category_containers):
                try:
                    # 获取大类标题
                    title_elem = container.query_selector("span[class*='maxClassList_max_title__']")
                    title = title_elem.text_content() if title_elem else f"大类{cat_idx + 1}"
                    
                    print(f"  📁 {title}")
                    
                    # 获取大类下的细分项（第一级）
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
                            print(f"解析第一级细分项 {cat_idx}-{item_idx} 时出错: {e}")
                            continue
                    
                    # 检查是否有第二级细分项（点击大类后出现的）
                    second_level_data = self.get_second_level_subcategories(container, title)
                    
                    category_data = {
                        "title": title.strip(),
                        "first_level": first_level_subcategories,
                        "second_level": second_level_data
                    }
                    
                    all_categories.append(category_data)
                    
                except Exception as e:
                    print(f"解析大类 {cat_idx} 时出错: {e}")
                    continue
            
            print(f"✅ 找到 {len(all_categories)} 个大类")
            return all_categories
            
        except Exception as e:
            print(f"❌ 获取分类结构失败: {e}")
            return []
    
    def get_second_level_subcategories(self, category_container: ElementHandle, category_title: str) -> List[Dict]:
        """
        获取第二级细分项（点击大类后出现的）
        
        优化：使用备用方式，通过文本匹配定位
        """
        try:
            print(f"    🔍 获取 [{category_title}] 的第二级细分项...")
            
            # 点击大类项（点击"全部"或第一个项）来触发第二级内容加载
            # 注意：这里我们不实际点击，而是直接查找可能存在的第二级结构
            
            # 方法1：查找可能存在的第二级容器（在当前大类容器内）
            second_level_container = category_container.query_selector(
                "div[class*='maxClassList_max_children_class__']"
            )
            
            if not second_level_container:
                # 方法2：查找页面上新出现的第二级容器（可能在下拉菜单外）
                second_level_container = self.page.query_selector(
                    "div[class*='maxClassList_max_children_class__']"
                )
            
            if second_level_container:
                # 检查是否包含"细分："标题
                title_elem = second_level_container.query_selector("span")
                if title_elem and "细分" in title_elem.text_content():
                    print(f"      ✅ 找到第二级细分容器")
                    
                    # 获取第二级细分项
                    second_level_items = second_level_container.query_selector_all("ul li")
                    
                    second_level_subcategories = []
                    
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
                                "has_close_btn": has_close_btn
                            })
                            
                            print(f"        {idx + 1}. {text.strip()} {'✅' if is_active else ''}")
                            
                        except Exception as e:
                            print(f"解析第二级细分项 {idx} 时出错: {e}")
                            continue
                    
                    return second_level_subcategories
            
            print(f"      ⚠️  未找到第二级细分项")
            return []
            
        except Exception as e:
            print(f"❌ 获取第二级细分项失败: {e}")
            return []
    
    def click_and_get_second_level(self, first_level_item: Dict, category_title: str) -> List[Dict]:
        """
        点击第一级细分项，获取第二级细分项
        
        Args:
            first_level_item: 第一级细分项元素
            category_title: 大类标题
            
        Returns:
            List[Dict]: 第二级细分项列表
        """
        try:
            print(f"🖱️  点击第一级细分项: [{category_title}] > {first_level_item['text']}")
            
            # 点击第一级细分项
            first_level_item["element"].click()
            
            # 等待第二级内容加载
            time.sleep(2)
            
            # 查找第二级细分容器
            second_level_container = self.page.query_selector(
                "div[class*='maxClassList_max_children_class__']"
            )
            
            if second_level_container:
                # 验证是否包含"细分："标题
                title_elem = second_level_container.query_selector("span")
                if title_elem and "细分" in title_elem.text_content():
                    print(f"      ✅ 第二级内容已加载")
                    
                    # 获取第二级细分项
                    second_level_items = second_level_container.query_selector_all("ul li")
                    
                    second_level_subcategories = []
                    
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
            
            print(f"⚠️  未找到第二级细分内容")
            return []
            
        except Exception as e:
            print(f"❌ 点击第一级细分项失败: {e}")
            return []
    
    def scrape_all_navigation(self) -> Dict:
        """完整遍历所有导航结构（包含三级结构）"""
        try:
            print("🚀 开始完整导航遍历...")
            
            navigation_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "main_navigation": []
            }
            
            # 获取主导航
            main_navs = self.get_main_navigation_items()
            if not main_navs:
                return navigation_data
            
            # 遍历每个主导航
            for nav_item in main_navs:
                try:
                    print(f"\n{'='*60}")
                    print(f"📂 处理主导航: {nav_item['text']}")
                    print(f"{'='*60}")
                    
                    nav_data = {
                        "text": nav_item["text"],
                        "data_id": nav_item["data_id"],
                        "data_type": nav_item["data_type"],
                        "is_active": nav_item["is_active"],
                        "categories": []
                    }
                    
                    # 打开下拉菜单
                    dropdown = self.open_dropdown_menu(nav_item)
                    if not dropdown:
                        print(f"❌ 无法打开 {nav_item['text']} 的下拉菜单")
                        continue
                    
                    # 获取大类和细分项结构
                    categories = self.get_categories_and_subcategories(dropdown)
                    
                    # 遍历每个大类，获取完整的二级细分项
                    for category in categories:
                        category_data = {
                            "title": category["title"],
                            "first_level": [],
                            "second_level": []
                        }
                        
                        # 保存第一级细分项
                        for first_level_item in category["first_level"]:
                            category_data["first_level"].append({
                                "text": first_level_item["text"],
                                "is_active": first_level_item["is_active"],
                                "has_close_btn": first_level_item["has_close_btn"]
                            })
                        
                        # 如果有第二级细分项，直接保存
                        if category["second_level"]:
                            for second_level_item in category["second_level"]:
                                category_data["second_level"].append({
                                    "text": second_level_item["text"],
                                    "is_active": second_level_item["is_active"],
                                    "has_close_btn": second_level_item["has_close_btn"]
                                })
                        
                        nav_data["categories"].append(category_data)
                    
                    navigation_data["main_navigation"].append(nav_data)
                    
                    # 关闭下拉菜单
                    self.page.keyboard.press("Escape")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"处理主导航 {nav_item['text']} 时出错: {e}")
                    continue
            
            print(f"\n✅ 完整遍历完成，共处理 {len(navigation_data['main_navigation'])} 个主导航项")
            return navigation_data
            
        except Exception as e:
            print(f"❌ 完整遍历失败: {e}")
            return {}
    
    def test_specific_navigation(self, main_nav_text: str, first_level_text: str, second_level_text: str = None) -> bool:
        """测试特定导航路径（支持三级）"""
        try:
            if second_level_text:
                print(f"\n🎯 测试导航路径: {main_nav_text} > {first_level_text} > {second_level_text}")
            else:
                print(f"\n🎯 测试导航路径: {main_nav_text} > {first_level_text}")
            
            # 获取主导航
            main_navs = self.get_main_navigation_items()
            
            # 找到目标主导航
            target_nav = None
            for nav in main_navs:
                if nav["text"] == main_nav_text:
                    target_nav = nav
                    break
            
            if not target_nav:
                print(f"❌ 未找到主导航: {main_nav_text}")
                return False
            
            # 打开下拉菜单
            dropdown = self.open_dropdown_menu(target_nav)
            if not dropdown:
                print(f"❌ 无法打开下拉菜单: {main_nav_text}")
                return False
            
            # 获取分类结构
            categories = self.get_categories_and_subcategories(dropdown)
            
            # 找到目标大类
            target_category = None
            for category in categories:
                if category["title"] == first_level_text:
                    target_category = category
                    break
            
            if not target_category:
                print(f"❌ 未找到大类: {first_level_text}")
                return False
            
            # 如果有第二级目标，进行二级导航
            if second_level_text:
                # 点击第一级细分项（点击"全部"或第一个项来触发第二级）
                first_level_item = target_category["first_level"][0]  # 点击第一个项
                
                # 点击并获取第二级细分项
                second_level_items = self.click_and_get_second_level(first_level_item, first_level_text)
                
                # 找到目标第二级细分项
                target_second_level = None
                for item in second_level_items:
                    if item["text"] == second_level_text:
                        target_second_level = item
                        break
                
                if not target_second_level:
                    print(f"❌ 未找到第二级细分项: {second_level_text}")
                    return False
                
                # 点击第二级细分项
                success = self.click_subcategory(target_second_level)
                
            else:
                # 只点击第一级细分项
                first_level_item = target_category["first_level"][0]
                success = self.click_subcategory(first_level_item)
            
            if success:
                print(f"✅ 导航测试成功: {main_nav_text} > {first_level_text}" + 
                      (f" > {second_level_text}" if second_level_text else ""))
            else:
                print(f"❌ 导航测试失败")
            
            return success
            
        except Exception as e:
            print(f"❌ 导航测试失败: {e}")
            return False
    
    def click_subcategory(self, subcategory: Dict) -> bool:
        """点击细分项"""
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
            
            print(f"✅ 成功点击: {text}")
            return True
            
        except Exception as e:
            print(f"❌ 点击细分项失败: {e}")
            return False
    
    def take_screenshot(self, filename: str = "screenshot.png") -> bool:
        """截图"""
        try:
            if self.page:
                self.page.screenshot(path=filename)
                print(f"📸 截图已保存: {filename}")
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
        automator.take_screenshot("initial_page.png")
        
        # 5. 方式1：完整遍历所有导航（包含三级结构）
        print("\n🔍 开始完整导航遍历...")
        navigation_data = automator.scrape_all_navigation()
        
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
            
            print(f"\n📊 遍历统计:")
            print(f"  主导航项: {total_main}")
            print(f"  大类: {total_categories}")
            print(f"  第一级细分项: {total_first_level}")
            print(f"  第二级细分项: {total_second_level}")
        
        # 6. 方式2：测试特定导航路径（三级）
        print("\n🎯 测试特定导航路径...")
        test_cases = [
            ("3D模型", "大类：", "沙发"),  # 三级路径
            ("3D模型", "大类：", "椅凳"),  # 三级路径
            ("材质", "大类：", "全部"),    # 二级路径
        ]
        
        for case in test_cases:
            if len(case) == 3:
                automator.test_specific_navigation(case[0], case[1], case[2])
            else:
                automator.test_specific_navigation(case[0], case[1])
            
            automator.take_screenshot(f"test_{case[0]}_{case[1]}_{case[2] if len(case) > 2 else ''}.png")
            time.sleep(3)  # 等待页面稳定
        
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