"""suki-refresh: 协议处理器 —— 静态站「本机刷新」把没在跑的本机服务静默拉起。

注册方式：双击 注册本机刷新.bat（HKCU 用户级注册表，无需管理员；卸载命令见 bat 尾部输出）。
职责边界：
- 只做「校验动作串 -> 探端口 -> 按需静默拉起 -> 等端口就绪 -> 退出」，不触发同步
  （触发由静态页经 CORS fetch 完成），不留常驻进程（拉起的服务自身随系统存活）。
- 动作串白名单：只认 suki-refresh:refresh（页面发起）与空动作，其余一律忽略。
  协议入口等于公开（页面源码是公开的），门禁是系统确认框；后果良性
  （拉起的是用户自己的三个本地服务），因此不做令牌校验。
- 子进程输出重定向 DEVNULL：pythonw 下无 stdout，服务里的 print 会 AttributeError。
"""
import datetime
import os
import socket
import subprocess
import sys
import time

ACTION = "suki-refresh:refresh"

# (端口, 启动脚本, 额外参数)；--no-browser = 协议拉起时不弹浏览器窗口
SERVICES = [
    (8231, r"D:\AAA_articafts\Bili Project\bili_fav.py", ("--no-browser",)),
    (8321, r"D:\AAA_articafts\Game Note\steam-play-data\server.py", ("--no-browser",)),
    (8642, r"D:\AAA_articafts\Anime Note\run.py", ("--no-browser",)),
]

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bili_link.log")


def log(msg):
    try:
        with open(LOG, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now():%Y-%m-%d %H:%M:%S} {msg}\n")
    except OSError:
        pass


def port_open(port):
    with socket.socket() as s:
        s.settimeout(0.4)
        return s.connect_ex(("127.0.0.1", port)) == 0


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args          # 测试用：只记日志不真拉起
    action = next((a for a in args if not a.startswith("--")), "")
    if action.rstrip("/") not in (ACTION, "suki-refresh:"):
        log(f"忽略未知动作: {action!r}")
        return
    started = []
    for port, script, extra in SERVICES:
        if port_open(port):
            continue
        if dry:
            log(f"[dry] 将拉起 {script}")
            started.append(port)
            continue
        try:
            subprocess.Popen(
                [sys.executable, script, *extra],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                cwd=os.path.dirname(script))
            started.append(port)
            log(f"拉起 {script}")
        except OSError as e:
            log(f"启动失败 {script}: {e}")
    deadline = time.time() + 20
    pending = set(started)
    while pending and time.time() < deadline:
        time.sleep(0.5)
        pending = {p for p in pending if not port_open(p)}
    if started:
        log(f"完成: 拉起={started} 未就绪={sorted(pending)}")


if __name__ == "__main__":
    main()
