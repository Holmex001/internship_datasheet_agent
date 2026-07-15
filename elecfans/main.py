# https://pdf.elecfans.com/ 的爬虫实现，支持搜索、筛选和下载 PDF 数据手册。

import requests
from bs4 import BeautifulSoup
import re
import urllib.parse
import json
import os
from dotenv import load_dotenv

load_dotenv()

class ElecfansSpider:
    def __init__(self):
        self.session = requests.Session()

        # 保持您的 Cookie
        cookie_str = os.getenv("ELECFANS_COOKIE")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Cookie": cookie_str
        }

    def fetch_and_filter_results(self, keyword):
        print(f"🔍 正在搜索关键词: [{keyword}] ...")
        search_url = f"https://pdf.elecfans.com/Search?f=&q={keyword}"

        try:
            response = self.session.get(search_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 1. 抓取页面上所有的 PDF 详情页链接
            all_results = []
            dl_btns = soup.find_all('a', class_='dl-btn')

            if not dl_btns:
                print("❌ 未在搜索结果中找到任何数据手册链接。")
                return

            print(f"抓取到 {len(dl_btns)} 条初步结果，正在解析并筛选...")

            for btn in dl_btns:
                if 'href' not in btn.attrs:
                    continue

                href = btn['href']

                # 利用正则从 href 中提取 厂商 和 型号
                # 例如: /LINER/LM337.html#pdf
                match = re.search(r'/([^/]+)/([^/]+)\.html', href)
                if match:
                    manufacturer = match.group(1)
                    model_name = match.group(2)
                else:
                    manufacturer = "Unknown"
                    model_name = "Unknown"

                # 拼接完整的详情页 URL
                detail_url = urllib.parse.urljoin("https://pdf.elecfans.com", href)

                all_results.append({
                    "keyword": keyword,
                    "model": model_name,
                    "manufacturer": manufacturer,
                    "detail_url": detail_url
                })

            # 2. 进行数据筛选 (精确匹配 vs 默认前 5 个)
            final_results = self._filter_logic(all_results, keyword)

            # 3. 将最终结果保存为 JSON
            self._save_to_json(final_results, "results.json")

        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求出错: {e}")

    def _filter_logic(self, all_results, keyword):
        """核心筛选逻辑"""
        exact_matches = []

        # 遍历所有结果，寻找完全匹配的型号（忽略大小写）
        for item in all_results:
            if item["model"].strip().upper() == keyword.strip().upper():
                exact_matches.append(item)

        if exact_matches:
            print(f"✅ 找到 {len(exact_matches)} 个完全匹配「{keyword}」的型号！")
            return exact_matches
        else:
            # 如果没有完全匹配的，截取前 5 个
            fallback_results = all_results[:5]
            print(f"⚠️ 未找到完全匹配「{keyword}」的型号，已截取排名前 {len(fallback_results)} 的搜索结果。")
            return fallback_results

    def _save_to_json(self, data, filename):
        """保存为 JSON 文件"""
        # ensure_ascii=False 保证中文字符正常显示，indent=4 让 JSON 文件有良好的缩进排版
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"📁 筛选完成！数据已成功保存至当前目录下的: {filename}")

    def filter_top_companies(self, results_filepath, top_companies_filepath):
        """
        传入 results.json 的地址和 top_companies.json 的地址，
        筛选出有名公司的数据手册，并最终输出一个字典数组 (JSON 集合)。
        """
        # 1. 检查文件是否存在
        if not os.path.exists(results_filepath):
            print(f"❌ 找不到结果文件: {results_filepath}")
            return []
        if not os.path.exists(top_companies_filepath):
            print(f"❌ 找不到有名公司名录: {top_companies_filepath}")
            return []

        # 2. 读取“有名公司”白名单，并全部转换为大写以实现忽略大小写的匹配
        with open(top_companies_filepath, 'r', encoding='utf-8') as f:
            top_companies_list = json.load(f)

        # 清洗：去除首尾空格并转大写
        top_companies_upper = [comp.strip().upper() for comp in top_companies_list]

        # 3. 读取待筛选的爬虫结果数据
        with open(results_filepath, 'r', encoding='utf-8') as f:
            all_results = json.load(f)

        filtered_array = []

        # 4. 核心筛选逻辑
        for item in all_results:
            # 获取当前数据的厂商名称，转为大写
            manufacturer = item.get("manufacturer", "").strip().upper()

            is_top_company = False

            # 遍历白名单进行比对
            for top_comp in top_companies_upper:
                # 采用“包含”判定：例如 "LINER[LINEAR TECHNOLOGY]" 包含 "LINER"
                if top_comp in manufacturer or manufacturer in top_comp:
                    is_top_company = True
                    break  # 只要匹配中一个白名单名字，就认定为有名公司，跳出内层循环

            # 如果验证通过，加入到最终的输出数组中
            if is_top_company:
                filtered_array.append(item)

        # 5. 打印统计信息并返回数组
        print(f"✅ 筛选完成！原始数据共 {len(all_results)} 条，成功筛选出大厂数据 {len(filtered_array)} 条。")
        return filtered_array

    def download_pdf_from_link(self, detail_url, model, manufacturer, save_dir="downloads"):
        """
        给它具体的详情页链接，它负责使用“撒网式正则”提取 fileid 并下载 PDF 文件。
        修复了 fileid 长度判断的 bug (兼容 24位和 32位)。
        """
        print(f"🔗 准备从链接提取下载: {detail_url}")
        try:
            # 1. 访问详情页
            headers = self.headers.copy()
            headers["Referer"] = "https://pdf.elecfans.com/Search"

            res = self.session.get(detail_url, headers=headers)
            res.raise_for_status()

            # --- 修正后的正则提取策略 ---
            file_id = None

            # 策略 A：优先寻找带有 "fileid" 关键字的赋值 (兼容 24 到 32 位的字母数字)
            # 例如 match: fileid="2a73d1a1bbdb6679d7219e8a" 或 fileid: '...'
            match = re.search(r'fileid[\s=:\'"]+([a-fA-F0-9]{24,32})', res.text, re.IGNORECASE)
            if match:
                file_id = match.group(1)

            # 策略 B：无差别撒网，直接找出所有被引号包裹的 24 位 16进制字符串 (典型的 MongoDB ID)
            if not file_id:
                hashes_24 = re.findall(r'["\']([a-fA-F0-9]{24})["\']', res.text)
                if hashes_24:
                    file_id = hashes_24[0]

                    # 策略 C：万一其他页面是 32 位，兜底查找 32 位字符串
            if not file_id:
                hashes_32 = re.findall(r'["\']([a-fA-F0-9]{32})["\']', res.text)
                if hashes_32:
                    file_id = hashes_32[0]

            if not file_id:
                print(f"❌ 下载失败：网页中未发现 24/32 位的特征码。({detail_url})")
                return False

            print(f"✅ 成功提取特征码 (fileid): {file_id}，正在发起下载...")

            # 2. 发起真实的下载请求
            download_url = f"https://pdf.elecfans.com/Product/down?fileid={file_id}"
            dl_headers = self.headers.copy()
            dl_headers["Referer"] = detail_url

            dl_res = self.session.get(download_url, headers=dl_headers, stream=True)
            dl_res.raise_for_status()

            # 3. 提取文件名
            safe_model = re.sub(r'[\\/*?:"<>|]', "_", model)
            safe_manufacturer = re.sub(r'[\\/*?:"<>|]', "_", manufacturer)
            filename = f"{safe_model}_{safe_manufacturer}.pdf"
            # 4. 创建文件夹并保存文件

            if not os.path.exists(save_dir):
                os.makedirs(save_dir)

            filepath = os.path.join(save_dir, filename)

            with open(filepath, 'wb') as f:
                for chunk in dl_res.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

            print(f"🎉 下载成功！文件保存至: {filepath}")
            return True

        except requests.exceptions.RequestException as e:
            print(f"❌ 网络请求出错: {e}")
            return False

    def download_batch(self, filtered_array):
        """
        批量下载筛选后的数据手册。
        """
        if not filtered_array:
            print("⚠️ 没有可下载的文件。请先进行筛选。")
            return

        for item in filtered_array:
            model = item.get("model", "UnknownModel")
            manufacturer = item.get("manufacturer", "UnknownManufacturer")
            detail_url = item.get("detail_url")

            if detail_url:
                self.download_pdf_from_link(detail_url, model, manufacturer)
            else:
                print(f"⚠️ 缺少详情页链接，无法下载: {model} ({manufacturer})")

if __name__ == "__main__":
    spider = ElecfansSpider()
    spider.fetch_and_filter_results("LM337")
    # spider.download_pdf_from_link("https://pdf.elecfans.com/LINER/LM337.html", "LM337", "LINER")
    filtered_array = spider.filter_top_companies(top_companies_filepath="top_companies.json", results_filepath="results.json")
    spider.download_batch(filtered_array)