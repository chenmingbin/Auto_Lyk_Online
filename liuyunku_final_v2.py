import time
import json
import os
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Browser, Page, ElementHandle
from pywinauto import Application, Desktop
import psutil
class LiuYunKuNavigationAutomator:
    """溜云库导航自动化器 - 最终优化版V2"""
    
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
        """获取主导航项（按指定顺序）"""
        try:
            if not self.page:
                print("❌ 页面未初始化")
                return []
            
            print("🔍 获取主导航项...")
            
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
                    print(f"  ⚠️  未找到主导航项: {target_text}")
            
            print(f"✅ 找到 {len(main_navs)} 个主导航项")
            return main_navs
            
        except Exception as e:
            print(f"❌ 获取主导航项失败: {e}")
            return []
    
    def open_dropdown_menu(self, nav_item: Dict) -> bool:
        """打开下拉菜单"""
        try:
            if not self.page:
                return False
            
            print(f"📂 打开下拉菜单: {nav_item['text']}")
            
            # 点击主导航项
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
    
    def get_all_categories_from_dropdown(self) -> List[Dict]:
        """
        从下拉菜单中获取所有大类
        
        优化：直接从下拉菜单容器中查找，避免获取到其他类目的大类
        """
        try:
            print("📋 从下拉菜单获取所有大类...")
            
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
            
            categories = []
            
            for container_idx, container in enumerate(containers):
                try:
                    # 方式1：查找标题span（可能有特定class）
                    title_elem = container.query_selector("span[class*='maxClassList_max_title__']")
                    
                    # 方式2：如果方式1失败，查找容器内的第一个span
                    if not title_elem:
                        title_elem = container.query_selector("span")
                    
                    # 方式3：查找所有span，找到非"细分"的文本
                    if not title_elem:
                        all_spans = container.query_selector_all("span")
                        for span in all_spans:
                            text = span.text_content()
                            if text and len(text.strip()) > 0 and "细分" not in text:
                                title_elem = span
                                break
                    
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
                    
                    category_data = {
                        "title": title.strip(),
                        "container_index": container_idx,
                        "element": container,
                        "title_element": title_elem
                    }
                    
                    categories.append(category_data)
                    
                except Exception as e:
                    print(f"  ❌ 解析容器 {container_idx} 时出错: {e}")
                    continue
            
            print(f"✅ 找到 {len(categories)} 个大类")
            return categories
            
        except Exception as e:
            print(f"❌ 获取大类失败: {e}")
            return []
    
    def click_category_and_get_subcategories(self, category: Dict, max_wait_time: float = 5.0) -> List[Dict]:
        """
        点击大类触发细分项菜单，并获取细分项
        
        优化：点击后等待新内容出现，然后获取细分项
        """
        try:
            print(f"    🖱️  点击大类触发细分项: {category['title']}")
            
            # 查找大类下的可点击项（通常是第一个li）
            clickable_items = category["element"].query_selector_all("ul li")
            
            if not clickable_items:
                print(f"    ❌ 未找到可点击项")
                return []
            
            # 记录点击前的容器数量
            before_containers = self.page.query_selector_all(
                "div[class*='maxClassList_max_children_class__']"
            )
            before_count = len(before_containers)
            
            print(f"    📊 点击前容器数量: {before_count}")
            
            # 尝试点击每个可能的项，直到出现细分项
            found_subcategories = False
            subcategories = []
            
            for item_idx, item in enumerate(clickable_items):
                try:
                    print(f"      尝试点击第 {item_idx + 1} 项...")
                    
                    # 点击该项
                    item.click()
                    
                    # 等待新内容加载
                    time.sleep(2)
                    
                    # 检查是否有新容器出现
                    after_containers = self.page.query_selector_all(
                        "div[class*='maxClassList_max_children_class__']"
                    )
                    after_count = len(after_containers)
                    
                    print(f"      点击后容器数量: {after_count}")
                    
                    if after_count > before_count:
                        print(f"      ✅ 检测到 {after_count - before_count} 个新容器")
                        
                        # 获取细分项
                        subcategories = self.extract_subcategories_from_new_containers(
                            before_count, after_containers
                        )
                        
                        if subcategories:
                            found_subcategories = True
                            break
                        else:
                            print(f"      ⚠️  新容器中未找到细分项")
                    
                    # 如果没有新容器，可能是点击后内容更新了，尝试获取当前容器内的细分项
                    if not found_subcategories:
                        subcategories = self.extract_subcategories_from_container(category["element"])
                        if subcategories:
                            found_subcategories = True
                            break
                    
                except Exception as e:
                    print(f"      ❌ 点击第 {item_idx + 1} 项失败: {e}")
                    continue
            
            if not found_subcategories:
                print(f"    ❌ 所有点击尝试都未找到细分项")
                return []
            
            return subcategories
            
        except Exception as e:
            print(f"❌ 点击大类失败: {e}")
            return []
    
    def extract_subcategories_from_new_containers(self, before_count: int, all_containers: List) -> List[Dict]:
        """从新出现的容器中提取细分项"""
        try:
            subcategories = []
            
            # 从新容器开始查找
            for idx in range(before_count, len(all_containers)):
                container = all_containers[idx]
                
                # 检查是否包含"细分"标题
                title_elem = container.query_selector("span")
                if title_elem and "细分" in title_elem.text_content():
                    print(f"        ✅ 找到细分容器: {title_elem.text_content()}")
                    
                    # 获取细分项
                    sub_items = container.query_selector_all("ul li")
                    
                    for sub_idx, item in enumerate(sub_items):
                        try:
                            text_elem = item.query_selector("span")
                            if not text_elem:
                                continue
                            
                            text = text_elem.text_content()
                            if not text:
                                continue
                            
                            is_active = "maxClassList_active__9kpsY" in (item.get_attribute("class") or "")
                            has_close_btn = item.query_selector("span[class*='maxClassList_close__']") is not None
                            
                            subcategories.append({
                                "text": text.strip(),
                                "index": sub_idx,
                                "is_active": is_active,
                                "has_close_btn": has_close_btn,
                                "element": item
                            })
                            
                            print(f"          {sub_idx + 1}. {text.strip()} {'✅' if is_active else ''}")
                            
                        except Exception as e:
                            print(f"          ❌ 解析细分项 {sub_idx} 时出错: {e}")
                            continue
                    
                    break
            
            return subcategories
            
        except Exception as e:
            print(f"❌ 从新容器提取细分项失败: {e}")
            return []
    
    def extract_subcategories_from_container(self, category_container) -> List[Dict]:
        """从大类容器中直接提取细分项（用于没有新容器出现的情况）"""
        try:
            subcategories = []
            
            # 查找容器内所有可能的细分项
            all_items = category_container.query_selector_all("ul li")
            
            for idx, item in enumerate(all_items):
                try:
                    text_elem = item.query_selector("span")
                    if not text_elem:
                        continue
                    
                    text = text_elem.text_content()
                    if not text:
                        continue
                    
                    # 跳过第一个项（通常是"全部"）
                    if idx == 0 and len(all_items) > 1:
                        continue
                    
                    is_active = "maxClassList_active__9kpsY" in (item.get_attribute("class") or "")
                    has_close_btn = item.query_selector("span[class*='maxClassList_close__']") is not None
                    
                    subcategories.append({
                        "text": text.strip(),
                        "index": idx,
                        "is_active": is_active,
                        "has_close_btn": has_close_btn,
                        "element": item
                    })
                    
                    print(f"          {idx + 1}. {text.strip()} {'✅' if is_active else ''}")
                    
                except Exception as e:
                    print(f"          ❌ 解析项 {idx} 时出错: {e}")
                    continue
            
            return subcategories
            
        except Exception as e:
            print(f"❌ 从容器提取细分项失败: {e}")
            return []
    
    def click_subcategory_and_screenshot(self, subcategory: Dict, nav_text: str, category_title: str) -> bool:
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
            filename = f"screenshots/{nav_text}_{category_title}_{text}.png"
            
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
        """按指定顺序处理所有导航"""
        try:
            print("🚀 开始按序处理所有导航...")
            
            navigation_data = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "main_navigation": []
            }
            
            # 获取主导航项（按指定顺序）
            main_navs = self.get_main_navigation_items()
            if not main_navs:
                print("❌ 未找到任何主导航项")
                return navigation_data
            
            # 按顺序处理每个主导航项
            for nav_idx, nav_item in enumerate(main_navs):
                try:
                    print(f"\n{'='*80}")
                    print(f"📂 [{nav_idx + 1}/{len(main_navs)}] 处理主导航: {nav_item['text']}")
                    print(f"{'='*80}")
                    
                    nav_data = {
                        "text": nav_item["text"],
                        "data_id": nav_item["data_id"],
                        "data_type": nav_item["data_type"],
                        "is_active": nav_item["is_active"],
                        "categories": []
                    }
                    
                    # 步骤a: 打开下拉菜单
                    if not self.open_dropdown_menu(nav_item):
                        print(f"❌ 无法打开 {nav_item['text']} 的下拉菜单，跳过")
                        continue
                    
                    # 步骤b: 获取所有大类（从当前下拉菜单）
                    categories = self.get_all_categories_from_dropdown()
                    if not categories:
                        print(f"⚠️  未找到大类，跳过 {nav_item['text']}")
                        continue
                    
                    # 步骤c: 对每个大类进行处理
                    for cat_idx, category in enumerate(categories):
                        try:
                            print(f"\n  📁 [{cat_idx + 1}/{len(categories)}] 大类: {category['title']}")
                            
                            # 🚨 特殊规则：跳过"贴图类目-免抠素材大类"
                            if nav_item['text'] == "贴图" and category['title'] == "免抠素材":
                                print(f"  ⚠️  跳过特殊处理的大类: {nav_item['text']} - {category['title']}")
                                continue
                            
                            # 点击大类触发细分项菜单，并获取细分项
                            subcategories = self.click_category_and_get_subcategories(category)
                            
                            if not subcategories:
                                print(f"    ⚠️  未找到细分项，跳过此大类")
                                continue
                            
                            # 保存大类数据
                            category_data = {
                                "title": category["title"],
                                "subcategories": []
                            }
                            
                            # 遍历细分项
                            for sub_idx, subcategory in enumerate(subcategories):
                                try:
                                    print(f"    🎯 [{sub_idx + 1}/{len(subcategories)}] 细分项: {subcategory['text']}")
                                    
                                    # 保存细分项数据
                                    category_data["subcategories"].append({
                                        "text": subcategory["text"],
                                        "is_active": subcategory["is_active"],
                                        "has_close_btn": subcategory["has_close_btn"]
                                    })
                                    
                                    # 点击细分项并截图
                                    self.click_subcategory_and_screenshot(
                                        subcategory, 
                                        nav_item['text'], 
                                        category['title']
                                    )
                                    
                                    # 等待一下，准备下一次操作
                                    time.sleep(1)
                                    
                                except Exception as e:
                                    print(f"    ❌ 处理细分项 {sub_idx} 时出错: {e}")
                                    continue
                            
                            nav_data["categories"].append(category_data)
                            
                        except Exception as e:
                            print(f"❌ 处理大类 {cat_idx} 时出错: {e}")
                            continue
                    
                    navigation_data["main_navigation"].append(nav_data)
                    
                    # 步骤d: 完成当前类目后，关闭下拉菜单
                    print(f"\n  ✅ 完成主导航 '{nav_item['text']}' 的所有大类处理")
                    self.page.keyboard.press("Escape")
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ 处理主导航 {nav_item['text']} 时出错: {e}")
                    continue
            
            print(f"\n✅ 按序处理完成，共处理 {len(navigation_data['main_navigation'])} 个主导航项")
            return navigation_data
            
        except Exception as e:
            print(f"❌ 按序处理失败: {e}")
            return {}
    
    def save_navigation_data(self, data: Dict, filename: str = "liuyunku_navigation_final_v2.json") -> bool:
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
    """主函数 - 最终优化版V2"""
    automator = LiuYunKuNavigationAutomator()
    
    try:
        print("🚀 启动溜云库导航自动化器（最终优化版V2）")
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
        
        # 2. 获取所有主导航项（按指定顺序）
        print("\n🔍 步骤3: 获取主导航项（按序）")
        
        # 3. 按顺序处理每个主导航项
        print("\n🎯 步骤4: 按序处理所有导航")
        navigation_data = automator.process_all_navigations_in_order()
        
        # 4. 保存完整数据到JSON
        print("\n💾 步骤5: 保存数据")
        if navigation_data["main_navigation"]:
            automator.save_navigation_data(navigation_data)
            
            # 打印统计信息
            total_main = len(navigation_data["main_navigation"])
            total_categories = sum(len(nav["categories"]) for nav in navigation_data["main_navigation"])
            total_subcategories = sum(
                sum(len(cat["subcategories"]) for cat in nav["categories"]) 
                for nav in navigation_data["main_navigation"]
            )
            
            print(f"\n📊 最终统计:")
            print(f"  主导航项: {total_main}")
            print(f"  大类: {total_categories}")
            print(f"  细分项: {total_subcategories}")
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