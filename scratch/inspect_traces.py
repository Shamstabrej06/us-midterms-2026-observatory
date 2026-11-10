import ctypes
from ctypes import wintypes
user32 = ctypes.windll.user32
oleacc = ctypes.windll.oleacc

h = user32.OpenDesktopW('exebox-74RZTFYFMOWGO3HCYSNIF7SXYA', 0, False, 0x01FF)
user32.SetThreadDesktop(h)

# Let's find all text using WM_GETTEXT or child windows
hwnd = 1048638
def enum_cb(h, _):
    length = user32.GetWindowTextLengthW(h)
    buff = ctypes.create_unicode_buffer(length + 1)
    user32.GetWindowTextW(h, buff, length + 1)
    cbuff = ctypes.create_unicode_buffer(256)
    user32.GetClassNameW(h, cbuff, 256)
    print(f"HWND: {h}, Class: {cbuff.value}, Text: '{buff.value}'")
    return True

user32.EnumChildWindows(hwnd, ctypes.WINFUNCTYPE(ctypes.c_bool, wintypes.HWND, wintypes.LPARAM)(enum_cb), 0)

# Check Desktop log files! Power BI Desktop writes detailed diagnostic traces!
import glob, os
pbi_traces = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Power BI Desktop\Traces")
print("\nChecking traces in:", pbi_traces)
if os.path.exists(pbi_traces):
    files = sorted(glob.glob(os.path.join(pbi_traces, "*.*")), key=os.path.getmtime, reverse=True)
    for f in files[:5]:
        print(" Trace file:", f, "Size:", os.path.getsize(f))
