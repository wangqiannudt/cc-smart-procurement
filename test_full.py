#!/usr/bin/env python3
"""
智慧采购系统全面测试脚本
测试内容：
1. 三种主题的视觉效果（深邃星空、Nord、Apple）
2. 所有页面的功能
3. 响应式布局
"""
import os
from playwright.sync_api import sync_playwright

# 创建截图目录
SCREENSHOT_DIR = '/tmp/procurement_test'
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def save_screenshot(page, name):
    """保存截图"""
    path = f'{SCREENSHOT_DIR}/{name}.png'
    page.screenshot(path=path, full_page=True)
    print(f"  截图保存: {path}")
    return path

def test_themes(page):
    """测试三种主题的视觉效果"""
    print("\n" + "="*60)
    print("🎨 主题视觉测试")
    print("="*60)

    themes = [
        ('default', '深邃星空'),
        ('nord', '北欧冷调'),
        ('apple', 'Apple')
    ]

    for theme_id, theme_name in themes:
        print(f"\n📱 测试主题: {theme_name} ({theme_id})")

        # 访问登录页（公开页面）
        page.goto('http://localhost:5173/login')
        page.wait_for_load_state('networkidle')

        # 设置主题
        page.evaluate(f'''
            localStorage.setItem('procurement-theme', '{theme_id}');
        ''')

        # 刷新应用主题
        page.reload()
        page.wait_for_load_state('networkidle')

        # 检查主题是否正确应用
        data_theme = page.evaluate('document.documentElement.getAttribute("data-theme")')
        print(f"  data-theme 属性: {data_theme}")

        # 获取主背景色
        bg_color = page.evaluate('getComputedStyle(document.documentElement).getPropertyValue("--bg-primary")')
        print(f"  主背景色: {bg_color}")

        # 保存登录页截图
        save_screenshot(page, f'theme_{theme_id}_login')

def test_login_page(page):
    """测试登录页面"""
    print("\n" + "="*60)
    print("🔐 登录页面测试")
    print("="*60)

    page.goto('http://localhost:5173/login')
    page.wait_for_load_state('networkidle')

    # 检查页面元素
    title = page.locator('h2, .login-title, .form-title').first
    if title.is_visible():
        print(f"  ✓ 页面标题可见: {title.text_content()}")

    # 检查登录表单
    username_input = page.locator('input[type="text"], input[placeholder*="用户"]').first
    password_input = page.locator('input[type="password"]').first
    login_btn = page.locator('button:has-text("登录"), button:has-text("登")').first

    if username_input.is_visible():
        print("  ✓ 用户名输入框可见")
    if password_input.is_visible():
        print("  ✓ 密码输入框可见")
    if login_btn.is_visible():
        print("  ✓ 登录按钮可见")

    # 检查注册链接
    register_link = page.locator('a:has-text("注册"), a[href="/register"]').first
    if register_link.is_visible():
        print("  ✓ 注册链接可见")

    save_screenshot(page, 'page_login')

def test_register_page(page):
    """测试注册页面"""
    print("\n" + "="*60)
    print("📝 注册页面测试")
    print("="*60)

    page.goto('http://localhost:5173/register')
    page.wait_for_load_state('networkidle')

    # 检查注册表单
    username = page.locator('input[placeholder*="用户"], input[type="text"]').first
    email = page.locator('input[type="email"], input[placeholder*="邮箱"]').first
    password = page.locator('input[type="password"]').first
    register_btn = page.locator('button:has-text("注册"), button:has-text("注")').first

    if username.is_visible():
        print("  ✓ 用户名输入框可见")
    if email.is_visible():
        print("  ✓ 邮箱输入框可见")
    if password.is_visible():
        print("  ✓ 密码输入框可见")
    if register_btn.is_visible():
        print("  ✓ 注册按钮可见")

    save_screenshot(page, 'page_register')

