import os
import sys
from dotenv import load_dotenv
from langchain.tools import tool

# ============ 解决跨目录导入 elecfans 爬虫 ============
# 把项目根目录加入Python搜索路径
ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(ROOT_PATH)

# 导入爬虫类
from elecfans.main import ElecfansSpider

# 加载环境变量
load_dotenv()
DATASHEET_DIR = os.getenv("DATASHEET_DIR", default="./elecfans/downloads")
TOP_COMPANY_JSON_PATH = os.path.join(ROOT_PATH, "elecfans", "top_companies.json")
RESULT_JSON_PATH = os.path.join(ROOT_PATH, "elecfans", "results.json")

# 全局爬虫实例
spider = ElecfansSpider()


@tool
def search_datasheet(part_number: str) -> str:
    """
    在电子发烧友网站搜索指定芯片型号的数据手册，返回可用厂商列表。
    使用场景：用户询问某个芯片型号，需要查询有哪些厂商版本的数据手册时调用。
    注意：必须先执行本工具搜索，得到厂商列表后，才能调用download_datasheet下载文件。

    Args:
        part_number: 芯片型号，例如 "LM337", "LM317"

    Returns:
        字符串，包含所有匹配的厂商清单；若无搜索结果返回提示文本
    """
    try:
        # 执行搜索，自动生成 results.json
        spider.fetch_and_filter_results(part_number)
        # 筛选大厂优先
        vendor_list = spider.filter_top_companies(
            results_filepath=RESULT_JSON_PATH,
            top_companies_filepath=TOP_COMPANY_JSON_PATH
        )

        if not vendor_list:
            return f"未找到【{part_number}】符合大厂名单的数据手册。"

        output = [f"===== {part_number} 可用厂商列表 ====="]
        global _cached_search_result
        # 缓存搜索结果，后续下载工具可以复用匹配信息
        _cached_search_result = {}
        for idx, item in enumerate(vendor_list, start=1):
            manu = item["manufacturer"]
            model = item["model"]
            url = item["detail_url"]
            _cached_search_result[manu.upper()] = item
            output.append(f"{idx}. 厂商：{manu} | 型号：{model}")
        return "\n".join(output)

    except Exception as e:
        err_msg = str(e)
        if "Cookie" in err_msg or "401" in err_msg or "403" in err_msg:
            return "搜索失败！ELECFANS_COOKIE已失效，请更新.env内Cookie。"
        return f"搜索【{part_number}】异常：{err_msg}"


# 全局缓存：保存上一次search_datasheet返回的搜索数据，避免重复搜索
_cached_search_result = {}


@tool
def download_datasheet(part_number: str, vendor_name: str) -> str:
    """
    根据芯片型号+厂商名称，下载对应PDF数据手册到本地DATASHEET_DIR目录。
    前置条件：必须先调用search_datasheet完成搜索，获取厂商列表后再执行下载！

    Args:
        part_number: 芯片型号，例如 "LM337"
        vendor_name: 厂商名称，和search_datasheet返回名称保持一致，例如 "STMICROELECTRONICS"

    Returns:
        下载状态文本，成功返回本地PDF完整路径；失败返回错误原因
    """
    global _cached_search_result
    vendor_key = vendor_name.strip().upper()

    # 检查缓存中是否存在该厂商
    if vendor_key not in _cached_search_result:
        return f"错误：不存在厂商【{vendor_name}】，请先调用search_datasheet重新搜索 {part_number}！"

    item = _cached_search_result[vendor_key]
    detail_url = item["detail_url"]
    model = item["model"]
    manufacturer = item["manufacturer"]

    try:
        success = spider.download_pdf_from_link(
            detail_url=detail_url,
            model=model,
            manufacturer=manufacturer,
            save_dir=DATASHEET_DIR
        )
        if success:
            safe_model = re.sub(r'[\\/*?:"<>|]', "_", model)
            safe_manufacturer = re.sub(r'[\\/*?:"<>|]', "_", manufacturer)
            pdf_name = f"{safe_model}_{safe_manufacturer}.pdf"
            full_path = os.path.join(DATASHEET_DIR, pdf_name)
            return f"✅ 下载成功！\n器件：{part_number}\n厂商：{manufacturer}\n本地文件路径：{full_path}"
        else:
            return f"❌【{vendor_name} {part_number}】PDF下载失败，网页无法提取下载链接，可能Cookie失效。"

    except Exception as e:
        return f"下载异常：{str(e)}"


# 导出工具列表，Agent那边直接导入使用
DATASHEET_TOOLS = [search_datasheet, download_datasheet]