import os
import subprocess
import ctypes

def broadcast_setting_change():
    """
    使用 Windows API 通知所有窗口环境变量已更改，以便它们可以重新加载。
    """
    HWND_BROADCAST = 0xFFFF
    WM_SETTINGCHANGE = 0x001A
    SMTO_ABORTIFHUNG = 0x0002
    result = ctypes.windll.user32.SendMessageTimeoutW(
        HWND_BROADCAST,
        WM_SETTINGCHANGE,
        0,
        "Environment",
        SMTO_ABORTIFHUNG,
        5000,  # 5秒超时
        None
    )
    return result

def toggle_proxy():
    """
    切换（设置或清除）系统代理环境变量。
    """
    proxy_address = 'http://127.0.0.1:33000'
    proxy_vars = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']
    
    # 检查当前是否设置了任何代理环境变量
    is_proxy_set = any(os.environ.get(var) for var in proxy_vars)

    print("--- 当前代理状态 ---")
    for var in proxy_vars:
        print(f"  {var}: '{os.environ.get(var, '')}'")
    print("------------------------")

    if not is_proxy_set:
        print(f"正在设置代理为 {proxy_address}...")
        try:
            for var in proxy_vars:
                # 使用 setx 设置用户环境变量
                subprocess.run(['setx', var, proxy_address], shell=True, check=True, capture_output=True)
            print("代理已成功设置。")
        except subprocess.CalledProcessError as e:
            # 如果命令执行失败，打印错误信息
            print(f"设置代理时出错: {e.stderr.decode('gbk', errors='ignore')}")
            return
    else:
        print("正在清除代理设置...")
        try:
            for var in proxy_vars:
                # 使用 reg delete 从注册表中删除环境变量，这比 `setx var ""` 更可靠
                subprocess.run(
                    ['reg', 'delete', 'HKCU\Environment', '/v', var, '/f'],
                    shell=True, check=False, capture_output=True
                )
            print("代理已成功清除。")
        except subprocess.CalledProcessError as e:
            print(f"清除代理时出错: {e.stderr.decode('gbk', errors='ignore')}")
            return

    # 通知其他进程环境变量已更改
    print("正在广播环境变量设置更改...")
    if broadcast_setting_change():
        print("成功通知其他进程。")
        print("更改应在新的命令提示符中生效。某些应用程序可能需要重新启动。")
    else:
        print("警告：未能广播设置更改。可能需要重新启动或重新登录才能使更改完全生效。")

if __name__ == "__main__":
    toggle_proxy()
    input("Press Enter to exit...")