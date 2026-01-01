from jwgl_auth import cas_login, get_jx0502zbid
from xxk import *
from tyk import *

import time
import requests
from datetime import datetime


USERNAME = "请填写你的账号"
PASSWORD = "请填写你的密码"
# 填写账号密码
xx_except_pool = ["旅游伦理学", "旅游大数据", "服务运营管理（双语）"]
ty_except_pool = {"跆拳道": "张淼"}
# 填写想选的选修课和体育课，体育课也支持填写多个，此处替换你你自己的课。


headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36',
    # 基础请求头，仅包含ua即可
}


def login():
    print("正在登录...")
    session = cas_login(USERNAME, PASSWORD)
    if not session:
        print("登录失败")
        exit(1)
    os.system("cls")
    print("登录成功\n")
    return session


def get_current_semester():
    """
    根据当前日期返回学期字符串
    判断依据示例：
      - 2025-2026-1：5月-10月之间
      - 2025-2026-2：10月-次年5月之间
    """
    now = datetime.now()
    year = now.year
    month = now.month

    if 5 <= month < 10:
        semester = f"{year}-{year + 1}-1"
    else:

        if month < 5:
            semester = f"{year - 1}-{year}-2"
        else:
            semester = f"{year}-{year + 1}-2"
    return semester


def main():

    while True:
        os.system("cls")
        current_time = datetime.now()
        print(current_time)
        try:
            session = login()
            data = {
                'jx0502zbid': get_jx0502zbid(session),
                'xnxq01id': get_current_semester(),
            }
            response = session.post(
                'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxk/doYjxzbx',
                data=data,  # 注：请求时一定要带上这个data参数，否则依然会返回成功但实际失败
                verify=False,
            )
            print("正在全选必修课...")
            if '一键选择必修成功' in response.text:
                print("必修课全选成功！\n")
                bx_result = True

            courses = parse_xxxk_courses(get_xxk(session))
            print("正在获取所有选修课：\n")
            print_xxcourses_tabulate(courses)
            xx_result = xxxk(session, xx_except_pool, courses)
            print("\n当前选课池：", end='')
            print(xx_except_pool)
            print("选课池执行完毕，最新状态：\n")
            print_xxcourses_tabulate(courses)

            courses = parse_tyxk_courses(get_tyk(session))
            print("\n")
            print_tycourses_tabulate(courses)
            print("\n当前选课池：", end='')
            print(ty_except_pool, end='')
            ty_result = tyxk(session, ty_except_pool, courses)

            if bx_result and xx_result and ty_result:
                break
        except:
            time.sleep(1)
            print("正在尝试重新登录...")


if __name__ == '__main__':

    main()
