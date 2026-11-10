import threading
import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

def worker():
    h = user32.OpenDesktopW('exebox-74RZTFYFMOWGO3HCYSNIF7SXYA', 0, False, 0x01FF)
    res = user32.SetThreadDesktop(h)
    err = kernel32.GetLastError()
    print("New thread SetThreadDesktop result:", res, "LastError:", err)
    if res:
        # Enumerate desktop windows
        results = []
        def wcb(hwnd, _):
            l = user32.GetWindowTextLengthW(hwnd)
            b = ctypes.create_unicode_buffer(l+1)
            user32.GetWindowTextW(hwnd, b, l+1)
            results.append((hwnd, b.value))
            return True
        user32.EnumDesktopWindows(h, ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(wcb), 0)
        print("Windows on desktop from worker thread:", len(results))
        for r in results:
            if "Issues" in r[1]:
                print("Found Issues dialog window:", r)
                # Let's inspect its child controls using WM_GETTEXT or UIAutomation
                # Send WM_COMMAND or click 'Copy details' or 'Close'
                pass

t = threading.Thread(target=worker)
t.start()
t.join()
