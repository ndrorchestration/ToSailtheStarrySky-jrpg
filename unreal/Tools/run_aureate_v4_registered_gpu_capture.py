#!/usr/bin/env python3
"""Run one *registered* UE Editor.Python V4 Skybourne capture in a review sandbox.

Source-only until executed on the authorized Windows UE 5.8.4 host. Never use
this runner against production content; process exit zero is not render proof.
"""
import argparse
import ctypes
import hashlib
import json
import re
import shutil
import struct
import subprocess
import sys
import time
from pathlib import Path
from verify_aureate_v4_png_pixels import inspect_png_pixels

ROOT = Path('C:/tmp/TSTSS_AureateCinematicV4_Native_20261103')
SANDBOX = ROOT / 'AureateCinematicV4Sandbox'
ORIGINAL = SANDBOX / 'AureateCinematicV4Sandbox.uproject'
UE_ROOT = Path('C:/Program Files/Epic Games/UE_5.8')
EDITOR = UE_ROOT / 'Engine/Binaries/Win64/UnrealEditor-Cmd.exe'
TEST_PLUGIN = UE_ROOT / 'Engine/Plugins/Tests/PythonAutomationTest/PythonAutomationTest.uplugin'
SOURCE = Path(__file__).with_name('capture_aureate_v4_skybourne_native_gpu.py')
MAP_FILE = SANDBOX / 'Content/TSTSS/Review/Scenes/AureateCinematicV4_Skybourne_Hero_20261103_FullEditor.umap'
MAP_SHA = '16bb93fb9bdd2a4e1559864df908122094fe8a641b4a1481f2935d64ba184c40'
MAX_SECONDS = 180

class Mem(ctypes.Structure):
    _fields_ = [('size', ctypes.c_ulong), ('load', ctypes.c_ulong),
                ('total', ctypes.c_ulonglong), ('avail', ctypes.c_ulonglong),
                ('totalpage', ctypes.c_ulonglong), ('availpage', ctypes.c_ulonglong),
                ('totalvirtual', ctypes.c_ulonglong), ('availvirtual', ctypes.c_ulonglong),
                ('avail_ext', ctypes.c_ulonglong)]

