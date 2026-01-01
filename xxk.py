"""
选修课选课模块
"""
from tabulate import tabulate
import os
import json

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
}
# 这个header必须保留，否则选修选课会失败


def get_xxk(session):
    """
    返回所有选修课的json
    """
    url = 'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxkkc/xsxkXxxk'
    data = {
        'sEcho': '1',
        'iColumns': '9',
        'sColumns': '',
        'iDisplayStart': '0',
        'iDisplayLength': '3',
        'mDataProp_0': 'kch',
        'mDataProp_1': 'kcmc',
        'mDataProp_2': 'xf',
        'mDataProp_3': 'skls',
        'mDataProp_4': 'sksj',
        'mDataProp_5': 'skdd',
        'mDataProp_6': 'xqmc',
        'mDataProp_7': 'ctsm',
        'mDataProp_8': 'czOper',
    }
    resp = session.get(url, headers=headers, params=data, verify=False)

    return resp.json()


def parse_xxxk_courses(data):
    """
    解析 get_xxk 返回的 JSON，
    只保留：课程名、课程时间、课程老师、课程ID、课程状态

    Args:
        data (dict): xsxkXxxk 接口返回的 JSON

    Returns:
        list[dict]: 精简后的课程列表
    """
    result = []

    aa_data = data.get("aaData", [])
    for course in aa_data:
        item = {
            "course_id": course.get("jx0404id"),   # 选课用的ID
            "course_name": course.get("kcmc"),
            "course_time": course.get("sksj")[-8:],
            "teacher": course.get("skls"),
            "is_choose": "不可选" if "冲突" in course.get("ctsm") else "可选"
            # 原意是表达是否冲突，但选修和必修必然不可能冲突，冲突只可能是已经选了，因此可以表示是否已选。
        }
        result.append(item)
    return result


def print_xxcourses_tabulate(courses):
    """
    打印选修课程
    """
    table = []
    for c in courses:
        table.append([
            c.get("course_name"),
            c.get("course_time"),
            c.get("teacher"),
            c.get("course_id"),
            c.get("is_choose")
        ])

    print(tabulate(
        table,
        headers=["课程名", "上课时间", "教师", "课程ID", "状态"],
        # tablefmt="grid",
        stralign="left"

    ))


def xxxk(session, pool, courses):
    """
    根据选修课池自动选课

    Args:
        session (requests.Session): 已登录 CAS session
        pool (list[str]): 想选的课程名列表
        courses (list[dict]): parse_xxxk_courses 返回的课程列表

    Returns:
        bool: 所有课是否选课成功
    """
    result = []
    for course in courses:
        if course["course_name"] in pool:
            if course["is_choose"] == "不可选":
                course["selected_status"] = "已选或冲突"
                continue
            try:
                url = f"http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxkkc/xxxkOper?jx0404id={course['course_id']}"
                resp = session.get(url, headers=headers, verify=False)
                res_json = resp.json()
                if res_json.get("success") is True:
                    result.append(1)
                    course["selected_status"] = "选课成功"
                    course["is_choose"] = "选课成功"
                else:
                    course["selected_status"] = f"选课失败 {res_json}"
            except Exception as e:
                course["selected_status"] = f"异常 {e}"
    print(result, pool)
    if len(result) == len(pool):
        return True
