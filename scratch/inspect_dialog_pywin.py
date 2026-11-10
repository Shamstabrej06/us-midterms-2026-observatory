import threading
import ctypes
from ctypes import wintypes
import win32gui
import win32con

user32 = ctypes.windll.user32

def worker():
    h = user32.OpenDesktopW('exebox-74RZTFYFMOWGO3HCYSNIF7SXYA', 0, False, 0x01FF)
    user32.SetThreadDesktop(h)

    # Find the dialog
    hwnd = win32gui.FindWindow(None, "Issues were found")
    print("Found dialog HWND:", hwnd)
    if not hwnd:
        return

    # Enumerate all child windows
    def enum_child(chwnd, lparam):
        cls = win32gui.GetClassName(chwnd)
        txt = win32gui.GetWindowText(chwnd)
        rect = win32gui.GetWindowRect(chwnd)
        print(f"Child {chwnd}: Class='{cls}', Text='{txt}', Rect={rect}")
        return True

    win32gui.EnumChildWindows(hwnd, enum_child, None)

t = threading.Thread(target=worker)
t.start()
t.join()
