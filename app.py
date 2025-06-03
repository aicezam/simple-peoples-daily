import flask
from flask import request, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime, date as dt_date
from urllib.parse import urljoin
import re

app = flask.Flask(__name__)
app.config["JSON_AS_ASCII"] = False

BASE_URL_TODAY = "http://www.people.com.cn/GB/59476/index.html"
BASE_URL_ARCHIVE_PREFIX = "http://www.people.com.cn/GB/59476/review/"
PEOPLE_CN_BASE = "http://www.people.com.cn"

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def extract_datetime_from_text(text_node_content, year_str=""):
    """
    Extracts 'YYYY年MM月DD日HH:MM' or 'MM月DD日HH:MM' from text.
    If year_str is provided (e.g., "2025年"), it's prepended to MM月DD日HH:MM.
    """
    if not text_node_content:
        return ""
    
    # Try full YYYY年MM月DD日HH:MM format first
    match_full = re.search(r'\[(\d{4}年\d{1,2}月\d{1,2}日\d{2}:\d{2})\]', text_node_content)
    if match_full:
        return match_full.group(1)

    # Try MM月DD日HH:MM format
    match_mdhm = re.search(r'\[(\d{1,2}月\d{1,2}日\d{2}:\d{2})\]', text_node_content)
    if match_mdhm and year_str:
        return year_str + match_mdhm.group(1)
    
    # Try YYYY年MM月DD日 format (no time)
    match_date_only_full = re.search(r'\[(\d{4}年\d{1,2}月\d{1,2}日)\]', text_node_content)
    if match_date_only_full:
        return match_date_only_full.group(1)

    # Try MM月DD日 format (no time, needs year)
    match_md_only = re.search(r'\[(\d{1,2}月\d{1,2}日)\]', text_node_content)
    if match_md_only and year_str:
        return year_str + match_md_only.group(1)
        
    return ""


def parse_legacy_page(soup, page_general_date_str):
    news_items = []
    year_for_partial_dates = ""
    if page_general_date_str:
        year_match = re.match(r'(\d{4}年)', page_general_date_str)
        if year_match:
            year_for_partial_dates = year_match.group(1)

    # 1. 主要新闻块 (td.indexfont13) - 通常是头条新闻
    main_news_td = soup.find('td', class_='indexfont13')
    if main_news_td:
        # Case 1: <div><a ...>Title</a> [datetime]</div>
        for div_tag in main_news_td.find_all('div', recursive=False):
            link_tag = div_tag.find('a', href=True)
            if link_tag:
                title = link_tag.get_text(strip=True)
                href = link_tag['href']
                absolute_link = urljoin(PEOPLE_CN_BASE, href)
                
                datetime_str_full = extract_datetime_from_text(div_tag.get_text(strip=False), year_for_partial_dates)
                
                news_items.append({
                    "title": "头条新闻："+title,
                    "link": absolute_link,
                    "datetime_str": datetime_str_full if datetime_str_full else page_general_date_str
                })

        # Case 2: <a href="..."><img ...></a> <center>[datetime]</center> (图片新闻)
        direct_a_tags = main_news_td.find_all('a', recursive=False, href=True)
        for link_tag in direct_a_tags:
            if link_tag.find('img'): 
                title = "头条新闻（图片）" 
                href = link_tag['href']
                absolute_link = urljoin(PEOPLE_CN_BASE, href)
                
                datetime_str_full = ""
                next_elem = link_tag.next_sibling
                time_text_container = ""
                while next_elem:
                    if next_elem.name == 'center':
                        time_text_container = next_elem.get_text(strip=True)
                        break
                    elif isinstance(next_elem, str) and next_elem.strip().startswith('['):
                         time_text_container = next_elem.strip()
                         break
                    next_elem = next_elem.next_sibling
                
                if time_text_container:
                    datetime_str_full = extract_datetime_from_text(time_text_container, year_for_partial_dates)

                news_items.append({
                    "title": title,
                    "link": absolute_link,
                    "datetime_str": datetime_str_full if datetime_str_full else page_general_date_str
                })
    
    # 2. 次要新闻列表 (td.p6 下的 li)
    secondary_news_container = soup.find('td', class_='p6')
    if secondary_news_container:
        list_items_tags = secondary_news_container.find_all('li')
        for item_li in list_items_tags:
            # Get the full text of the <li> as title
            title = item_li.get_text(strip=True)
            
            # Find the first link in <li>
            link_tag_in_li = item_li.find('a', href=True)
            href = ""
            if link_tag_in_li and link_tag_in_li.has_attr('href'):
                href = link_tag_in_li['href']
            
            absolute_link = urljoin(PEOPLE_CN_BASE, href) if href else PEOPLE_CN_BASE

            datetime_str_full = ""
            next_node = item_li.next_sibling
            while next_node and (isinstance(next_node, str) and not next_node.strip()):
                next_node = next_node.next_sibling
            
            if next_node and isinstance(next_node, str) and next_node.strip().startswith('['):
                datetime_str_full = extract_datetime_from_text(next_node.strip(), year_for_partial_dates) # year_for_partial_dates might not be needed if format is YYYY年...

            news_items.append({
                "title": title,
                "link": absolute_link,
                "datetime_str": datetime_str_full if datetime_str_full else page_general_date_str
            })

    # Deduplication based on title and link to ensure uniqueness
    seen_items = set()
    unique_news = []
    for item in news_items:
        identifier = (item['title'], item['link'])
        if identifier not in seen_items:
            unique_news.append(item)
            seen_items.add(identifier)
    return unique_news

