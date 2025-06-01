from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import asyncio


from bs4 import BeautifulSoup

def extract_author_institutions(html):
    """
    从HTML中提取作者单位信息
    
    参数:
        html (str): 包含作者单位信息的HTML片段
        
    返回:
        list: 作者单位列表
    """
    soup = BeautifulSoup(html, 'html.parser')
    institutions = []
    
    # 查找所有class为'author'的h3标签
    for author_section in soup.find_all('h3', class_='author'):
        # 跳过包含作者姓名的部分（通常有id="authorpart"）
        if 'id' in author_section.attrs and 'authorpart' in author_section['id']:
            continue
            
        # 提取单位信息
        for span in author_section.find_all('span'):
            a_tag = span.find('a')
            if a_tag:
                # 获取纯文本并去除首尾空白
                institution = a_tag.get_text(strip=True)
                if institution:  # 确保不是空字符串
                    institutions.append(institution)
                    
    return institutions


async def find_cnki_article_url(title: str, author: str,communication:str) -> dict:
    search_url_advanced = "https://kns.cnki.net/kns8s/AdvSearch"
    search_url = "https://kns.cnki.net/kns8s/search"
    results = {"search": [], "advanced_search": []}

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,  # 设为False便于调试
            timeout=60000,
            args=['--start-maximized']
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = await context.new_page()
        articles = []
        try:
            # ========== 普通检索 ==========
            await page.goto(search_url, timeout=60000)
            # 等待搜索表单加载完成

            await page.wait_for_selector('.sort-default', timeout=5000)
            
            # 确保选择的是篇名选项
            current_span = await page.text_content('.sort-default span')
            if "篇名" not in current_span:
                await page.click('.sort-default')
                await page.wait_for_selector('.sort-list', state='visible', timeout=5000)
                await page.click('.sort-list li[data-val="TI"] a')
                await page.wait_for_timeout(500)  # 短暂等待选项切换
            
            # 填写篇名
            await page.fill('#txt_search', title)
            
            # 点击搜索按钮
            await page.click('.search-btn')
            
            # 确保总库标签存在并可见
            await page.wait_for_selector('a[data-id="all"].all[name="classify"]', state='visible', timeout=10000)
            await page.click('a[data-id="all"][class="all"][name="classify"]')
            
            # 等待结果区域加载
            await page.wait_for_selector('#gridTable', timeout=5000)
            await page.wait_for_timeout(2000)  # 短暂等待
            await page.wait_for_selector('table.result-table-list', timeout=5000)
            
            # 首先点击所有"显示全部作者"的链接
            show_all_authors_buttons = await page.query_selector_all('a.showAllAuthors')
            for button in show_all_authors_buttons:
                try:
                    await button.click()
                    await page.wait_for_timeout(500)  # 短暂等待作者信息加载
                except Exception as e:
                    print(f"点击显示全部作者时出错: {str(e)}")
                    continue
            
            # 等待所有作者信息加载完成
            await page.wait_for_timeout(2000)
            
            # 获取更新后的页面内容
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')
            rows = soup.select('table.result-table-list tr')[1:]  # 第一个是表头
            # print(rows)
            
            for row in rows:
                # 标题和URL
                title_tag = row.select_one('td.name a')
                article_title = title_tag.text.strip() if title_tag else ""
                href = title_tag['href'] if title_tag else ""
                if href and not href.startswith('http'):
                    href = 'https://kns.cnki.net' + href
#                 if title_tag:

#                     try:
#                         await page.goto(href, timeout=60000)
#                         # 等待页面加载
#                         # await page.evaluate('(element) => element.click()', await page.query_selector(f'a[href="{title_tag["href"]}"]'))
#                         await page.wait_for_load_state('networkidle')
#   # 等待页面加载（根据情况调整时间）
                        
#                         # 获取页面内容
#                         content = await page.content()
                        
