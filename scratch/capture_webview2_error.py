import ctypes
from ctypes import wintypes
import win32gui
import win32ui
from PIL import Image

user32 = ctypes.windll.user32

h = user32.OpenDesktopW('Default', 0, False, 0x01FF)
user32.SetThreadDesktop(h)

hwnd = 854198
rect = win32gui.GetWindowRect(hwnd)
w = rect[2] - rect[0]
h_win = rect[3] - rect[1]

hwndDC = win32gui.GetWindowDC(hwnd)
mfcDC = win32ui.CreateDCFromHandle(hwndDC)
saveDC = mfcDC.CreateCompatibleDC()

saveBitMap = win32ui.CreateBitmap()
saveBitMap.CreateCompatibleBitmap(mfcDC, w, h_win)
saveDC.SelectObject(saveBitMap)

user32.PrintWindow(hwnd, saveDC.GetSafeHdc(), 2)

bmpinfo = saveBitMap.GetInfo()
bmpstr = saveBitMap.GetBitmapBits(True)

im = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)
im.save(r"C:\Users\shams\us-midterms-2026-observatory\scratch\webview2_error.png")
print("Saved scratch/webview2_error.png successfully!")

win32gui.DeleteObject(saveBitMap.GetHandle())
saveDC.DeleteDC()
mfcDC.DeleteDC()
win32gui.ReleaseDC(hwnd, hwndDC)
