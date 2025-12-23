# 溜云库自动化配置文件
# 应用配置
APP_CONFIG = {
    "exe_path": r"D:\LiuYunKu4\LiuYunKu.exe",  # 溜云库可执行文件路径
    "window_title_keyword": "溜云库",  # 窗口标题关键词
    "online_material_keyword": "在线",  # 在线素材按钮关键词
    "model_library_keyword": "模型库",  # 模型库页面关键词
    "startup_timeout": 30,  # 启动超时时间（秒）
    "operation_delay": 2,  # 操作间隔时间（秒）
}
# 浏览器连接配置
BROWSER_CONFIG = {
    "cdp_ports": ['9222', '9333', '9444', '9555'],  # CDP端口列表
    "connection_retries": 3,  # 连接重试次数
    "connection_timeout": 10,  # 连接超时时间（秒）
    "page_timeout": 15000,  # 页面操作超时（毫秒）
    "network_idle_timeout": 15000,  # 网络空闲超时（毫秒）
}
# 导航选择器配置
SELECTOR_CONFIG = {
    "main_nav_container": "ul[data-rfd-droppable-id='nav-list']",
    "main_nav_item": "li",
    "main_nav_text": "p",
    "dropdown_menu": "div.mantine-HoverCard-dropdown[role='dialog']",
    "category_container": "div[class*='maxClassList_max_children_class__']",
    "category_title": "span[class*='maxClassList_max_title__']",
    "subcategory_item": "li",
    "subcategory_text": "span",
    "close_button": "span[class*='maxClassList_close__']",
    "active_class": "maxClassList_active__9kpsY",
}
# 测试用例配置
TEST_CASES = [
    {"main_nav": "3D模型", "subcategory": "沙发"},
    {"main_nav": "3D模型", "subcategory": "椅凳"},
    {"main_nav": "3D模型", "subcategory": "柜类"},
    {"main_nav": "3D模型", "subcategory": "桌台"},
    {"main_nav": "材质", "subcategory": "全部"},
    {"main_nav": "SU模型", "subcategory": "全部"},
    {"main_nav": "贴图", "subcategory": "全部"},
    {"main_nav": "CAD", "subcategory": "全部"},
    {"main_nav": "灯光", "subcategory": "全部"},
    {"main_nav": "光域网", "subcategory": "全部"},
]
# 输出配置
OUTPUT_CONFIG = {
    "navigation_data_file": "liuyunku_navigation.json",
    "screenshot_dir": "screenshots",
    "log_file": "liuyunku_automation.log",
    "save_screenshots": True,
    "save_json": True,
}
# 日志配置
LOG_CONFIG = {
    "level": "INFO",  # DEBUG, INFO, WARNING, ERROR
    "console_output": True,
    "file_output": True,
    "log_format": "%(asctime)s - %(levelname)s - %(message)s",
}