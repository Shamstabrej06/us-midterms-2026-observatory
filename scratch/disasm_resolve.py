import clr
clr.AddReference(r"C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll")
import System
from System.Reflection import BindingFlags
from System.Reflection.Emit import OpCodes

asm = System.Reflection.Assembly.LoadFrom(r"C:\Program Files\WindowsApps\Microsoft.MicrosoftPowerBIDesktop_2.159.1231.0_x64__8wekyb3d8bbwe\bin\Microsoft.PowerBI.Packaging.dll")
t = asm.GetType("Microsoft.PowerBI.Packaging.Project.PBIProjectShredder+<ResolveReportExplorationAsync>d__6")
m = t.GetMethod("MoveNext", BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Instance)
body = m.GetMethodBody()
il = list(body.GetILAsByteArray())
module = m.Module

print(f"Total IL bytes in MoveNext: {len(il)}")
# Let's inspect all strings and method calls
i = 0
while i < len(il):
    op = il[i]
    if op == 0x72: # ldstr
        token = int.from_bytes(bytes(il[i+1:i+5]), "little", signed=True)
        try:
            s = module.ResolveString(token)
            print(f"[{i}] ldstr: {repr(s)}")
        except Exception:
            pass
        i += 5
    elif op in (0x28, 0x6F): # call / callvirt
        token = int.from_bytes(bytes(il[i+1:i+5]), "little", signed=True)
        try:
            target = module.ResolveMethod(token)
            print(f"[{i}] call: {target.DeclaringType.Name}::{target.Name}")
        except Exception:
            pass
        i += 5
    else:
        i += 1