def free_ram():
    status = Mem()
    status.size = ctypes.sizeof(status)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
        raise RuntimeError('Unable to read Windows physical RAM')
    return status.avail / (1024 ** 3)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate_native(report, native_receipt, image, expected_test, expected_report_sha):
    """Strict evidence admission, engine-free; never approves image appearance."""
    if not isinstance(report, dict) or not isinstance(native_receipt, dict):
        raise ValueError('Missing native automation report or capture receipt')
    if report.get('failed') != 0 or report.get('notRun') != 0:
        raise ValueError('Automation run failed or skipped tests')
    tests = report.get('tests')
    if not isinstance(tests, list):
        raise ValueError('No per-test native automation report')
    matches = [t for t in tests if t.get('fullTestPath') == expected_test]
    if len(matches) != 1 or matches[0].get('state') != 'Success':
        raise ValueError('Exact registered Editor.Python test not proven successful')
    if report.get('succeeded', 0) < 1:
        raise ValueError('No reported successful native tests')
    if native_receipt.get('state') != 'NATIVE_D3D11_CAPTURE_ONE_FRAME_TASK_PASS_PIXEL_QA_PENDING':
        raise ValueError('Native screenshot task has no completed receipt')
    if not native_receipt.get('native_task_complete'):
        raise ValueError('Native task completion absent')
    if (native_receipt.get('source_map_sha_before') != MAP_SHA or
            native_receipt.get('source_map_sha_after') != MAP_SHA or expected_report_sha != MAP_SHA):
        raise ValueError('Source review map changed')
    if not image.is_file():
        raise ValueError('Native screenshot PNG missing')
    raw = image.read_bytes()
    if len(raw) < 4096 or raw[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('PNG absent or corrupt header')
    width, height = struct.unpack_from('>II', raw, 16)
    if (width, height) != (1280, 720):
        raise ValueError('Wrong native screenshot dimensions')
    image_hash = hashlib.sha256(raw).hexdigest()
    if image_hash != native_receipt.get('png_sha256') or len(raw) != native_receipt.get('png_bytes'):
        raise ValueError('PNG bytes/hash differ from native receipt')
    pixels = inspect_png_pixels(raw)
    return {'png_sha256': image_hash, 'png_bytes': len(raw), 'pixel_integrity': pixels,
            'dimensions': [width, height], 'registered_test_path': expected_test}

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--attempt', required=True, help='Unused, unique identifier')
    args = parser.parse_args(argv)
    attempt = args.attempt
    if not re.fullmatch(r'[a-z][a-z0-9_]{2,18}', attempt):
        raise ValueError('Attempt must be 3-19 lowercase ASCII alphanumeric/underscore characters')
    if sys.platform != 'win32':
        raise RuntimeError('Registered native GPU capture is Windows-only')
    if not all(p.is_file() for p in (ORIGINAL, EDITOR, SOURCE, MAP_FILE, TEST_PLUGIN)):
        raise RuntimeError('UE5.8 capture sandbox, source, map or bundled plugin missing')
    project = json.loads(ORIGINAL.read_text(encoding='utf-8'))
    if (project.get('EngineAssociation') != '5.8' or
            'AUREATE_CINEMATIC_V4_REVIEW_ONLY' not in project.get('Description', '')):
        raise RuntimeError('Refusing non-review project')
    if sha(MAP_FILE) != MAP_SHA:
        raise RuntimeError('Refusing changed Skybourne native review map')
    if free_ram() < 6.5 or shutil.disk_usage(ROOT).free < 14 * (1024 ** 3):
        raise RuntimeError('Native GPU memory/disk safety gate rejected launch')
    existing = subprocess.run(['tasklist', '/FO', 'CSV'],
                              capture_output=True, text=True, check=True).stdout
    if any(('"' + n + '"') in existing for n in ('UnrealEditor.exe', 'UnrealEditor-Cmd.exe')):
        raise RuntimeError('An Unreal Editor is already active; refusing contention')

    name = 'AureateV4Gpu_' + attempt
    test_name = 'test_aureate_v4_skybourne_' + attempt
    test_path = 'Editor.Python.' + name + '.' + test_name
    temporary_project = SANDBOX / (name + '.uproject')
    python_dir = SANDBOX / 'Content/Python'
    temporary_test = python_dir / (test_name + '.py')
    output = ROOT / ('SkybourneV4NativeGPU_20261103_' + attempt)
    png = output / 'Skybourne_V4_UE584_D3D11_ThreeQuarter_REVIEW.png'
    receipt = output / 'native_skybourne_gpu_capture_receipt.json'
    log = ROOT / ('ue584_v4_registered_gpu_' + attempt + '.log')
    host_file = ROOT / ('host_v4_registered_gpu_' + attempt + '.json')
    report_dir = ROOT / ('report_v4_registered_gpu_' + attempt)
    if any(p.exists() for p in (temporary_project, temporary_test, output,
                                log, host_file, report_dir)):
        raise FileExistsError('Attempt evidence or staging path already occupied; no overwrite')

    plugins = project.setdefault('Plugins', [])
    if not isinstance(plugins, list):
        raise RuntimeError('Unexpected project Plugins schema')
    for plugin_name in ('PythonScriptPlugin', 'PythonAutomationTest'):
        plugin = next((p for p in plugins if p.get('Name') == plugin_name), None)
        if plugin is None:
            plugins.append({'Name': plugin_name, 'Enabled': True})
        else:
            plugin['Enabled'] = True
    staged_project = (json.dumps(project, indent=2) + '\n').encode('utf-8')
    staged_test = SOURCE.read_bytes()
    report = {'state': 'NOT_LAUNCHED', 'attempt': attempt, 'test_path': test_path,
              'source_map_sha_expected': MAP_SHA, 'player_unlock_changed': False,
              'canonical_art_approved': False, 'user_editor_untouched': True}
    proc = None
    try:
        # Temporary *sibling* descriptor enables only the bundled test plugin.
        # Original review .uproject and all pre-existing maps stay byte-identical.
        python_dir.mkdir(parents=True, exist_ok=True)
        with temporary_project.open('xb') as fd:
            fd.write(staged_project)
        with temporary_test.open('xb') as fd:
            fd.write(staged_test)
        cmd = [str(EDITOR), str(temporary_project), '-d3d11', '-NoSplash',
               '-NoSound', '-Unattended', '-nop4', '-stdout', '-FullStdOutLogOutput',
               '-ExecCmds=Automation RunTests ' + test_path + '; Quit',
               '-ReportExportPath=' + str(report_dir)]
        with log.open('x', encoding='utf-8') as out:
            proc = subprocess.Popen(cmd, stdout=out, stderr=subprocess.STDOUT,
                                    stdin=subprocess.DEVNULL, cwd=str(ROOT),
                                    creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS,
                                    env={**__import__('os').environ,
                                         'TSTSS_V4_CAPTURE_ATTEMPT': attempt})
            report['pid'] = proc.pid
            start = time.monotonic()
            while proc.poll() is None:
                if time.monotonic() - start > MAX_SECONDS:
                    report['state'] = 'STOPPED_BY_TIME_WATCHDOG'
                    proc.terminate()
                    break
                if free_ram() < 1.5:
                    report['state'] = 'STOPPED_BY_RAM_WATCHDOG'
                    proc.terminate()
                    break
                time.sleep(2)
            try:
                report['exit_code'] = proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                report['exit_code'] = proc.wait(timeout=5)
        if report['state'] == 'NOT_LAUNCHED':
            if report['exit_code'] != 0:
                raise RuntimeError('Unreal Editor automation process failed')
            native = json.loads(receipt.read_text(encoding='utf-8'))
            framework = json.loads((report_dir / 'index.json').read_text(encoding='utf-8'))
            report.update(validate_native(framework, native, png, test_path, sha(MAP_FILE)))
            report['state'] = 'NATIVE_REGISTERED_TEST_AND_PNG_PIXEL_INTEGRITY_PASS_VISUAL_REVIEW_PENDING'
    except Exception as exc:
        report['error'] = str(exc)
        if report['state'] == 'NOT_LAUNCHED':
            report['state'] = 'NATIVE_CAPTURE_NOT_VERIFIED'
    finally:
        for path, content in ((temporary_test, staged_test),
                              (temporary_project, staged_project)):
            if path.exists() and path.read_bytes() == content:
                path.unlink()
            elif path.exists():
                report['state'] = 'STAGING_MODIFIED_MANUAL_REVIEW_REQUIRED'
        report['source_map_sha_postflight'] = sha(MAP_FILE)
        if report['source_map_sha_postflight'] != MAP_SHA:
            report['state'] = 'SOURCE_MAP_CHANGED_REJECTED'
        report['ram_gib_postflight'] = round(free_ram(), 2)
        host_file.write_text(json.dumps(report, sort_keys=True, indent=2) + '\n', encoding='utf-8')
        print('AUREATE_V4_REGISTERED_GPU_RESULT', json.dumps(report, sort_keys=True), flush=True)
    if report['state'] != 'NATIVE_REGISTERED_TEST_AND_PNG_PIXEL_INTEGRITY_PASS_VISUAL_REVIEW_PENDING':
        raise SystemExit(1)

if __name__ == '__main__':
    main()
