import ctypes.wintypes
import os

hWnd = ctypes.windll.user32.GetForegroundWindow()

title_length = ctypes.windll.user32.GetWindowTextLengthW(hWnd)
title = ctypes.create_unicode_buffer(title_length + 1)
ctypes.windll.user32.GetWindowTextW(hWnd, title, title_length + 1)

pid = ctypes.wintypes.DWORD()
ctypes.windll.user32.GetWindowThreadProcessId(hWnd, ctypes.pointer(pid))

hProcess = ctypes.windll.kernel32.OpenProcess(0x0401, False, pid)
executable_path = ctypes.create_unicode_buffer(512)
ctypes.windll.psapi.GetProcessImageFileNameW(hProcess, executable_path, 512)
filename = os.path.basename(executable_path.value.decode("utf-8"))

ctypes.windll.kernel32.CloseHandle(hProcess)

print(title.value, filename)