def parse_modern_page(soup, page_general_date_str):
    # (Keeping the modern page parser from previous version, 
    #  you might need to adapt its datetime extraction if it becomes relevant)
    news_items = []
    # Common containers for modern layouts
    containers = [
        soup.find('div', class_='ej_list_box'),
        soup.find('div', class_='p_list_co'), 
        soup.find('ul', class_='list_ej14'),
        soup.find('div', class_='news_list'), 
        soup.find('div', class_='focus_list'),
    ]
    
    processed_links = set()

    for container in containers:
        if container:
            list_item_tags = container.find_all('li')
            if not list_item_tags: 
                links_in_container = container.find_all('a', href=True)
                for link_tag in links_in_container:
                    title = link_tag.get_text(strip=True)
                    href = link_tag['href']
                    if title and href and not href.startswith('javascript:'):
                        absolute_link = urljoin(PEOPLE_CN_BASE, href)
                        if absolute_link not in processed_links:
                            news_items.append({
                                "title": title,
                                "link": absolute_link,
                                "datetime_str": page_general_date_str # Placeholder, modern pages need specific time extraction
                            })
                            processed_links.add(absolute_link)
            else: 
                for item_tag in list_item_tags:
                    link_tag = item_tag.find('a', href=True)
                    # Attempt to find time associated with this item (example, may need adjustment)
                    time_tag = item_tag.find(['span', 'p'], class_=re.compile(r'time|date|meta'))
                    item_datetime_str = page_general_date_str
                    if time_tag:
                        extracted_dt = extract_datetime_from_text(time_tag.get_text(strip=True), page_general_date_str.split('年')[0]+'年' if page_general_date_str else "")
                        if extracted_dt:
                            item_datetime_str = extracted_dt
                    
                    if link_tag:
                        title = link_tag.get_text(strip=True)
                        href = link_tag['href']
                        if title and href and not href.startswith('javascript:'):
                            absolute_link = urljoin(PEOPLE_CN_BASE, href)
                            if absolute_link not in processed_links:
                                news_items.append({
                                    "title": title,
                                    "link": absolute_link,
                                    "datetime_str": item_datetime_str
                                })
                                processed_links.add(absolute_link)
    return news_items


