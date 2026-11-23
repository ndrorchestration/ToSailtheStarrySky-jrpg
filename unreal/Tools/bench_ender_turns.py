"""Guarded Ender movement A/B capture: idle/walk/stop/run/stop/90/180/stop.

Keyboard and rendered-media evidence on Windows: NOT human testing.
Requires matching exact source checkout and a separately guarded Unreal game host.
Captures ONLY a foreground, exact-PID UnrealWindow; releases all owned keys.
Optional FFmpeg records only the named Unreal game window, never entire desktop.
No editor/project/source/asset writes.
"""
import argparse
import ctypes
from ctypes import wintypes
from datetime import datetime, timezone
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from PIL import ImageGrab

ROOT = Path(__file__).resolve().parents[2]
EVIDENCE = ROOT / "unreal" / "Saved" / "MigrationEvidence"
U = ctypes.windll.user32
U.GetForegroundWindow.restype = wintypes.HWND
U.GetWindowThreadProcessId.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.DWORD))
U.GetClassNameW.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
U.GetWindowTextW.argtypes = (wintypes.HWND, wintypes.LPWSTR, ctypes.c_int)
U.GetWindowRect.argtypes = (wintypes.HWND, ctypes.POINTER(wintypes.RECT))
U.keybd_event.argtypes = (ctypes.c_ubyte, ctypes.c_ubyte, wintypes.DWORD, ctypes.c_size_t)
U.PostMessageW.argtypes = (wintypes.HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
VK = {"W": (0x57, 0x11), "S": (0x53, 0x1F), "A": (0x41, 0x1E),
      "D": (0x44, 0x20), "Shift": (0xA0, 0x2A)}


def need(value, label):
    if not value:
        raise RuntimeError("HOLD_ENDER_PIVOT_" + label)


def utc():
    return datetime.now(timezone.utc).isoformat()


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def window_info(hwnd):
    pid = wintypes.DWORD()
    U.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
    klass = ctypes.create_unicode_buffer(100)
    title = ctypes.create_unicode_buffer(256)
    U.GetClassNameW(hwnd, klass, 100)
    U.GetWindowTextW(hwnd, title, 256)
    return int(pid.value), klass.value, title.value


def owned_foreground(pid):
    hwnd = U.GetForegroundWindow()
    actual, klass, title = window_info(hwnd)
    need(actual == pid and klass == "UnrealWindow" and
         "ToSailTheStarrySky" in title, "FOREGROUND_GAME")
    return hwnd, title


def snapshot(pid, out, label):
    hwnd, _ = owned_foreground(pid)
    rectangle = wintypes.RECT()
    need(U.GetWindowRect(hwnd, ctypes.byref(rectangle)), "RECT")
    need(rectangle.right - rectangle.left >= 640 and
         rectangle.bottom - rectangle.top >= 480, "WINDOW_SIZE")
    image = out / (label + ".png")
    need(not image.exists(), "SCREENSHOT_ALREADY_EXISTS")
    frame = ImageGrab.grab(bbox=(rectangle.left, rectangle.top,
                                  rectangle.right, rectangle.bottom),
                           all_screens=True)
    need(owned_foreground(pid)[0] == hwnd, "FOREGROUND_CHANGED_DURING_SCREENSHOT")
    frame.save(image)
    return {"label": label, "utc": utc(), "image": image.name,
            "pixel_width": frame.width, "pixel_height": frame.height}


def close_owned(pid):
    windows = []
    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def each(hwnd, unused):
        actual, klass, title = window_info(hwnd)
        if actual == pid and klass == "UnrealWindow" and "ToSailTheStarrySky" in title:
            windows.append(hwnd)
        return True
    U.EnumWindows(each, 0)
    need(len(windows) == 1, "OWNED_WINDOW_COUNT")
    need(U.PostMessageW(windows[0], 0x0010, 0, 0), "CLOSE_OWNED_WINDOW")


def key(name, down):
    vk, scan = VK[name]
    U.keybd_event(vk, scan, 0 if down else 2, 0)


def guarded_hold(pid, seconds):
    target = time.monotonic() + seconds
    while time.monotonic() < target:
        owned_foreground(pid)
        time.sleep(.05)


def make_video(pid, output, stderr):
    """Capture only the foreground owned game rectangle from desktop compositor.

    Window GDI frame capture returns stale Direct3D surfaces on this machine.
    Never capture a whole display: require an onscreen exact-PID game window.
    """
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        return None
    hwnd, title = owned_foreground(pid)
    need(title and "\n" not in title and "\r" not in title, "WINDOW_TITLE")
    rectangle = wintypes.RECT()
    need(U.GetWindowRect(hwnd, ctypes.byref(rectangle)), "CAPTURE_RECT")
    width = rectangle.right - rectangle.left
    height = rectangle.bottom - rectangle.top
    screen_width = U.GetSystemMetrics(0)
    screen_height = U.GetSystemMetrics(1)
    need(640 <= width <= screen_width and 480 <= height <= screen_height,
         "CAPTURE_SIZE")
    need(0 <= rectangle.left < rectangle.right <= screen_width
         and 0 <= rectangle.top < rectangle.bottom <= screen_height,
         "CAPTURE_NOT_ENTIRELY_ON_PRIMARY_SCREEN")
    return subprocess.Popen([
        ffmpeg, "-hide_banner", "-loglevel", "error", "-n",
        "-f", "gdigrab", "-draw_mouse", "0", "-framerate", "18",
        "-offset_x", str(rectangle.left), "-offset_y", str(rectangle.top),
        "-video_size", str(width) + "x" + str(height),
        "-i", "desktop", "-c:v", "libx264", "-preset", "veryfast",
        "-crf", "29", "-pix_fmt", "yuv420p", str(output)],
        stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=stderr,
        creationflags=subprocess.CREATE_NO_WINDOW)


def validate_video(path):
    """Reject stale-frame captures. Frame count alone is insufficient."""
    if not path.is_file() or not shutil.which("ffprobe") or not shutil.which("ffmpeg"):
        return False, {"status": "HOLD_VIDEO_OR_TOOLS_MISSING"}
    meta = subprocess.run([
        "ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
        "-show_entries", "stream=nb_read_frames,duration,width,height,r_frame_rate",
        "-of", "json", str(path)], check=True, text=True,
        capture_output=True, timeout=12)
    streams = json.loads(meta.stdout)["streams"]
    need(len(streams) == 1, "UNEXPECTED_VIDEO_STREAMS")
    stream = streams[0]
    frames = int(stream["nb_read_frames"])
    duration = float(stream["duration"])
    hashes_process = subprocess.run([
        "ffmpeg", "-v", "error", "-i", str(path), "-f", "framemd5", "-"],
        check=True, text=True, capture_output=True, timeout=18)
    hashes = [line.split(",")[-1].strip() for line in
              hashes_process.stdout.splitlines()
              if line and not line.startswith("#") and "," in line]
    unique = len(set(hashes))
    eligible = (frames >= 140 and len(hashes) == frames and
                unique >= 70 and duration >= 8.5 and
                stream["width"] >= 640 and stream["height"] >= 480)
    return eligible, {"status": "DYNAMIC_REGION_VIDEO_PASS" if eligible
                       else "HOLD_STALE_OR_TOO_SHORT_VIDEO",
                       "frames": frames, "unique_frame_md5": unique,
                       "duration_seconds": round(duration, 3),
                       "width": int(stream["width"]),
                       "height": int(stream["height"])}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--variant", choices=["blend", "legacy"], required=True)
    args = parser.parse_args()
    out = Path(args.evidence).resolve()
    need(out.parent == EVIDENCE.resolve(), "EVIDENCE_LOCATION")
    need(out.is_dir(), "EVIDENCE_FOLDER")
    need(re.fullmatch(r"[0-9a-f]{40}", args.head) is not None, "HEAD_FORMAT")
    need(git("rev-parse", "HEAD") == args.head and not git("status", "--porcelain"),
         "SOURCE")
    need(not any((out / x).exists() for x in (
        "host.json", "game.log", "game-start.json", "verdict.json",
        "controller.log", "movement.mp4")), "FRESH_EVIDENCE")
    host = None
    video = None
    pid = None
    held = []
    events = []
    errors = []
    vidfile = out / "movement.mp4"
    stderrfile = (out / "video-encoder.log").open("w", encoding="utf8")
    coordinator = (out / "controller.log").open("w", encoding="utf8")
    try:
        host = subprocess.Popen(["powershell.exe", "-NoProfile",
                "-ExecutionPolicy", "Bypass", "-File", str(out / "run_guard.ps1")],
                cwd=str(ROOT), stdout=coordinator, stderr=subprocess.STDOUT)
        limit = time.monotonic() + 48
        while not (out / "game-start.json").exists() and time.monotonic() < limit:
            need(host.poll() is None, "HOST_EARLY_EXIT")
            time.sleep(.15)
        need((out / "game-start.json").exists(), "GAME_START_TIMEOUT")
        started = json.loads((out / "game-start.json").read_text(encoding="utf-8-sig"))
        need(started.get("head") == args.head, "GAME_HEAD")
        pid = int(started["pid"])
        start = datetime.fromisoformat(started["started_utc"].replace("Z", "+00:00")).timestamp()
        while time.time() < start + 23:
            need(host.poll() is None, "GAME_EARLY_EXIT")
            time.sleep(.1)
        owned_foreground(pid)
        video = make_video(pid, vidfile, stderrfile)
        events.append(snapshot(pid, out, "00_idle"))

        def transition(label, wanted, duration, image=None):
            desired = list(wanted)
            for code in reversed(held[:]):
                if code not in desired:
                    key(code, False)
                    held.remove(code)
            for code in desired:
                if code not in held:
                    key(code, True)
                    held.append(code)
            events.append({"label": label, "utc": utc(), "keys": desired})
            guarded_hold(pid, duration)
            if image:
                events.append(snapshot(pid, out, image))

        transition("walk_start", ["W"], 1.5, "01_walk")
        transition("walk_stop", [], 1.0, "02_stop")
        transition("sprint_start", ["W", "Shift"], 1.55, "03_sprint")
        transition("sprint_stop", [], 1.0, "04_sprint_stop")
        transition("right_90", ["D"], 1.5, "05_right")
        transition("reverse_180", ["A"], 1.5, "06_reverse")
        transition("final_stop", [], 1.0, "07_final_idle")
        print("CONTROL_PHASES_COMPLETED", len(events), flush=True)
    except Exception as exc:
        errors.append(str(exc))
        print("FAIL_CLOSED", str(exc), flush=True)
    finally:
        for code in reversed(held[:]):
            try:
                key(code, False)
            except Exception as exc:
                errors.append("KEY_RELEASE_" + str(exc))
        if video is not None:
            try:
                video.stdin.write(b"q\n")
                video.stdin.flush()
                video.wait(timeout=12)
            except Exception as exc:
                errors.append("VIDEO_SHUTDOWN_" + str(exc))
                video.terminate()
                try:
                    video.wait(timeout=5)
                except Exception:
                    pass
        if pid and host and host.poll() is None:
            try:
                close_owned(pid)
            except Exception as exc:
                errors.append("CLOSE_" + str(exc))
        if host:
            try:
                host.wait(timeout=30)
            except subprocess.TimeoutExpired:
                errors.append("HOST_TIMEOUT")
        coordinator.close()
        stderrfile.close()

        logfile = out / "game.log"
        log = logfile.read_text(encoding="utf8", errors="replace") if logfile.exists() else ""
        startinfo = json.loads((out / "host.json").read_text(encoding="utf-8-sig")) if (
            out / "host.json").exists() else {}
        facing = [x for x in log.splitlines() if "TSTSS_ENDER_FACING_SAMPLE" in x]
        speeds = [x for x in log.splitlines() if "TSTSS_ENDER_PIE_WALKRUN_APPLIED" in x]
        toe = [x for x in log.splitlines() if "TSTSS_ENDER_FOOT_SAMPLE" in x]
        bound = [x for x in log.splitlines() if "TSTSS_ENDER_PRIVATE_BLENDSPACE_BOUND" in x]
        legacy = [x for x in log.splitlines() if "TSTSS_ENDER_PIE_ANIM_REQUESTED" in x]
        speedband = [x for x in log.splitlines() if "TSTSS_ENDER_PRIVATE_BLENDSPACE_BAND" in x]
        usecorrect = (
            (args.variant == "blend" and bound and not legacy
             and any("band=2" in x for x in speedband)
             and any("band=0" in x for x in speedband))
            or (args.variant == "legacy" and legacy and not bound))
        good = (not errors and len(events) >= 15 and usecorrect and len(toe) >= 120
                and len(speeds) >= 2 and len(facing) >= 2
                and startinfo.get("child_exit_code") == 0
                and startinfo.get("assets_unchanged") is True
                and startinfo.get("source_clean") is True)
        videook = False
        video_metadata = {"status": "NOT_EVALUATED"}
        if video is not None and video.returncode == 0:
            try:
                videook, video_metadata = validate_video(vidfile)
            except Exception as exc:
                video_metadata = {"status": "HOLD_VIDEO_PROBE", "error": str(exc)}
        (out / "video-validation.json").write_text(
            json.dumps(video_metadata, indent=2), encoding="utf8")
        good = good and videook
        receipt = {
            "source_sha": args.head,
            "status": "NATIVE_AUTOMATED_ENDER_PIVOT_INPUT_PASS" if good else "HOLD_ENDER_PIVOT",
            "variant": args.variant, "errors": errors,
            "events": events, "frame_count": len([x for x in events if "image" in x]),
            "video": "DYNAMIC_OWNED_GAME_REGION" if videook and video and video.returncode == 0
                     else "NOT_VERIFIED",
            "video_bytes": vidfile.stat().st_size if vidfile.exists() else 0,
            "video_validation": video_metadata,
            "facing_sample_count": len(facing),
            "facing_samples": facing,
            "toe_sample_count": len(toe),
            "movement_state_count": len(speeds),
            "legacy_direct_clip_count": len(legacy),
            "blend_bound_count": len(bound),
            "band_samples": speedband,
            "protected_count": startinfo.get("protected_count"),
            "assets_unchanged": startinfo.get("assets_unchanged"),
            "source_clean": startinfo.get("source_clean"),
            "game_exit": startinfo.get("child_exit_code"),
            "keyboard": "WINDOW_FOCUSED_OS_INJECTED_NOT_HUMAN",
            "fluidity_and_art_acceptance": "NOT_ESTABLISHED"
        }
        (out / "verdict.json").write_text(json.dumps(receipt, indent=2), encoding="utf8")
        print("PIVOT_RESULT", receipt["status"], "toe", len(toe),
              "facing", len(facing), "frames", receipt["frame_count"],
              "video", receipt["video"], flush=True)
        if not good:
            sys.exit(3)


if __name__ == "__main__":
    main()
