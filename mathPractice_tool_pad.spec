# -*- mode: python ; coding: utf-8 -*-

# 产物名带构建日期（用户要求：年月日后缀，如 mathPractice_tool_pad_20261123.exe）
import datetime
import os
_BUILD_DATE = datetime.date.today().strftime("%Y%m%d")

# 静态题库打进 exe（运行时由 app/__init__.py 自动同步到 exe 旁 data/bank；
# 过滤抽题进度 progress_* 与签名标记等运行文件）
_datas = [('app', 'app'), ('static', 'static')]
_bank_dir = 'data/bank'
if os.path.isdir(_bank_dir):
    for _name in sorted(os.listdir(_bank_dir)):
        if _name.startswith('progress_') or _name == '.bundled_sig':
            continue
        _path = os.path.join(_bank_dir, _name)
        if os.path.isfile(_path) and _name.endswith('.json'):
            _datas.append((_path, 'data/bank'))
    _figs = os.path.join(_bank_dir, 'finale_figs')
    if os.path.isdir(_figs):
        _datas.append((_figs, 'data/bank/finale_figs'))


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=_datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='mathPractice_tool_pad_' + _BUILD_DATE,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    icon='icon.ico',
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