def get_peoples_daily_news(target_date_str=None):
    request_url = ""
    page_general_date_str = "" # YYYY年MM月DD日 format

    try:
        if target_date_str:
            try:
                query_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
                url_date_str = query_date.strftime("%Y%m%d")
                request_url = f"{BASE_URL_ARCHIVE_PREFIX}{url_date_str}.html"
                page_general_date_str = query_date.strftime("%Y年%m月%d日")
            except ValueError:
                return {"error": "日期格式错误，请使用 YYYY-MM-DD 格式。"}
        else:
            request_url = BASE_URL_TODAY
        
        response = requests.get(request_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser', from_encoding='gbk')

        parsed_page_date_from_html = ""
        # Try to get date from page (this is the overall page date, not individual article times)
        date_source_info = soup.find(lambda tag: tag.name == 'td' and 
                                   tag.get('class') == ['wt'] and 
                                   '年' in tag.get_text() and '月' in tag.get_text() and '日' in tag.get_text() and
                                   (tag.get('align') == 'right' or not tag.has_attr('align')))
        if not date_source_info:
            date_source_info = soup.select_one('div.path span, div.title_nav span.date, div.box_left_title01 span, p.ej_left_time, .banB > .fl, .ban1 > .fl')
        
        if date_source_info:
            date_text = date_source_info.get_text(strip=True)
            match = re.search(r'(\d{4}年\d{1,2}月\d{1,2}日)', date_text)
            if match:
                parsed_page_date_from_html = match.group(1)
        
        if target_date_str: 
            if parsed_page_date_from_html and parsed_page_date_from_html != page_general_date_str:
                print(f"Warning: Queried date {page_general_date_str} but page shows {parsed_page_date_from_html}. Using date from page for general context.")
                page_general_date_str = parsed_page_date_from_html
            elif not parsed_page_date_from_html:
                 print(f"Warning: Could not parse general date from historical page {request_url}. Using query date {page_general_date_str}.")
        else: 
            if parsed_page_date_from_html:
                page_general_date_str = parsed_page_date_from_html
            else:
                print("Warning: Could not parse general date from today's page. Using system date.")
                page_general_date_str = datetime.now().strftime("%Y年%m月%d日")
        
        if not page_general_date_str:
             return {"error": "无法确定新闻的总体页面日期。", "data": []}

        # Determine which parser to use
        news_data_raw = []
        modern_items = parse_modern_page(soup, page_general_date_str)
        
        # Heuristic: if modern parser finds very few items, or if specific legacy markers are present
        is_legacy_page = soup.find('td', class_='indexfont13') or soup.find('td', class_='p6')
        
        if is_legacy_page and (not modern_items or len(modern_items) < 5): # Threshold can be adjusted
            print("Page seems legacy or modern parser found few items. Using legacy parser.")
            legacy_items = parse_legacy_page(soup, page_general_date_str)
            news_data_raw = legacy_items
        else:
            news_data_raw = modern_items
            if not news_data_raw and is_legacy_page : # Fallback if modern found nothing but it looks legacy
                 print("Modern parser found nothing, but page has legacy markers. Retrying with legacy parser.")
                 legacy_items = parse_legacy_page(soup, page_general_date_str)
                 news_data_raw = legacy_items


        if not news_data_raw:
            message = f"未能从 {page_general_date_str} 的页面提取新闻数据。"
            return {"message": message, "data": []}
        
        # Format the final list: rename 'datetime_str' to 'date'
        final_news_list = []
        for item in news_data_raw:
            final_news_list.append({
                "date": item.get("datetime_str", page_general_date_str), # Fallback to general page date
                "title": item["title"],
                "link": item["link"]
            })

        return {"message": "获取成功", "data": final_news_list}

    except requests.exceptions.HTTPError as e:
        error_msg_date_part = page_general_date_str if page_general_date_str else (target_date_str if target_date_str else "今日")
        if e.response.status_code == 404:
            return {"error": f"未找到 {error_msg_date_part} 的新闻页面 (404)。可能该日期没有归档或URL错误。"}
        return {"error": f"请求页面失败 ({e.response.status_code}): {e}"}
    except requests.exceptions.RequestException as e:
        return {"error": f"网络请求错误: {e}"}
    except Exception as e:
        import traceback
        print(f"An unexpected error occurred: {type(e).__name__} - {e}")
        print(traceback.format_exc())
        return {"error": f"处理时发生未知错误: {e}"}

@app.route('/api/peoples_daily_news', methods=['GET'])
def api_get_news():
    date_query = request.args.get('date') 
    if date_query:
        try:
            datetime.strptime(date_query, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "日期格式无效，请使用 YYYY-MM-DD 格式。"}), 400
        result = get_peoples_daily_news(target_date_str=date_query)
    else:
        result = get_peoples_daily_news()

    if "error" in result:
        status_code = 500 
        # ... (status code logic from previous version)
        return jsonify(result), status_code
    return jsonify(result)

if __name__ == '__main__':
    port = 5013 
    print("API 服务已启动，请访问:")
    print(f"今日要闻: http://127.0.0.1:{port}/api/peoples_daily_news")
    print(f"指定日期 (例如2023-10-01): http://127.0.0.1:{port}/api/peoples_daily_news?date=2023-10-01")
    app.run(debug=True, host='0.0.0.0', port=port)
