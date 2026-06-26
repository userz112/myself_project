import undetected_chromedriver as uc
from selenium_stealth import stealth
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

driver = None

time.sleep(random.uniform(2, 3)) 
try:
    options = uc.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--start-maximized')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # 添加代理IP（如果有免费代理）
    # options.add_argument('--proxy-server=http://127.0.0.1:7890')
    
    driver = uc.Chrome(options=options, use_subprocess=True, version_main=132)
    
    stealth(driver,
            languages=["zh-CN", "zh"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="ANGLE (Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0)",
            fix_hairline=True,
            )
    
    print("正在访问网站...")
    driver.get('https://beijing.anjuke.com/')

    print("\n=== HTML内容分析 ===")
    page_source = driver.page_source
    
    # 保存HTML到文件，方便查看
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(page_source)
    print("HTML已保存到 page_source.html 文件")
    
    # 查找所有包含数字的元素（可能是价格）
    print("\n=== 查找可能的房源元素 ===")
    all_elements = driver.find_elements(By.CSS_SELECTOR, "*")
    
    # 查找包含价格的元素（包含数字和货币符号）
    price_candidates = []
    for elem in all_elements:
        try:
            text = elem.text.strip()
            if text and any(c.isdigit() for c in text):
                if '万' in text or '元' in text or '㎡' in text or '平' in text:
                    price_candidates.append((elem.tag_name, elem.get_attribute('class'), text[:50]))
        except:
            continue
    
    print(f"\n找到 {len(price_candidates)} 个可能包含价格的元素:")
    for i, (tag, class_name, text) in enumerate(price_candidates[:10]):
        print(f"{i+1}. <{tag} class='{class_name}'> {text}")
    
    # 查找所有class名称
    print("\n=== 查找所有class名称 ===")
    all_classes = set()
    for elem in all_elements:
        try:
            class_name = elem.get_attribute('class')
            if class_name:
                all_classes.add(class_name)
        except:
            continue
    
    # 过滤出可能相关的class
    relevant_classes = [c for c in all_classes if any(keyword in c.lower() for keyword in ['house', 'list', 'item', 'price', 'info', 'title'])]
    print(f"\n找到 {len(relevant_classes)} 个可能相关的class:")
    for i, class_name in enumerate(relevant_classes[:20]):
        elements = driver.find_elements(By.CLASS_NAME, class_name.split()[0] if ' ' in class_name else class_name)
        print(f"{i+1}. '.{class_name}' - {len(elements)} 个元素")
    
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )
    
    print()

    time.sleep(random.uniform(2, 4))
    
    print(f"页面标题: {driver.title}")
    
    house_items = driver.find_elements(By.CSS_SELECTOR, ".list-item")
    print(f"找到 {len(house_items)} 个房源")
    
    if not house_items:
        print("没有找到房源元素，尝试其他选择器...")
        alternative_selectors = [
            ".house-item",
            "[class*='list']",
            "[class*='item']",
            ".house-mod",
        ]
        
        for selector in alternative_selectors:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            if elements:
                print(f"选择器 '{selector}' 找到 {len(elements)} 个元素")
                house_items = elements
                break
    
    if not house_items:
        print("仍然没有找到房源，请检查页面结构")
        print("页面URL:", driver.current_url)
        print("页面标题:", driver.title)
    
    for i, item in enumerate(house_items[:5]):
        try:
            print(f"\n正在处理第 {i+1} 个房源...")
            
            try:
                title_element = item.find_element(By.CLASS_NAME, "item-info-meta")
                title = title_element.text
                print(f"标题: {title}")
            except Exception as e:
                print(f"获取标题失败: {e}")
                continue
            
            try:
                price_element = item.find_element(By.CLASS_NAME, "item-info-price-one-num")
                price = price_element.text
                print(f"价格: {price}m²")
            except Exception as e:
                print(f"获取价格失败: {e}")
                continue
            
            print(f"{i+1}. {title} - {price}m²")
            
        except Exception as e:
            print(f"处理房源 {i+1} 时发生错误: {type(e).__name__}: {e}")
            continue
    
except Exception as e:
    print(f"发生错误: {e}")

finally:
    if driver:
        try:
            driver.quit()
        except:
            pass