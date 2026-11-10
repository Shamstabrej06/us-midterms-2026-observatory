import ctypes
from ctypes import wintypes
user32 = ctypes.windll.user32

h = user32.OpenDesktopW('exebox-74RZTFYFMOWGO3HCYSNIF7SXYA', 0, False, 0x01FF)
user32.SetThreadDesktop(h)

hwnd = 1048638
print("Inspecting window 1048638 ('Issues were found')...")

children = []
def child_cb(chwnd, _):
    l = user32.GetWindowTextLengthW(chwnd)
    b = ctypes.create_unicode_buffer(l+1)
    user32.GetWindowTextW(chwnd, b, l+1)
    cbuff = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(chwnd, cbuff, 256)
    children.append((chwnd, b.value, cbuff.value))
    return True

user32.EnumChildWindows(hwnd, ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(child_cb), 0)
for chwnd, txt, cls in children:
    print(f"[{cls}] '{txt}'")
