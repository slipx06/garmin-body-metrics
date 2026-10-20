# PyInstaller build for the Windows app (folder mode, no console window).
# Build from the repo root:  pyinstaller packaging/body_metrics.spec
from PyInstaller.utils.hooks import collect_all

ROOT = SPECPATH + "/.."

datas, binaries, hiddenimports = [], [], []
# curl_cffi ships compiled code, ua_generator and tzdata ship data files,
# and garminconnect imports some modules lazily; bundle all of them whole.
for pkg in ("curl_cffi", "ua_generator", "tzdata", "garminconnect"):
    d, b, h = collect_all(pkg)
    datas += d
    binaries += b
    hiddenimports += h

a = Analysis(
    [ROOT + "/app.py"],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    exclude_binaries=True,
    name="Body Metrics",
    icon=ROOT + "/icon.ico",
    console=False,
    upx=False,
)
coll = COLLECT(exe, a.binaries, a.datas, name="Body Metrics", upx=False)
