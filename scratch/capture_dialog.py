import threading
import ctypes
from ctypes import wintypes
import win32gui
import win32ui
import win32con
from PIL import Image

user32 = ctypes.windll.user32

def worker():
    h = user32.OpenDesktopW('exebox-74RZTFYFMOWGO3HCYSNIF7SXYA', 0, False, 0x01FF)
    user32.SetThreadDesktop(h)

    hwnd = 1048638
    rect = win32gui.GetWindowRect(hwnd)
    w = rect[2] - rect[0]
    h_win = rect[3] - rect[1]
    print(f"Dialog rect: {rect}, size: {w}x{h_win}")

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()

    saveBitMap = win32ui.CreateBitmap()
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h_win)
    saveDC.SelectObject(saveBitMap)

    # PW_RENDERFULLCONTENT = 2
    res = user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)
    print("PrintWindow result:", res)

    bmpinfo = saveBitMap.GetInfo()
    bmpstr = saveBitMap.GetBitmapBits(True)

    im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
    im.save(r"C:\Users\shams\us-midterms-2026-observatory\scratch\issues_dialog.png")
    print("Saved scratch/issues_dialog.png successfully!")

    win32gui.DeleteObject(saveBitMap.GetHandle())
    saveDC.DeleteDC()
    mfcDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, hwndDC)

t = threading.Thread(target=worker)
t.start()
t.join()
