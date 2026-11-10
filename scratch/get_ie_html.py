import threading
import ctypes
from ctypes import wintypes
import win32gui
import win32con

user32 = ctypes.windll.user32
oleacc = ctypes.windll.oleacc

# IHTMLDocument2 GUID: {332C4425-26CB-11D0-B483-00C04FD90119}
IID_IHTMLDocument2 = ctypes.c_char_p(b"\x25\x44\x2c\x33\xcb\x26\xd0\x11\xb4\x83\x00\xc0\x4f\xd9\x01\x19")

def worker():
    h = user32.OpenDesktopW('exebox-74RZTFYFMOWGO3HCYSNIF7SXYA', 0, False, 0x01FF)
    user32.SetThreadDesktop(h)

    hwnd_ie = 1902616
    msg = user32.RegisterWindowMessageW("WM_HTML_GETOBJECT")
    lres = wintypes.LPARAM()
    user32.SendMessageTimeoutW(hwnd_ie, msg, 0, 0, win32con.SMTO_ABORTIFHUNG, 1000, ctypes.byref(lres))
    print("WM_HTML_GETOBJECT lres:", lres.value)
    if lres.value:
        pDoc = ctypes.c_void_p()
        # ObjectFromLresult(LRESULT, REFIID, WPARAM, void**)
        hr = oleacc.ObjectFromLresult(lres, IID_IHTMLDocument2, 0, ctypes.byref(pDoc))
        print("ObjectFromLresult hr:", hex(hr), "pDoc:", pDoc)

t = threading.Thread(target=worker)
t.start()
t.join()
