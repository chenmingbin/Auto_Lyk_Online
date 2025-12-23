import time
import json
import os
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Browser, Page, ElementHandle
from pywinauto import Application, Desktop
import psutil
class LiuYunKuNavigationAutomator:
    """溜云库导航自动化器 - 正确层级版"""
    
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
        """获取主导航项（类目列表）"""
        try:
            if not self.page:
                print("❌ 页面未初始化")
                return []
            
            print("🔍 获取类目列表...")
            
            # 等待导航加载
            self.page.wait_for_selector("ul[data-rfd-droppable-id='nav-list']", timeout=10000)
            
            nav_items = self.page.query_selector_all("ul[data-rfd-droppable-id='nav-list'] li")
            
            main_navs = []
            
            # 按指定顺序查找导航项
            target_order = ["3D模型", "SU模型", "材质", "贴图", "CAD", "灯光", "光域网", "PS免抠"]
            
            for target_text in target_order:
                found = False
                for idx, item in enumerate(nav_items):
                    try:
                        text_elem = item.query_selector("p")
                        if not text_elem:
                            continue
                        
                        text = text_elem.text_content()
                        if not text:
                            continue
                        
                        if text.strip() == target_text:
                            data_id = item.get_attribute("data-rfd-draggable-id")
                            data_type = text_elem.get_attribute("datatype")
                            is_active = "maxClassList_active__9kpsY" in (item.get_attribute("class") or "")
                            
                            nav_item = {
                                "index": idx,
                                "text": text.strip(),
                                "data_id": data_id,
                                "data_type": data_type,
                                "is_active": is_active,
                                "element": item,
                                "text_element": text_elem
                            }
                            
                            main_navs.append(nav_item)
                            print(f"  ✅ {text.strip()} (类型: {data_type}, 激活: {is_active})")
                            found = True
                            break
                            
                    except Exception as e:
                        continue
                
                if not found:
                    print(f"  ⚠️  未找到类目: {target_text}")
            
            print(f"✅ 找到 {len(main_navs)} 个类目")
            return main_navs
            
        except Exception as e:
            print(f"❌ 获取类目列表失败: {e}")
            return []
    
    def open_dropdown_menu(self, nav_item: Dict) -> bool:
        """打开类目下拉菜单"""
        try:
            if not self.page:
                return False
            
            print(f"📂 打开类目下拉菜单: {nav_item['text']}")
            
            # 点击类目
            nav_item["text_element"].click()
            
            # 等待下拉菜单出现
            print("⏳ 等待下拉菜单加载...")
            
            # 方式1：等待可见
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
            
            # 方式2：查找所有可见的下拉菜单
            time.sleep(2)
            dropdowns = self.page.query_selector_all("div.mantine-HoverCard-dropdown[role='dialog']")
            
            for dropdown in dropdowns:
                style = dropdown.get_attribute("style") or ""
                if "display: none" not in style:
                    print("✅ 下拉菜单已打开（方式2）")
                    return True
            
            print("❌ 无法定位下拉菜单")
            return False
            
        except Exception as e:
            print(f"❌ 打开下拉菜单失败: {e}")
            return False
    
    def get_all_big_categories(self) -> List[Dict]:
        """
        获取当前类目下的所有大类
        
        优化：从当前可见的下拉菜单中获取，避免跨类目
        """
        try:
            print("📋 获取当前类目的所有大类...")
            
            # 查找当前可见的下拉菜单
            dropdown = self.page.query_selector("div.mantine-HoverCard-dropdown[role='dialog']:not([style*='display: none'])")
            
            if not dropdown:
                print("❌ 未找到可见的下拉菜单")
                return []
            
            # 在下拉菜单内查找大类容器
            containers = dropdown.query_selector_all("div[class*='maxClassList_max_children_class__']")
            
            if not containers:
                print("❌ 下拉菜单内未找到大类容器")
                return []
            
            big_categories = []
            
            for container_idx, container in enumerate(containers):
                try:
                    # 查找大类标题
                    title_elem = container.query_selector("span[class*='maxClassList_max_title__']")
                    
                    if not title_elem:
                        # 如果没有特定class，查找容器内的第一个span
                        title_elem = container.query_selector("span")
                    
                    if not title_elem:
                        print(f"  ⚠️  容器 {container_idx} 未找到标题元素")
                        continue
                    
                    title = title_elem.text_content()
                    if not title or len(title.strip()) == 0:
                        print(f"  ⚠️  容器 {container_idx} 标题为空")
                        continue
                    
                    # 过滤掉"细分"相关的标题
                    if "细分" in title:
                        print(f"  ⚠️  跳过细分容器: {title}")
                        continue
                    
                    print(f"  📁 {title}")
                    
                    big_category = {
                        "title": title.strip(),
                        "container_index": container_idx,
                        "element": container,
                        "title_element": title_elem
                    }
                    
                    big_categories.append(big_category)
                    
                except Exception as e:
                    print(f"  ❌ 解析容器 {container_idx} 时出错: {e}")
                    continue
            
            print(f"✅ 找到 {len(big_categories)} 个大类")
            return big_categories
            
        except Exception as e:
            print(f"❌ 获取大类失败: {e}")
            return []
    
    def click_big_category_and_get_subcategories(self, big_category: Dict) -> List[Dict]:
        """
        点击大类，触发细分项显示，并获取细分项
        
        优化：点击大类后等待细分项容器出现
        """
        try:
            print(f"    🖱️  点击大类: {big_category['title']}")
            
            # 查找大类下的可点击项（通常是第一个li）
            clickable_items = big_category["element"].query_selector_all("ul li")
            
            if not clickable_items:
                print(f"    ❌ 未找到可点击项")
                return []
            
            # 记录点击前的细分项容器数量
            before_sub_containers = self.page.query_selector_all(
                "div[class*='maxClassList_max_children_class__'] span[class*='maxClassList_max_title__']"
            )
            before_sub_count = len([s for s in before_sub_containers if "细分" in s.text_content()])
            
            print(f"    📊 点击前细分容器数量: {before_sub_count}")
            
            # 点击第一个可点击项（通常是"全部"）
            clickable_items[0].click()
            
            # 等待细分项容器出现
            print("    ⏳ 等待细分项容器出现...")
            time.sleep(2)
            
            # 检查是否有新的细分项容器出现
            after_sub_containers = self.page.query_selector_all(
                "div[class*='maxClassList_max_children_class__'] span[class*='maxClassList_max_title__']"
            )
            after_sub_count = len([s for s in after_sub_containers if "细分" in s.text_content()])
            
            print(f"    📊 点击后细分容器数量: {after_sub_count}")
            
            if after_sub_count <= before_sub_count:
                print(f"    ⚠️  未检测到新的细分项容器")
                return []
            
            # 获取细分项容器
            sub_containers = self.page.query_selector_all("div[class*='maxClassList_max_children_class__']")
            
            # 找到包含"细分："标题的容器
            subcategories = []
            
            for container in sub_containers:
                title_elem = container.query_selector("span")
                if title_elem and "细分" in title_elem.text_content():
                    print(f"    ✅ 找到细分项容器: {title_elem.text_content()}")
                    
                    # 获取细分项列表
                    sub_items = container.query_selector_all("ul li")
                    
                    for idx, item in enumerate(sub_items):
                        try:
                            text_elem = item.query_selector("span")
                            if not text_elem:
                                continue
                            
                            text = text_elem.text_content()
                            if not text:
                                continue
                            
                            # 检查激活状态
                            is_active = "maxClassList_active__9kpsY" in (item.get_attribute("class") or "")
                            
                            # 检查是否有关闭按钮
                            has_close_btn = item.query_selector("span[class*='maxClassList_close__']") is not None
                            
                            subcategory = {
                                "text": text.strip(),
                                "index": idx,
                                "is_active": is_active,
                                "has_close_btn": has_close_btn,
                                "element": item
                            }
                            
                            subcategories.append(subcategory)
                            print(f"      {idx + 1}. {text.strip()} {'✅' if is_active else ''} {'[X]' if has_close_btn else ''}")
                            
                        except Exception as e:
                            print(f"      ❌ 解析细分项 {idx} 时出错: {e}")
                            continue
                    
                    break
            
            if not subcategories:
                print(f"    ❌ 未找到细分项")
            
            return subcategories
            
        except Exception as e:
            print(f"❌ 点击大类失败: {e}")
            return []
    
    def click_subcategory_and_screenshot(self, subcategory: Dict, nav_text: str, big_category_title: str) -> bool:
        """点击细分项并截图"""
        try:
            if not self.page:
                return False
            
            text = subcategory["text"]
            
            print(f"      🖱️  点击细分项: {text}")
            
            # 点击细分项
            subcategory["element"].click()
            
            # 等待页面响应
            self.page.wait_for_load_state("networkidle", timeout=15000)
            time.sleep(2)
            
            # 生成截图文件名
            filename = f"screenshots/{nav_text}_{big_category_title}_{text}.png"
            
            # 确保目录存在
            os.makedirs("screenshots", exist_ok=True)
            
            # 截图
            if self.page.screenshot(path=filename):
                print(f"      📸 截图已保存: {filename}")
                return True
            else:
                print(f"      ⚠️  截图失败，但点击成功")
                return True
            
        except Exception as e:
            print(f"      ❌ 点击细分项失败: {e}")
            return False
    
    def process_all_navigations_in_order(self) -> Dict:
        """
        按指定顺序处理所有导航
        
        完整流程：
        1. 遍历类目列表
        2. 对每个类目：
           a. 打开下拉菜单
           b. 获取所有大类
           c. 对每个大类：
              - 点击大类触发细分项
              - 获取细分项列表
              - 遍历细分项，点击并截图
           d. 完成当前类目后关闭下拉菜单
        3. 进入下一个类目
        """
        try:
            print("🚀 开始按序处理所有导航...")
            
            navigation_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "main_navigation": []
            }
            
            # 1. 获取类目列表
            main_navs = self.get_main_navigation_items()
            if not main_navs:
                print("❌ 未找到任何类目")
                return navigation_data
            
            # 2. 按顺序处理每个类目
            for nav_idx, nav_item in enumerate(main_navs):
                try:
                    print(f"\n{'='*80}")
                    print(f"📂 [{nav_idx + 1}/{len(main_navs)}] 处理类目: {nav_item['text']}")
                    print(f"{'='*80}")
                    
                    nav_data = {
                        "text": nav_item["text"],
                        "data_id": nav_item["data_id"],
                        "data_type": nav_item["data_type"],
                        "is_active": nav_item["is_active"],
                        "big_categories": []
                    }
                    
                    # 步骤a: 打开下拉菜单
                    if not self.open_dropdown_menu(nav_item):
                        print(f"❌ 无法打开类目 '{nav_item['text']}' 的下拉菜单，跳过")
                        continue
                    
                    # 步骤b: 获取所有大类
                    big_categories = self.get_all_big_categories()
                    if not big_categories:
                        print(f"⚠️  未找到大类，跳过类目 '{nav_item['text']}'")
                        continue
                    
                    # 步骤c: 对每个大类进行处理
                    for big_idx, big_category in enumerate(big_categories):
                        try:
                            print(f"\n  📁 [{big_idx + 1}/{len(big_categories)}] 大类: {big_category['title']}")
                            
                            # 🚨 特殊规则：跳过"贴图类目-免抠素材大类"
                            if nav_item['text'] == "贴图" and big_category['title'] == "免抠素材":
                                print(f"  ⚠️  跳过特殊处理的大类: {nav_item['text']} - {big_category['title']}")
                                continue
                            
                            # 点击大类，触发细分项显示，并获取细分项
                            subcategories = self.click_big_category_and_get_subcategories(big_category)
                            
                            if not subcategories:
                                print(f"    ⚠️  未找到细分项，跳过此大类")
                                continue
                            
                            # 保存大类数据
                            big_category_data = {
                                "title": big_category["title"],
                                "subcategories": []
                            }
                            
                            # 遍历细分项
                            for sub_idx, subcategory in enumerate(subcategories):
                                try:
                                    print(f"    🎯 [{sub_idx + 1}/{len(subcategories)}] 细分项: {subcategory['text']}")
                                    
                                    # 保存细分项数据
                                    big_category_data["subcategories"].append({
                                        "text": subcategory["text"],
                                        "is_active": subcategory["is_active"],
                                        "has_close_btn": subcategory["has_close_btn"]
                                    })
                                    
                                    # 点击细分项并截图
                                    self.click_subcategory_and_screenshot(
                                        subcategory, 
                                        nav_item['text'], 
                                        big_category['title']
                                    )
                                    
                                    # 等待一下，准备下一次操作
                                    time.sleep(1)
                                    
                                except Exception as e:
                                    print(f"    ❌ 处理细分项 {sub_idx} 时出错: {e}")
                                    continue
                            
                            nav_data["big_categories"].append(big_category_data)
                            
                        except Exception as e:
                            print(f"❌ 处理大类 {big_idx} 时出错: {e}")
                            continue
                    
                    navigation_data["main_navigation"].append(nav_data)
                    
                    # 步骤d: 完成当前类目后，关闭下拉菜单
                    print(f"\n  ✅ 完成类目 '{nav_item['text']}' 的所有大类处理")
                    self.page.keyboard.press("Escape")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ 处理类目 {nav_item['text']} 时出错: {e}")
                    continue
            
            print(f"\n✅ 按序处理完成，共处理 {len(navigation_data['main_navigation'])} 个类目")
            return navigation_data
            
        except Exception as e:
            print(f"❌ 按序处理失败: {e}")
            return {}
    
    def save_navigation_data(self, data: Dict, filename: str = "liuyunku_navigation_correct.json") -> bool:
        """保存导航数据到文件"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✅ 导航数据已保存到: {filename}")
            return True
        except Exception as e:
            print(f"❌ 保存数据失败: {e}")
            return False
    
    def take_initial_screenshot(self) -> bool:
        """拍摄初始页面截图"""
        try:
            os.makedirs("screenshots", exist_ok=True)
            return self.page.screenshot(path="screenshots/initial_page.png")
        except Exception as e:
            print(f"❌ 初始截图失败: {e}")
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
    """主函数 - 正确层级版"""
    automator = LiuYunKuNavigationAutomator()
    
    try:
        print("🚀 启动溜云库导航自动化器（正确层级版）")
        print("=" * 60)
        
        # 1. 启动溜云库 → 导航到在线素材 → 连接浏览器
        print("\n📍 步骤1: 启动应用并导航到在线素材")
        if not automator.start_application():
            print("❌ 应用启动失败")
            return
        
        if not automator.navigate_to_online_material():
            print("❌ 无法导航到在线素材")
            return
        
        print("\n🌐 步骤2: 连接到浏览器")
        if not automator.connect_to_browser():
            print("❌ 无法连接到浏览器")
            return
        
        # 拍摄初始截图
        automator.take_initial_screenshot()
        
        # 2. 获取类目列表
        print("\n🔍 步骤3: 获取类目列表")
        
        # 3. 按顺序处理每个类目
        print("\n🎯 步骤4: 按序处理所有类目")
        navigation_data = automator.process_all_navigations_in_order()
        
        # 4. 保存完整数据到JSON
        print("\n💾 步骤5: 保存数据")
        if navigation_data["main_navigation"]:
            automator.save_navigation_data(navigation_data)
            
            # 打印统计信息
            total_main = len(navigation_data["main_navigation"])
            total_big = sum(len(nav["big_categories"]) for nav in navigation_data["main_navigation"])
            total_subcategories = sum(
                sum(len(big["subcategories"]) for big in nav["big_categories"]) 
                for nav in navigation_data["main_navigation"]
            )
            
            print(f"\n📊 最终统计:")
            print(f"  类目数量: {total_main}")
            print(f"  大类数量: {total_big}")
            print(f"  细分项数量: {total_subcategories}")
            print(f"  截图数量: {total_subcategories}")
        
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