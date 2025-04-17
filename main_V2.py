# Author: Yewei
# Purpose: Download budget documents and rename thee accordingly

import csv
import os
import requests
from lxml import etree
from DrissionPage import ChromiumPage

base_url = "https://www.shanghai.gov.cn"

one_url = [
    "https://www.shanghai.gov.cn/bmys-25-001/index.html,党委部门",
    "https://www.shanghai.gov.cn/bmys-25-002/index.html,政府部门",
    "https://www.shanghai.gov.cn/bmys-25-003/index.html,人大政协",
    "https://www.shanghai.gov.cn/bmys-25-004/index.html,民主党派",
    "https://www.shanghai.gov.cn/bmys-25-005/index.html,司法机关",
    "https://www.shanghai.gov.cn/bmys-25-006/index.html,人民团体",
    "https://www.shanghai.gov.cn/bmys-25-007/index.html,其他"
]

def crawl_two_link():
    page = ChromiumPage()
    with open("files/two.csv", newline="", mode='a+', encoding='utf-8') as f:
        writer = csv.writer(f)
        for i in one_url:
            page.get(i.split(",")[0])
            page.wait.load_start()
            tree = etree.HTML(page.html)
            hrefs = tree.xpath("//div[@class='rt-yus dangw']/ul/li/a")
            for item in hrefs:
                href = item.xpath("./@href")[0]
                title = item.xpath("./@title")[0]
                writer.writerow([i.split(",")[1], title, href])
                print(i.split(",")[1], title, href)
            f.flush()
            page.wait(5)

def crawl_pdf_link():
    page = ChromiumPage()
    with open("files/two.csv", mode='r', encoding='utf-8') as fr:
        links = fr.readlines()
        for link in links:
            title1 = link.split(",")[0]
            title2 = link.split(",")[1]
            url = base_url + link.split(",")[2].strip()
            page.get(url)
            page.wait.load_start()
            tree = etree.HTML(page.html)
            hrefs = tree.xpath("//div[@class='rt-yus trout-region-list']/ul/li/a")
            with open("files/pdf.csv", newline="", mode='a+', encoding='utf-8') as fw:
                writer = csv.writer(fw)
                for item in hrefs:
                    file_name = item.xpath("./@title")[0]
                    href = item.xpath("./@href")[0]
                    writer.writerow([title1, title2, file_name, href])
                    print(title1, title2, file_name, href)
                fw.flush()
                page.wait(5)

def crawl_pdf():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': base_url
    }
    session = requests.Session()
    session.headers.update(headers)
    
    with open("files/pdf.csv", mode='r', encoding='utf-8') as fr:
        links = fr.readlines()
        for item in links:
            # 使用csv模块正确解析带逗号的内容
            parts = item.strip().split(',')
            if len(parts) < 4:
                print(f"Invalid line: {item.strip()}")
                continue
            title1, title2, file_name, link = parts[0], parts[1], parts[2], parts[3]
            
            # 创建安全路径（处理特殊字符）
            safe_title1 = "".join([c if c.isalnum() or c in " _-" else "_" for c in title1])
            safe_title2 = "".join([c if c.isalnum() or c in " _-" else "_" for c in title2])
            file_path = os.path.join(os.getcwd(), "files", safe_title1, safe_title2)
            os.makedirs(file_path, exist_ok=True)
            
            # 补全文件名的扩展名
            if not file_name.lower().endswith('.pdf'):
                file_name += '.pdf'
            
            # 完整的文件路径
            full_file_path = os.path.join(file_path, file_name)
            
            # 完整的下载URL
            full_url = base_url + link.strip()
            
            print(f"正在下载：{full_url} 到 {full_file_path}")
            
            try:
                response = session.get(full_url, stream=True)
                response.raise_for_status()  # 检查请求是否成功
                with open(full_file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"成功下载：{file_name}")
            except requests.exceptions.HTTPError as e:
                print(f"HTTP错误: {full_url} - {str(e)}")
            except requests.exceptions.RequestException as e:
                print(f"请求错误: {full_url} - {str(e)}")
            except Exception as e:
                print(f"其他错误: {full_url} - {str(e)}")
            
            # 适当增加等待时间
            import time
            time.sleep(3)

"""
if __name__ == '__main__':
    os.makedirs('files/', exist_ok=True)
    # 1、下载链接
    #crawl_two_link()
    # 2、下载pdf链接
    crawl_pdf_link()
    # 3、下载PDF
    crawl_pdf()
"""

if __name__ == '__main__':
    os.makedirs('files/', exist_ok=True)
    
    print("请选择要执行的操作：")
    print("1. 遍历所有步骤")
    print("2. 获取PDF下载地址并下载")
    print("3. 单独下载PDF")
    
    choice = input("请输入选项 (1/2/3): ").strip()
    
    if choice == '1':
        # 1、下载链接
        crawl_two_link()
        # 2、下载pdf链接
        crawl_pdf_link()
        # 3、下载PDF
        crawl_pdf()
    elif choice == '2':
        # 2、下载pdf链接
        crawl_pdf_link()
        # 3、下载PDF
        crawl_pdf()
    elif choice == '3':
        # 3、下载PDF
        crawl_pdf()
    else:
        print("无效的选项，请输入 1、2 或 3。")