def test_home_page(page):
    """测试首页（需要登录）"""
    print("\n" + "="*60)
    print("🏠 首页（系统概览）测试")
    print("="*60)

    # 设置测试用户（模拟登录状态）
    page.goto('http://localhost:5173/login')
    page.wait_for_load_state('networkidle')

    # 设置模拟登录状态
    page.evaluate('''
        localStorage.setItem('smart_procurement_token', 'test_token');
        localStorage.setItem('smart_procurement_user', JSON.stringify({
            id: 1,
            username: 'test_user',
            role: 'handler'
        }));
    ''')

    # 访问首页
    page.goto('http://localhost:5173/')
    page.wait_for_load_state('networkidle')

    # 检查页面元素
    header = page.locator('.header h1, h1:has-text("概览"), h1:has-text("系统")').first
    if header.is_visible():
        print(f"  ✓ 页面标题: {header.text_content()}")

    # 检查统计卡片
    stat_cards = page.locator('.stat-card').all()
    print(f"  ✓ 统计卡片数量: {len(stat_cards)}")

    # 检查智能体状态
    status_card = page.locator('.status-card, .card:has-text("智能体")').first
    if status_card.is_visible():
        print("  ✓ 智能体状态卡片可见")

    # 检查快速操作
    actions_card = page.locator('.actions-card, .card:has-text("快速操作")').first
    if actions_card.is_visible():
        print("  ✓ 快速操作卡片可见")

    # 检查侧边栏
    sidebar = page.locator('.sidebar, .el-aside').first
    if sidebar.is_visible():
        print("  ✓ 侧边栏可见")

    # 检查主题切换器
    theme_switcher = page.locator('.theme-switcher, .theme-current').first
    if theme_switcher.is_visible():
        print("  ✓ 主题切换器可见")

    save_screenshot(page, 'page_home')

def test_chat_page(page):
    """测试 AI 对话页面"""
    print("\n" + "="*60)
    print("💬 AI 对话页面测试")
    print("="*60)

    page.goto('http://localhost:5173/chat')
    page.wait_for_load_state('networkidle')

    # 检查聊天输入框
    chat_input = page.locator('textarea, input[placeholder*="输入"], input[placeholder*="消息"]').first
    if chat_input.is_visible():
        print("  ✓ 聊天输入框可见")

    # 检查发送按钮
    send_btn = page.locator('button:has-text("发送"), button .el-icon').first
    if send_btn.is_visible():
        print("  ✓ 发送按钮可见")

    # 检查欢迎消息或历史记录
    welcome = page.locator('.welcome, .chat-welcome, .message').first
    if welcome.is_visible():
        print("  ✓ 欢迎区域/消息可见")

    save_screenshot(page, 'page_chat')

def test_requirements_page(page):
    """测试需求审查页面"""
    print("\n" + "="*60)
    print("📋 需求审查页面测试")
    print("="*60)

    page.goto('http://localhost:5173/requirements')
    page.wait_for_load_state('networkidle')

    # 检查上传区域
    upload = page.locator('.el-upload, .upload-area, [class*="upload"]').first
    if upload.is_visible():
        print("  ✓ 文件上传区域可见")

    # 检查品类选择
    category_select = page.locator('.el-select, select, [class*="category"]').first
    if category_select.is_visible():
        print("  ✓ 品类选择器可见")

    # 检查审查按钮
    review_btn = page.locator('button:has-text("审查"), button:has-text("分析")').first
    if review_btn.is_visible():
        print("  ✓ 审查按钮可见")

    save_screenshot(page, 'page_requirements')

def test_price_page(page):
    """测试价格参考页面"""
    print("\n" + "="*60)
    print("📊 价格参考页面测试")
    print("="*60)

    page.goto('http://localhost:5173/price')
    page.wait_for_load_state('networkidle')

    # 检查搜索框
    search = page.locator('input[placeholder*="搜索"], input[placeholder*="查询"], .el-input').first
    if search.is_visible():
        print("  ✓ 搜索输入框可见")

    # 检查品类选择或筛选
    filter_area = page.locator('.filter, [class*="filter"], .el-select').first
    if filter_area.is_visible():
        print("  ✓ 筛选区域可见")

    # 检查图表区域
    chart = page.locator('.chart, [class*="chart"], .echarts').first
    if chart.is_visible():
        print("  ✓ 图表区域可见")

    save_screenshot(page, 'page_price')

def test_contract_page(page):
    """测试合同分析页面"""
    print("\n" + "="*60)
    print("📄 合同分析页面测试")
    print("="*60)

    page.goto('http://localhost:5173/contract')
    page.wait_for_load_state('networkidle')

    # 检查上传区域
    upload = page.locator('.el-upload, .upload-area, [class*="upload"]').first
    if upload.is_visible():
        print("  ✓ 文件上传区域可见")

    # 检查分析按钮
    analyze_btn = page.locator('button:has-text("分析"), button:has-text("上传")').first
    if analyze_btn.is_visible():
        print("  ✓ 分析按钮可见")

    save_screenshot(page, 'page_contract')

