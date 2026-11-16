#!/usr/bin/env python3
"""Host runner for the Aureate envelope exporter. Two subcommands.

  export   Windows only. Launches UnrealEditor-Cmd (NullRHI) once to dump ONE review map
           into a NEW snapshot JSON. Gates: RAM >= 4.2 GiB, disk >= 14 GiB, no other
           Unreal commandlet, no overwrite of snapshot or receipt, watchdog on RAM/time.
  combine  Any OS. Turns two snapshots (from-form, to-form) into a verifier config via
           aureate_envelope_records.build_config, then runs the swept-clearance verifier.

SOURCE-SIDE SCREEN ONLY. Nothing here approves a transition, a clearance, art or canon.
Exit code 0 only when the verifier verdict is CLEAR_UNDER_ENVELOPES.
"""
import argparse
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import aureate_envelope_records as records  # noqa: E402

ROOT = Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
PROJECT = ROOT / "AureateCinematicV4Sandbox" / "AureateCinematicV4Sandbox.uproject"
UE = Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
SCRIPT = HERE / "export_aureate_envelopes_native.py"
MAX_SECONDS = 160
MIN_RAM_GIB = 4.2
MIN_DISK_GIB = 14


def _load_verifier():
    path = HERE.parent / "ArtSource" / "ShipReview" / "aureate_swept_clearance.py"
    spec = importlib.util.spec_from_file_location("aureate_swept_clearance", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _free_ram_gib():
    import ctypes

    class Mem(ctypes.Structure):
        _fields_ = [("size", ctypes.c_ulong), ("load", ctypes.c_ulong),
                    ("total", ctypes.c_ulonglong), ("avail", ctypes.c_ulonglong),
                    ("totalpage", ctypes.c_ulonglong), ("availpage", ctypes.c_ulonglong),
                    ("totalvirtual", ctypes.c_ulonglong), ("availvirtual", ctypes.c_ulonglong),
                    ("avail_ext", ctypes.c_ulonglong)]
    m = Mem()
    m.size = ctypes.sizeof(m)
    if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
        raise RuntimeError("Windows available-RAM query failed")
    return m.avail / 1024 ** 3


def _write_new(path, text):
    path = Path(path)
    if path.exists():
        raise RuntimeError(f"Refusing to overwrite {path}")
    with open(path, "x", encoding="utf8") as handle:
        handle.write(text)


def cmd_export(args):
    import shutil
    if sys.platform != "win32":
        raise RuntimeError("Native UE export runs on Windows only")
    if not (UE.is_file() and SCRIPT.is_file() and PROJECT.is_file()):
        raise RuntimeError("Missing UE, exporter script or V4 sandbox project")
    data = json.loads(PROJECT.read_text(encoding="utf8"))
    if data.get("EngineAssociation") != "5.8" or \
            "AUREATE_CINEMATIC_V4_REVIEW_ONLY" not in data.get("Description", ""):
        raise RuntimeError("Not a review-only UE5.8 sandbox")
    out = Path(args.out)
    receipt = out.with_suffix(".receipt.json")
    log = out.with_suffix(".log")
    for p in (out, receipt, log):
        if p.exists():
            raise RuntimeError(f"Refusing to overwrite {p}")
    if _free_ram_gib() < MIN_RAM_GIB:
        raise RuntimeError("RAM gate below 4.2 GiB: do not launch")
    if shutil.disk_usage(ROOT).free < MIN_DISK_GIB * 1024 ** 3:
        raise RuntimeError("Disk gate below 14 GiB: do not launch")
    tasks = subprocess.run(["tasklist", "/FI", "IMAGENAME eq UnrealEditor-Cmd.exe", "/FO", "CSV"],
                           capture_output=True, text=True, check=True).stdout
    if '"UnrealEditor-Cmd.exe"' in tasks:
        raise RuntimeError("Another UE commandlet exists: refuse concurrency")
    env = dict(os.environ, TSTSS_ENVELOPE_MAP=args.map, TSTSS_ENVELOPE_FORM=args.form,
               TSTSS_ENVELOPE_OUT=str(out))
    cmd = [str(UE), str(PROJECT), "-ExecutePythonScript=" + str(SCRIPT),
           "-NullRHI", "-NoSplash", "-NoSound", "-Unattended", "-nop4",
           "-stdout", "-FullStdOutLogOutput"]
    report = {"state": "NOT_STARTED", "read_only": True, "map": args.map, "form": args.form,
              "ram_gib_start": round(_free_ram_gib(), 2), "max_seconds": MAX_SECONDS}
    code = None
    try:
        with open(log, "x", encoding="utf8") as output:
            proc = subprocess.Popen(cmd, stdout=output, stderr=subprocess.STDOUT,
                                    stdin=subprocess.DEVNULL, cwd=str(ROOT), env=env,
                                    creationflags=subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            t0 = time.monotonic()
            while proc.poll() is None:
                if _free_ram_gib() < 0.95 or time.monotonic() - t0 > MAX_SECONDS:
                    report["state"] = "STOPPED_BY_RAM_OR_TIME_WATCHDOG"
                    proc.terminate()
                    break
                time.sleep(2)
            try:
                code = proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                proc.kill()
                code = proc.wait(timeout=5)
        if report["state"] == "NOT_STARTED":
            ok = code == 0 and out.is_file()
            report["state"] = "EXPORT_PASS_UNVERIFIED" if ok else "EXPORT_HOLD"
    finally:
        report["exit_code"] = code
        _write_new(receipt, json.dumps(report, sort_keys=True, indent=2) + "\n")
    print(report["state"], out)
    return 0 if report["state"] == "EXPORT_PASS_UNVERIFIED" else 1


def cmd_combine(args):
    sc = _load_verifier()
    out = Path(args.out)
    if out.exists():
        raise RuntimeError(f"Refusing to overwrite {out}")
    try:
        snaps = [json.loads(Path(p).read_text(encoding="utf8")) for p in (args.from_snapshot, args.to_snapshot)]
        cfg = records.build_config(snaps[0], snaps[1], required_clearance=args.clearance)
    except (OSError, ValueError) as exc:  # json errors and EnvelopeError are ValueError
        print("FAIL_CLOSED_INVALID_INPUT", exc)
        return 1
    result = sc.verify(cfg)
    _write_new(out, json.dumps({"config": cfg, "result": result}, sort_keys=True, indent=2) + "\n")
    print(result["verdict"], out)
    return 0 if result["verdict"] == sc.V_CLEAR else 1


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    e = sub.add_parser("export")
    e.add_argument("--map", required=True, help="/Game/TSTSS/Review/... map path")
    e.add_argument("--form", required=True, help="display form name, e.g. Skybourne")
    e.add_argument("--out", required=True, help="NEW snapshot .json path")
    c = sub.add_parser("combine")
    c.add_argument("--from-snapshot", required=True)
    c.add_argument("--to-snapshot", required=True)
    c.add_argument("--clearance", type=float, default=0.0, help="required clearance in cm")
    c.add_argument("--out", required=True, help="NEW combined result .json path")
    args = parser.parse_args(argv)
    try:
        return cmd_export(args) if args.command == "export" else cmd_combine(args)
    except RuntimeError as exc:
        print("REFUSED", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
