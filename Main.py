import gxk_data
import time
import os
import pandas as pd
import json
import requests
from tabulate import tabulate


with open("Cookie.json", "r", encoding="utf-8") as file:
    cookies = json.load(file)  # 将 JSON 数据加载为 Python 字典

headers = {
    'Accept': '*/*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Origin': 'http://jwgl.jiaowu.dlufl.edu.cn',
    'Proxy-Connection': 'keep-alive',
    'Referer': 'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxkkc/comeInBxxk',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    'X-Requested-With': 'XMLHttpRequest',
}

data = {
    'sEcho': '1',
    'iColumns': '9',
    'sColumns': '',
    'iDisplayStart': '0',
    'iDisplayLength': '5000',
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


def add_id(id):
    """用于管理选课池中的课程ID。
    
    - 以'+'开头的ID将被添加到选课池。
    - 以'-'开头的ID将被从选课池中移除。
    - 输入空ID或无效ID将被忽略。
    - 文件路径为"ID.txt"，ID长度必须为16位。
    """
    # 文件路径
    file_path = "ID.txt"

    # 读取当前文件中的 ID
    try:
        with open(file_path, "r") as f:
            choose_list = [line.strip() for line in f.readlines()]
    except FileNotFoundError:
        choose_list = []

    # 检查 ID 长度是否为 16
    if len(id) == 16:
        if id[0] == '+':
            # 以 '+' 开头，添加到列表（去重）
            id_to_add = id[1:]
            if id_to_add not in choose_list:
                choose_list.append(id_to_add)
                print("添加成功！当前ID池：")
            else:
                print("ID 已经存在，无法重复添加！")

        elif id[0] == '-':
            # 以 '-' 开头，移除列表中的 ID
            id_to_remove = id[1:]
            if id_to_remove in choose_list:
                choose_list.remove(id_to_remove)
                print("移除成功！当前ID池：")
            else:
                print("ID 不在列表中，无法移除！")

        else:
            print("ID 格式错误：必须以 '+' 或 '-' 开头！")
    elif id == '':
        pass
    else:
        print("ID 无效：长度必须为 16 位！")

    # 更新文件中的 ID 列表（去重）
    with open(file_path, "w") as f:
        for id in set(choose_list):  # 使用 set 去重
            f.write(id + "\n")

    # 打印当前 ID 池
    print("当前 ID 池：")
    for i in set(choose_list):  # 使用 set 去重
        print(i)


def pre_load():
    """预加载函数，确保cookie有效并初始化选课环境。
    
    即使cookie正确，也必须先访问这个URL才能开始选课。
    """
    params = {
        'jx0502zbid': '57CC78AC27EE439C98DE2A3121D0AE3D',
    }
    response = requests.get(
        'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxk/xsxk_index',
        params=params,
        cookies=cookies,
        headers=headers,
        verify=False,
    )
    response.close()


def print_course(courses):
    """打印课程列表，主要用于调试。
    
    参数：
        courses (list): 包含课程信息的字典列表。
    返回：
        int: 课程总数。
    """
    i = 0
    for course in courses:
        class_name = course.get('class_name', '未知课程')
        class_id = course.get('class_id', '未知ID')
        class_time = course.get('class_time', '未知课程')
        class_teacher = course.get('class_teacher', '未知课程')
        i += 1
    return i


def ls_course(url):
    """获取课程列表。
    
    参数：
        url (str): 请求的URL地址。
    返回：
        list: 包含课程信息的字典列表。
    """
    response = requests.post(
        url,
        cookies=cookies,
        headers=headers,
        data=data,
        verify=False,
    )
    content = json.loads(response.text)['aaData']
    courses = []

    for each_class in content:
        if each_class['skls']:
            class_name = each_class['kcmc']
            class_id = each_class['jx0404id']
            class_time = each_class['sksj'].replace('<br>', '')
            class_teacher = each_class['skls']
            courses.append({
                'class_name': class_name,
                'class_id': class_id,
                'class_time': class_time,
                'class_teacher': class_teacher
            })
    return courses


def find_course(file, *keywords):
    """根据关键字查找课程。
    
    参数：
        file (str): CSV 文件路径。
        *keywords (str): 关键字。
    返回：
        str: 表格化的查询结果或"无"。
    """
    df = pd.read_csv(file)
    df["combined"] = df.apply(lambda row: " ".join(map(str, row)), axis=1)
    for keyword in keywords:
        df = df[df["combined"].str.contains(keyword, na=False, case=False)]
    df = df.drop(columns=["combined"])
    if df.empty:
        return "无"
    return tabulate(df, headers="keys", tablefmt="simple", showindex=False)


def bx_course(url1, url2):
    """选择必修课程。
    
    参数：
        url1 (str): 课程列表请求地址。
        url2 (str): 选课操作请求地址。
    """
    course_list = ls_course(url1)
    len = print_course(course_list)
    print(f"当前课程共有{len}节课可选————")
    for i in range(0, len):
        class_teacher = course_list[i]['class_teacher']
        class_name = course_list[i]['class_name']
        class_id = course_list[i]['class_id']
        class_time = course_list[i]['class_time']
        print(f'\n{class_teacher.ljust(4, "　")}{class_name}\n{class_id}\n{class_time}')
        params = {'jx0404id': class_id}
        resp = requests.get(url2, params=params, cookies=cookies, headers=headers, verify=False)
        resp.close()
        if resp.json()['success']:
            print('选课成功！')
        else:
            print(resp.json()['message'])
        print('----------------------------------')


def xx_course(url1, url2):
    """选择选修课程。
    
    参数：
        url1 (str): 课程列表请求地址。
        url2 (str): 选课操作请求地址。
    """
    course_list = ls_course(url1)
    len_courses = len(course_list)
    print_course(course_list)
    print(f"当前课程共有{len_courses}节课可选————")
    course_dict = {}
    for i in range(len_courses):
        class_teacher = course_list[i]['class_teacher']
        class_name = course_list[i]['class_name']
        class_id = course_list[i]['class_id']
        class_time = course_list[i]['class_time']
        print(f'\n{i + 1}. {class_teacher.ljust(4, "　")}{class_name}\n{class_id}\n{class_time}')
        course_dict[i + 1] = class_id
    selected_indexes = input("\n请输入课程序号，用英文逗号分隔：").split(",")
    for index in selected_indexes:
        index = int(index.strip())
        if index in course_dict:
            class_id = course_dict[index]
            params = {'jx0404id': class_id}
            resp = requests.get(url2, params=params, cookies=cookies, headers=headers, verify=False)
            resp.close()
            if resp.json()['success']:
                print(f'选课成功！课程ID: {class_id}')
            else:
                print(f"选课失败！{resp.json()['message']}")
        else:
            print(f"无效的序号：{index}")


def public_course(url, id):
    """选择公选课程。
    
    参数：
        url (str): 选课请求地址。
        id (str): 课程ID。
    返回：
        bool: 选课是否成功。
    """
    params = {
        'jx0404id': id,
        'xkzy': '',
        'trjf': '',
    }
    resp = requests.get(url, params=params, cookies=cookies, headers=headers, verify=False)
    resp.close()
    if resp.json()['success']:
        print('选课成功！')
        return True
    else:
        print(resp.json()['message'])
        return False


def cancel_course(url, id):
    """退选课程。
    
    参数：
        url (str): 退课请求地址。
        id (str): 课程ID。
    返回：
        bool: 退课是否成功。
    """
    params = {'jx0404id': id}
    resp = requests.get(url, params=params, cookies=cookies, headers=headers, verify=False)
    resp.close()
    if resp.json()['success']:
        print('退课成功！')
        return True
    else:
        print('该课程还未选择！')
        return False


def main():
    """主函数，程序入口。
    
    提供多种选课模式，包括必修、选修、循环选课、查找公选课等功能。
    """
    pre_load()
    url1 = 'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxkkc/xsxkBxxk'
    url2 = 'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxkkc/xsxkXxxk'
    url3 = 'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxkkc/ggxxkxkOper'
    url4 = 'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxkkc/bxxkOper'
    url5 = 'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxkjg/xstkOper'
    while True:
        print("=============================")
        print(" 输入1进入必修选课")
        print(" 输入2进入选修选课")
        print(" 输入3进入循环选课模式")
        print(" 输入4查找或选择公共选修课")
        print(" 输入5加载选修课数据")
        print(" 输入6进入退课模式")
        print("=============================")
        i = input("Please Enter:")
        if int(i) == 0:
            break
        try:
            if int(i) == 1:
                os.system('cls')
                bx_course(url1, url4)
                print("所有必修课选择成功！")
                os.system('pause')
                os.system('cls')
            elif int(i) == 2:
                os.system('cls')
                xx_course(url2, url4)
                os.system('pause')
                os.system('cls')
            elif int(i) == 3:
                while True:
                    os.system('cls')
                    print("本模式适用于指定课程已没有名额，但有人退课的情况下可以及时选到，选课池内容永久保存。")
                    print("=============================")
                    print("输入0退出")
                    print("输入1设置选课池")
                    print("输入2在选课池中开始选课")
                    print("=============================")
                    words = input("请输入：")
                    if words == '0':
                        break
                    elif words == '1':
                        print("说明：如输入+ID标明添加，-ID表明移除，输入0退出。")
                        add_id("")
                        while True:
                            id = input("Please Enter Course ID:")
                            if id == '0':
                                break
                            add_id(id)
                    elif words == '2':
                        sum = 0
                        while True:
                            with open("ID.txt", "r") as f:
                                ids = [line.strip() for line in f.readlines()]
                            sum += 1
                            print(f"\n第{sum}次尝试：")
                            for id in ids:
                                print(id)
                                if public_course(url3, id):
                                    break
                            time.sleep(1.5)
            elif int(i) == 4:
                os.system('cls')
                print("输入课程名称则搜索，输入课程ID则选课，输入0退出。")
                print("说明：例如最后一列3/30表示课程容量30人，已选3人。搜索支持星期几、老师、课程类型等。")
                while True:
                    words = input("\n请输入：").replace('，', ',')
                    if words == '0':
                        break
                    elif len(words) == 15:
                        os.system('cls')
                        public_course(url3, words)
                        os.system('pause')
                    else:
                        words = words.split(",")
                        results = find_course("data.csv", *words)
                        print(results)
            elif int(i) == 5:
                gxk_data.get_data()
                os.system('cls')
                print("提取完成！")
            elif int(i) == 6:
                words = input("请输入退课ID：")
                cancel_course(url5, words)
                os.system('pause')
                os.system('cls')
        except:
            os.system('cls')


if __name__ == '__main__':
    main()