def test_responsive(page):
    """测试响应式布局"""
    print("\n" + "="*60)
    print("📐 响应式布局测试")
    print("="*60)

    # 设置主题为默认
    page.goto('http://localhost:5173/login')
    page.evaluate('localStorage.setItem("procurement-theme", "default");')
    page.reload()
    page.wait_for_load_state('networkidle')

    viewports = [
        ('desktop', 1920, 1080),
        ('tablet', 768, 1024),
        ('mobile', 375, 812)
    ]

    for name, width, height in viewports:
        print(f"\n  测试 {name} 视口 ({width}x{height})")
        page.set_viewport_size({'width': width, 'height': height})
        page.wait_for_timeout(500)

        # 检查关键元素是否可见
        if width < 768:
            # 移动端应该有汉堡菜单
            hamburger = page.locator('.hamburger-btn, .mobile-header button').first
            if hamburger.is_visible():
                print(f"    ✓ 移动端汉堡菜单可见")
        else:
            # 桌面端应该有侧边栏
            sidebar = page.locator('.sidebar, .el-aside').first
            if sidebar.is_visible():
                print(f"    ✓ 桌面端侧边栏可见")

        save_screenshot(page, f'responsive_{name}')

def test_theme_colors(page):
    """测试主题颜色一致性"""
    print("\n" + "="*60)
    print("🎨 主题颜色一致性测试")
    print("="*60)

    themes = ['default', 'nord', 'apple']

    for theme in themes:
        print(f"\n  测试主题: {theme}")
        page.goto('http://localhost:5173/login')
        page.evaluate(f'localStorage.setItem("procurement-theme", "{theme}");')
        page.reload()
        page.wait_for_load_state('networkidle')

        # 获取 CSS 变量值
        colors = page.evaluate('''
            () => {
                const styles = getComputedStyle(document.documentElement);
                return {
                    bgPrimary: styles.getPropertyValue('--bg-primary').trim(),
                    bgCard: styles.getPropertyValue('--bg-card').trim(),
                    textPrimary: styles.getPropertyValue('--text-primary').trim(),
                    colorPrimary: styles.getPropertyValue('--color-primary').trim(),
                    colorSuccess: styles.getPropertyValue('--color-success').trim(),
                    colorWarning: styles.getPropertyValue('--color-warning').trim(),
                    colorDanger: styles.getPropertyValue('--color-danger').trim()
                };
            }
        ''')

        print(f"    主背景: {colors['bgPrimary']}")
        print(f"    卡片背景: {colors['bgCard']}")
        print(f"    主色调: {colors['colorPrimary']}")
        print(f"    成功色: {colors['colorSuccess']}")
        print(f"    警告色: {colors['colorWarning']}")
        print(f"    危险色: {colors['colorDanger']}")

        # 检查是否有白色背景（深色主题下不应该有）
        if theme == 'default':
            if '#fff' in colors['bgCard'].lower() or '#ffffff' in colors['bgCard'].lower():
                print("    ⚠️ 警告: 深色主题下卡片背景为白色！")
            else:
                print("    ✓ 深色主题卡片背景正常")

def main():
    print("="*60)
    print("🚀 智慧采购系统全面测试")
    print("="*60)
    print(f"截图保存目录: {SCREENSHOT_DIR}")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            executable_path='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        )
        context = browser.new_context(
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        try:
            # 1. 主题视觉测试
            test_themes(page)

            # 2. 页面功能测试
            test_login_page(page)
            test_register_page(page)
            test_home_page(page)
            test_chat_page(page)
            test_requirements_page(page)
            test_price_page(page)
            test_contract_page(page)

            # 3. 响应式测试
            test_responsive(page)

            # 4. 颜色一致性测试
            test_theme_colors(page)

            print("\n" + "="*60)
            print("✅ 测试完成！")
            print("="*60)
            print(f"所有截图保存在: {SCREENSHOT_DIR}")
            print("\n请检查截图文件确认视觉效果。")

        except Exception as e:
            print(f"\n❌ 测试出错: {e}")
            import traceback
            traceback.print_exc()
        finally:
            browser.close()

if __name__ == '__main__':
    main()
