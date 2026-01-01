"""
体育课选课模块
"""
from tabulate import tabulate
import re

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'http://jwgl.jiaowu.dlufl.edu.cn',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxkkc/comeInGgxxkxk',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}


def get_tyk(session):
    """
    返回所有体育课的json
    """
    url = 'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxkkc/xsxkGgxxkxk'
    data = {
        'sEcho': '1',
        'iColumns': '12',
        'sColumns': '',
        'iDisplayStart': '0',
        'iDisplayLength': '15',
        'mDataProp_0': 'kch',
        'mDataProp_1': 'kcmc',
        'mDataProp_2': 'xf',
        'mDataProp_3': 'skls',
        'mDataProp_4': 'sksj',
        'mDataProp_5': 'skdd',
        'mDataProp_6': 'xqmc',
        'mDataProp_7': 'xkrs',
        'mDataProp_8': 'syrs',
        'mDataProp_9': 'ctsm',
        'mDataProp_10': 'szkcflmc',
        'mDataProp_11': 'czOper',
        'kcxx': '',
        'skls': '',
        'skxq': '',
        'skjc': '',
        'sfym': 'true',
        'sfct': 'true',
        'szjylb': '11',
    }
    resp = session.get(url, headers=headers, params=data, verify=False)

    return resp.json()


def parse_tyxk_courses(data):
    """
    解析 get_tyk 返回的 JSON，
    只保留：课程类型、课程名、课程时间、课程老师、课程ID、选课情况

    Args:
        data (dict): xsxkGgxxkxk 接口返回的 JSON

    Returns:
        list[dict]: 精简后的课程列表
    """
    result = []

    aa_data = data.get("aaData", [])
    for course in aa_data:
        item = {
            "course_type": course.get("kcmc"),
            "course_name": course.get("fzmc"),
            "course_time": course.get("sksj")[-8:],
            "teacher": course.get("skls"),
            "course_id": course.get("jx0404id"),   # 选课用的ID
            "Remaining": course.get("syrs"),
            "total": int(course.get("syrs")) + course.get("xkrs"),
            "selected_status": "可选"
        }
        result.append(item)
    return result


def print_tycourses_tabulate(courses):
    """
    打印选修课程
    """
    table = []
    for c in courses:
        table.append([
            c.get("course_type"),
            c.get("course_name"),
            c.get("course_time"),
            c.get("teacher"),
            c.get("course_id"),
            c.get("Remaining"),
            c.get("total"),
            c.get("selected_status")
        ])

    print(tabulate(
        table,
        headers=["课程类型", "课程名", "上课时间", "教师", "课程ID", "剩余名额", "总名额", "状态"],
        # tablefmt="grid",
        stralign="left"

    ))


def tyxk(session, pool, courses):
    """
    根据选修课池自动选课

    Args:
        session (requests.Session): 已登录 CAS session
        pool (list[str]): 想选的体育课程名列表
        courses (list[dict]): parse_xxxk_courses 返回的课程列表

    Returns:
        bool：表示选课成功或失败
    """
    for course in courses:
        courses_name = re.sub(r'\d+', '', course["course_name"])
        if courses_name in pool and course["teacher"] == pool[courses_name]:
            if int(course["Remaining"]) == 0:
                course["selected_status"] = "课程已满"
                continue
            try:
                params = {
                    'jx0404id': course["course_id"], 'xkzy': '', 'trjf': ''}
                url = 'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxkkc/ggxxkxkOper'
                resp = session.get(url=url, params=params,
                                   headers=headers, verify=False)
                res_json = resp.json()
                if res_json.get("success") is True:
                    course["selected_status"] = "选课成功"
                    print(f"\n选课成功，已选择{course["teacher"]}-{courses_name}!")
                    return True
                else:
                    course["selected_status"] = f"选课失败 {res_json}"
            except Exception as e:
                course["selected_status"] = f"异常 {e}"
    else:
        print("所有体育课都选择失败！")
        return False
