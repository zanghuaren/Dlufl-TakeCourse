"""
教务系统 CAS 登录模块
"""

import re
import requests
import execjs
from bs4 import BeautifulSoup


def cas_login(username, password, des_js_path="des.js"):
    """
    CAS 登录

    Args:
        username: 学号
        password: 密码
        des_js_path: DES加密JS文件路径

    Returns:
        requests.Session: 登录成功的session对象，失败返回None
    """
    session = requests.Session()
    cas_login_url = "https://cas.dlufl.edu.cn/cas/login"
    service_url = "http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/caslogin.jsp"

    try:
        # 获取登录页面参数
        resp = session.get(cas_login_url, params={"service": service_url})
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        lt = soup.find("input", {"name": "lt"})["value"]
        execution = soup.find("input", {"name": "execution"})["value"]

        # 加密密码
        with open(des_js_path, "r", encoding="utf-8") as f:
            js_code = f.read()
        ctx = execjs.compile(js_code)
        rsa = ctx.call("strEnc", username + password + lt, "1", "2", "3")

        # 提交登录
        data = {
            "rsa": rsa,
            "ul": len(username),
            "pl": len(password),
            "lt": lt,
            "execution": execution,
            "_eventId": "submit"
        }

        resp = session.post(
            cas_login_url,
            params={"service": service_url},
            data=data,
            allow_redirects=False
        )

        # 完成认证
        ticket_url = resp.headers.get("Location")
        if ticket_url:
            session.get(ticket_url)
            # 预加载让cookie生效
            preload(session)
            return session
        return None

    except Exception as e:
        print(f"登录失败: {e}")
        return None


def get_jx0502zbid(session):
    """
    动态获取当前选课批次 jx0502zbid

    Args:
        session: 已完成 CAS 登录的 requests.Session

    Returns:
        str | None: 32位 jx0502zbid，获取失败返回 None
    """
    url = "http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxk/xklc_list"
    params = {'Ves632DSdyV': 'NEW_XSD_PYGL'}

    headers = {
        'Referer': 'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/framework/xsMain.jsp',
        'User-Agent': 'Mozilla/5.0',
    }

    resp = session.get(url, params=params, headers=headers, verify=False)
    resp.raise_for_status()

    html = resp.text

    # 优先：从链接中提取
    match = re.search(r'jx0502zbid=([A-Z0-9]{32})', html)
    if match:
        return match.group(1)

    return None


def preload(session):
    """
    预加载选课首页，让 JWGL cookie 与上下文生效
    """
    try:
        jx0502zbid = get_jx0502zbid(session)
        if not jx0502zbid:
            raise RuntimeError("未能获取 jx0502zbid")

        session.get(
            'http://jwgl.jiaowu.dlufl.edu.cn/jxjsxsd/xsxk/xsxk_index',
            params={'jx0502zbid': jx0502zbid},
            verify=False
        )

    except Exception as e:
        print(f"预加载失败,选课未开放: {e}")