#                         soup = BeautifulSoup(content, 'html.parser')

                        
#                         author_home_html = (soup.find_all('h3',class_='author'))
#                         author_home_list = extract_author_institutions(str(author_home_html))
#                         author_home = "\n".join(author_home_list) if author_home_list else "未提取到作者单位"
#                         print(author_home)
#                         await page.go_back()
#                         await page.wait_for_timeout(1000)
#                     except Exception as e:
#                         print(f"出错: {e}")

                # 作者处理
                author_div = row.select_one('td.author div.authorinfo')
                if author_div:
                    # 获取所有作者（包括点击后显示的）
                    author_p = author_div.select_one('p')
                    if author_p:
                        # 获取可见作者
                        visible_authors = author_p.get_text(strip=True)
                        # 获取隐藏作者（如果有）
                        hidden_authors = author_div.select_one('span[style="display:none"]')
                        if hidden_authors:
                            authors = visible_authors + hidden_authors.text
                        else:
                            authors = visible_authors
                    else:
                        authors = ""
                else:
                    # 中文文章处理
                    author_tags = row.select('td.author a')
                    authors = ";".join([a.text.strip() for a in author_tags]) if author_tags else ""
                
                # 来源处理
                source_tag = row.select_one('td.source a')
                if source_tag:  # 中文文章
                    source = source_tag.text.strip()
                else:  # 外文文章
                    source_span = row.select_one('td.source span')
                    source = source_span.text.strip() if source_span else ""
                
                # 发表时间
                date_tag = row.select_one('td.date')
                publish_date = date_tag.text.strip() if date_tag else ""
                
                # 数据库类型
                data_tag = row.select_one('td.data span')
                database = data_tag.text.strip() if data_tag else ""
                
                # 被引次数
                quote_tag = row.select_one('td.quote')
                citations = quote_tag.text.strip() if quote_tag else "0"
                
                # 下载次数
                download_tag = row.select_one('td.download a.downloadCnt')
                downloads = download_tag.text.strip() if download_tag else "0"
                
                articles.append({
                    "title": article_title,
                    "url": href,
                    "作者": authors,
                    "来源": source,
                    "发表时间": publish_date,
                    "数据库": database,
                    "被引": citations,
                    "下载": downloads,
                    "联系人":communication
                })
            article_info = {}
            if articles:
                for article in articles:
                    if author in article['作者']:
                        article_info = article
                        break
            if not article_info:
                article_info = {}
                
            else:
                try:
                    # 打开文章详情页
                    await page.goto(article_info["url"], timeout=60000)
                    # 等待页面加载
                    # await page.evaluate('(element) => element.click()', await page.query_selector(f'a[href="{title_tag["href"]}"]'))
                    await page.wait_for_load_state('networkidle')
                    
                    # 获取页面内容
                    content = await page.content()
                    
                    soup = BeautifulSoup(content, 'html.parser')

                    
                    author_home_html = (soup.find_all('h3',class_='author'))
                    author_home_list = extract_author_institutions(str(author_home_html))
                    if author_home_list:
                        author_home = "\n".join(author_home_list)
                    elif not author_home_list:
                        # 尝试从“作者背景”中提取
                        author_background = soup.find_all('h3')
                        extracted_units = []
                        for h3 in author_background:
                            b_tag = h3.find('b')
                            if b_tag and '作者背景' in b_tag.get_text():
                                span = h3.find('span')
                                if span:
                                    links = span.find_all('a')
                                    for link in links:
                                        text = link.get_text(strip=True)
                                        if text:
                                            extracted_units.append(text)
                                break  # 找到一个“作者背景”就够了
                        if extracted_units:
                            author_home = "\n".join(extracted_units)
                        else:
                            author_home = "未提取到作者单位"
                        
                    # print(author_home)
                    article_info["作者单位"] = author_home
                    # await page.go_back()
                    await page.wait_for_timeout(1000)
                except Exception as e:
                    print(f"出错: {e}")
                    article_info["作者单位"] = "未提取到作者单位"
            
        except Exception as e:
            print(f"Error occurred: {str(e)}")
            # 保存截图和HTML用于调试
            await page.screenshot(path='debug.png')
            with open('debug.html', 'w', encoding='utf-8') as f:
                f.write(await page.content())
            article_info = {}
        
        await browser.close()

    return article_info
