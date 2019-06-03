import re
from datetime import datetime


def timestamp2strdt(timestamp):
    # datetime.fromtimestamp(timeStamp).strftime("%Y-%m-%d %H:%M:%S.%f")
    return datetime.fromtimestamp(int(timestamp)).strftime("%Y-%m-%d %H:%M:%S")


def trans_2_md(string):
    """
    文本转化为字典列表; 注意这里考虑了递归书签但是未启用
    如果有兴趣可以复写。但是递归书签在markdown中也不好显示。
    :param string:
    :return:
    """
    partern = """<DT><H3 ADD_DATE="(\d+)" LAST_MODIFIED="(\d+)">(.*?)</H3>.*?<DL><p>(.*?)</DL><p>"""
    datas = re.findall(partern, string)
    results = []
    for add_date, last_modify, mark_tag, contents in datas:
        info = dict(
            mark_tag=mark_tag,
            add_date=timestamp2strdt(add_date),
            last_modify=timestamp2strdt(last_modify),
            type="d",
            childs=trans_2_md(contents)
        )
        line_partern = """<DT><A HREF="(.*?)" ADD_DATE="(\d+)".*?">(.*?)</A>"""
        _marks = re.findall(line_partern, contents)
        marks = []
        for href, add_date, mark_name in _marks:
            marks.append(dict(
                href=href,
                add_date=timestamp2strdt(add_date),
                mark_name=mark_name.replace("|","_").replace(".", "。")[:40],
                type="f"
            ))

        info.setdefault("marks", marks)
        results.append(info)
    return results


def main(book_marks_path):
    """
    主要执行的函数
    :param book_marks_path: 输入你的导出书签html的位置
    :return: 运行脚本的当前目录下生成一个 output.md 文件
    """
    with open(book_marks_path, "r", encoding="utf-8") as f:
        string = f.read().replace("\n", "")
        f.close()
    results = trans_2_md(string)
    md_string = """"""
    for x in results:
        md_string += """## {}""".format(x["mark_tag"]) +"\n"
        md_string += """> _创建时间_ **{}**  _最后修改_ **{}**>>""".format(x["add_date"], x["last_modify"]) +"\n"
        md_string += "> \n"
        md_string += "|{mark_name}|{href}|{add_date}|\n".format(**dict( href="链接", add_date="添加时间", mark_name="书签名称",))
        md_string += "|------------------|------------------|-----------------|" + "\n"
        for mark in x["marks"]:
            md_string += "|[{mark_name}]({href})|{href}|{add_date}|".format(**mark) + "\n"
        md_string += "\n"

    with open("output.md", "w+", encoding="utf-8") as f:
        f.write(md_string)
        f.close()


if __name__ == '__main__':
    book_marks_path = "e://bookmarks_2019_6_3.html"
    main(book_marks_path)

