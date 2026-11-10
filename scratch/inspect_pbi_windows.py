import ctypes
from ctypes import wintypes
user32 = ctypes.windll.user32

h_def = user32.OpenDesktopW('Default', 0, False, 0x01FF)
results = []
def cb(hwnd, _):
    pid = wintypes.DWORD()
    user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    if pid.value == 20152:
        l = user32.GetWindowTextLengthW(hwnd)
        b = ctypes.create_unicode_buffer(l+1)
        user32.GetWindowTextW(hwnd, b, l+1)
        cbuff = ctypes.create_unicode_buffer(256)
        user32.GetClassNameW(hwnd, cbuff, 256)
        results.append((hwnd, b.value, cbuff.value))
    return True

user32.EnumDesktopWindows(h_def, ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(cb), 0)
print(f"Total windows for PID 20152: {len(results)}")
for r in results:
    print(r)

# For each window, check children
def child_cb(chwnd, _):
    l = user32.GetWindowTextLengthW(chwnd)
    b = ctypes.create_unicode_buffer(l+1)
    user32.GetWindowTextW(chwnd, b, l+1)
    cbuff = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(chwnd, cbuff, 256)
    if b.value.strip():
        print("   Child:", b.value, "|", cbuff.value)
    return True

for hwnd, title, cls in results:
    user32.EnumChildWindows(hwnd, ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(child_cb), 0)