import asyncio
import time
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def extract_organizations_with_playwright(search_url, username, password):
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            timeout=60000,
            args=['--start-maximized']
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            await page.goto(search_url, timeout=15000)
            
            # Check if login is required (look for either login form or content)
            login_form = await page.query_selector("input#TextBoxUserName")
            if login_form:
                print("Login form detected, attempting login...")
                # Fill in credentials
                await page.fill("input#TextBoxUserName", username)
                await page.fill("input#TextBoxPwd", password)
                
                # Check agreement checkbox
                await page.check("input#agreement")
                
                # Handle slider verification if present
                slider = await page.query_selector("#nc_1_n1z")
                if slider:
                    try:
                        box = await slider.bounding_box()
                        if box:
                            await page.mouse.move(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
                            await page.mouse.down()
                            await page.mouse.move(box["x"] + box["width"] * 2, box["y"] + box["height"] / 2, steps=50)
                            await page.mouse.up()
                    except Exception as e:
                        print(f"Slider handling error: {e}")
                
                # Click login button and wait for navigation
                await page.click("a.tologin")
                await page.wait_for_timeout(3000)  # Wait for potential redirect
            
            # Wait for content to load
            try:
                await page.wait_for_selector("h3.author", timeout=10000)
            except:
                # Fallback to different selector if first one fails
                await page.wait_for_selector(".author-scholar", timeout=10000)
            
            # Get page content
            html = await page.content()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')
            org_names = []
            
            # Extract organizations from different possible structures
            # Structure 1: h3.author with organization links
            for h3 in soup.find_all('h3', class_='author'):
                for a in h3.find_all('a'):
                    text = a.get_text(strip=True)
                    if any(kw in text for kw in ["公司", "大学", "研究院", "研究所", "中心", "医院", "学院", "College", "University", "Institute"]):
                        org_names.append(text)
            
            # Structure 2: author-scholar with organization info
            for div in soup.find_all(class_='author-scholar'):
                text = div.get_text(strip=True)
                if any(kw in text for kw in ["公司", "大学", "研究院", "研究所", "中心", "医院", "学院", "College", "University", "Institute"]):
                    org_names.append(text)
            
            # Structure 3: author background info
            for h3 in soup.find_all('h3', string=lambda t: "作者背景" in str(t)):
                for a in h3.find_next_sibling().find_all('a'):
                    text = a.get_text(strip=True)
                    if any(kw in text for kw in ["公司", "大学", "研究院", "研究所", "中心", "医院", "学院", "College", "University", "Institute"]):
                        org_names.append(text)
            
            # Remove duplicates while preserving order
            seen = set()
            unique_orgs = []
            for org in org_names:
                if org not in seen:
                    seen.add(org)
                    unique_orgs.append(org)
            
            return unique_orgs if unique_orgs else ["未提取到作者单位"]
            
        except Exception as e:
            print(f"Error processing {search_url}: {str(e)}")
            return ["提取过程中发生错误"]
        finally:
            await browser.close()




import base64
def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")





def extract_json(s):
    # 查找第一个左大括号的位置，确保最外层是JSON对象
    start = None
    for i, c in enumerate(s):
        if c == '{':
            start = i
            break
    if start is None:
        return None  # 没有找到可能的JSON对象

    stack = ['{']  # 初始化栈，用于匹配括号
    in_string = False  # 是否在字符串内部
    escape = False  # 是否处理转义字符
    end = None  # 记录结束位置

    # 从start+1开始遍历字符，匹配括号
    for i in range(start + 1, len(s)):
        char = s[i]

        if in_string:
            if escape:
                escape = False  # 转义状态结束
            else:
                if char == '\\':
                    escape = True  # 下一个字符被转义
                elif char == '"':
                    in_string = False  # 字符串结束
        else:
            if char == '"':
                in_string = True  # 进入字符串
                escape = False
            elif char == '{':
                stack.append(char)
            elif char == '}':
                if not stack:
                    break  # 栈空，无法匹配
                stack.pop()
                if not stack:  # 栈空，匹配成功
                    end = i
                    break
        # 继续循环直到找到结束或遍历完字符串

    if end is None:
        return None  # 没有完整的结构

    json_str = s[start:end + 1]

    try:
        import json
        parsed = json.loads(json_str)
        # 确保解析结果是一个字典
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None  # JSON解析失败     
   

def integrate_patent_info(patent_list):
    for patent in patent_list:
        if len(patent) == 5:
            keys = ["申请号","申请日","申请年度","发明创造名称","申请人"]
            for key in keys:
                if key not in patent:
                    return []
            patent["专利名称"] = patent.pop("发明创造名称")
            patent["申请日期"] = patent.pop("申请日")
            patent["授权公告日"] = "-"
            patent["授权年度"] = "-"
            patent["专利号"] = "-"
            patent["发明人"] = "-"
            patent["联系人"] = "-"
            patent["申请类型"] = "发明"
            patent["状态"] = "受理"
            patent["部门"] = "采集业务部"
            patent["专利权人"] = patent.pop("申请人")
        elif len(patent) == 9:
            keys = ["发明名称","发明人","专利号","专利申请日","申请年度","授权公告日","专利权人","授权年度","授权公告号"]
            for key in keys:
                if key not in patent:
                    return []
            patent["专利名称"] = patent.pop("发明名称")
            patent["申请日期"] = patent.pop("专利申请日")
            patent["申请号"] = "-"
            patent["联系人"] = "-"
            del patent["授权公告号"]
            patent["申请类型"] = "发明"    
            patent["状态"] = "授权"
            patent["部门"] = "采集业务部" 
        else:
            return []
        
    return patent_list
import base64
import io
from PIL import Image
import fitz  # PyMuPDF
from PIL import Image
import io
import base64

def pdf_to_base64_images(uploaded_files):
    base64_images = []
    
    for uploaded_file in uploaded_files:
        # Read the PDF file
        pdf_data = uploaded_file.read()
        
        # Open PDF with PyMuPDF
        pdf_document = fitz.open(stream=pdf_data, filetype="pdf")
        
        # 只处理第一页（page_num = 0）
        page = pdf_document.load_page(0)  # 第一页索引是 0
        pix = page.get_pixmap()
        
        # Convert to PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        
        # Convert to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")
        
        base64_images.append(img_base64)
        
        pdf_document.close()  # 关闭 PDF 文件
    
    return base64_images




if __name__ == "__main__":
    # title = "A novel hybrid machine learning approach for δ13C spatial prediction in polish hard-water lakes"
    title = "Research on Photovoltaic Power Prediction Based on BP Neural Network Algorithm"

    author = "Zhang Bozhi"
    result = asyncio.run(find_cnki_article_url(title, author,''))
    print(result)
