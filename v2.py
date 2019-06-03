import re
import sys
from datetime import datetime

from urllib.parse import urlparse


def timestamp2strdt(timestamp):
    # datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S.%f")

    try:
        return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")
    except:
        print("ERROR: 错误的日期格式化-->"+ timestamp)
        return str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def trans_2_md(string):
    """
    文本转化为字典列表; 注意这里考虑了递归书签但是未启用
    如果有兴趣可以复写。但是递归书签在markdown中也不好显示。
    :param string:
    :return:
    """
    # datas = re.findall(partern, string)
    rx = re.compile("""<H3 ADD_DATE="(\d+)" LAST_MODIFIED="(\d+)".*?>(.*?)</H3>\s*<DL><p>(.*?)<\DL><p>""")
    datas = rx.findall(string)
    results = []
    for add_date, last_modify, mark_tag, contents in datas:
        info = dict(
            mark_tag=mark_tag,
            add_date=timestamp2strdt(add_date),
            last_modify=timestamp2strdt(last_modify),
            type="d",
            childs=trans_2_md(contents)
        )
        line_partern = """<A HREF="(.*?)" ADD_DATE="(\d+)".*?">(.*?)</A>"""
        _marks = re.findall(line_partern, contents)
        marks = []
        for href, add_date, mark_name in _marks:
            marks.append(dict(
                href=href,
                host=str(urlparse(href).netloc),
                scheme=urlparse(href).scheme,
                add_date=timestamp2strdt(add_date),
                mark_name=mark_name.replace("|","_").replace(".", "。").replace(
                    "[", "【").replace("]", "】")[:40],
                type="f"
            ))

        info.setdefault("marks", marks)
        results.append(info)
    return results


def main(book_marks_path, output="output.md"):
    """
    主要执行的函数
    :param book_marks_path: 输入你的导出书签html的位置
    :return: 运行脚本的当前目录下生成一个 output.md 文件
    """
    with open(book_marks_path, "r", encoding="utf-8") as f:
        string = f.read().replace("\n", "")
        # 修改DT这种象征性换行的标签为空; DT就是一个换行的标志。
        string = string.replace("<DT>", "")
        f.close()
    results = trans_2_md(string)
    md_string = """"""
    for x in results:
        md_string += """## {}""".format(x["mark_tag"]) +"\n"
        md_string += """> _创建时间_ **{}**  _最后修改_ **{}**>>""".format(x["add_date"], x["last_modify"]) +"\n"
        md_string += "> \n"
        #md_string += "|{mark_name}|{href}|{add_date}|\n".format(**dict( href="链接", add_date="添加时间", mark_name="书签名称",))
        md_string += "|{mark_name}|{href}|{add_date}|\n".format(**dict( href="链接", add_date="添加时间", mark_name="书签名称",))
        md_string += "|------------------|------------------|-----------------|" + "\n"
        for mark in x["marks"]:
            md_string += "|[{mark_name}]({href})|{host}|{add_date}|".format(**mark) + "\n"
        md_string += "\n"

    with open(output, "w+", encoding="utf-8") as f:
        f.write(md_string)
        f.close()

    return True


if __name__ == '__main__':
    print("使用说明: python3 v2.py e://test.html a.md")
    if len(sys.argv) < 2:
        raise EOFError("必须指定一个Google书签html文件路径")
    google_marks_html_path = sys.argv[1]
    try:
        output = sys.argv[2]
    except:
        print("第二个参数是输出的文件位置")
        output = "output.md"
    main(google_marks_html_path, output)

