import winreg as winreg

INTERNET_SETTINGS = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                   r'Software\\Microsoft\\Windows\\CurrentVersion\\Internet Settings',
                                   0, winreg.KEY_ALL_ACCESS)


def enable_proxy():
    _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, 'ProxyEnable')
    winreg.SetValueEx(INTERNET_SETTINGS, 'ProxyEnable', 0, reg_type, 1)
    _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, 'ProxyServer')
    winreg.SetValueEx(INTERNET_SETTINGS, 'ProxyServer', 0, reg_type, '127.0.0.3:11100')

def disable_proxy():
    _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, 'ProxyEnable')
    winreg.SetValueEx(INTERNET_SETTINGS, 'ProxyEnable', 0, reg_type, 0)
    _, reg_type = winreg.QueryValueEx(INTERNET_SETTINGS, 'ProxyServer')
    winreg.SetValueEx(INTERNET_SETTINGS, 'ProxyServer', 0, reg_type, '')

