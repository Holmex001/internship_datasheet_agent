from datasheet_tools import search_datasheet, download_datasheet

if __name__ == "__main__":
    # 测试搜索工具
    res = search_datasheet.invoke({"part_number": "LM337"})
    print(res)

    # 测试下载，把厂商名复制上面打印出来的
    # res2 = download_datasheet.invoke({"part_number":"LM337", "vendor_name":"STMICROELECTRONICS"})
    # print(res2)