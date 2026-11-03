#!/usr/bin/env python3
"""Create a new empty isolated UE 5.8.4 project for native V4 mesh review.

No project, map, plugin, gameplay, source asset or existing sandbox is touched.
Any occupied destination is refused. This tool does NOT run Unreal.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parent))
from import_aureate_cinematic_v4_review import preflight

MARKER="AUREATE_CINEMATIC_V4_REVIEW_ONLY"
PROJECT_NAME="AureateCinematicV4Sandbox"
DEFAULT_ROOT=Path("C:/tmp/TSTSS_AureateCinematicV4_Native_20261103")
DEFAULT_SOURCE=Path("C:/tmp/TSTSS_AureateCinematicV4_Output_20261103")


def bootstrap(root:Path,source:Path):
    if root.exists():
        raise FileExistsError("Refuse existing project root: "+str(root))
    receipt=preflight(source)
    executable=Path("C:/Program Files/Epic Games/UE_5.8/Engine/Binaries/Win64/UnrealEditor-Cmd.exe")
    if not executable.is_file():
        raise FileNotFoundError("Expected verified installed Unreal 5.8 Editor")
    if shutil.disk_usage(root.parent if root.parent.exists() else Path("C:/")).free < 15 * 1024**3:
        raise RuntimeError("Need >=15 GiB disk headroom before generating UE project")
    sandbox=root/PROJECT_NAME
    sandbox.mkdir(parents=True,exist_ok=False)
    project_data={
        "FileVersion":3,
        "EngineAssociation":"5.8",
        "Category":"Games",
        "Description":"Aureate Wake V4 detail assets; "+MARKER+"; zero gameplay/save/promoted art.",
        "Plugins":[{"Name":"PythonScriptPlugin","Enabled":True},
                   {"Name":"PythonAutomationTest","Enabled":True}],
    }
    project_path=sandbox/(PROJECT_NAME+".uproject")
    project_path.write_text(json.dumps(project_data,indent=2)+"\n",encoding="utf-8")
    (sandbox/"Content").mkdir()
    (sandbox/"Config").mkdir()
    config="[Core.Log]\nLogPython=VeryVerbose\nLogInterchangeEngine=Verbose\n"
    (sandbox/"Config"/"DefaultEngine.ini").write_text(config,encoding="utf-8")
    out={"status":"DISPOSABLE_REVIEW_PROJECT_CREATED_NOT_NATIVE_IMPORTED",
         "engine_association":"5.8",
         "sandbox":str(sandbox),"project_file":str(project_path),
         "project_sha256":hashlib.sha256(project_path.read_bytes()).hexdigest(),
         "glb_preflight":receipt,"game_project_touched":False,
         "native_editor_executed":False,"production_modified":False,
         "starbourne_gate_changed":False}
    (root/"bootstrap_receipt.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    return out


def main(argv=None):
    p=argparse.ArgumentParser()
    p.add_argument("--root",type=Path,default=DEFAULT_ROOT)
    p.add_argument("--source",type=Path,default=DEFAULT_SOURCE)
    args=p.parse_args(argv)
    print(json.dumps(bootstrap(args.root,args.source),indent=2,sort_keys=True))


if __name__=="__main__":
    main()
