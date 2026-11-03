#!/usr/bin/env python3
"""Compile the actual Unreal Level 1 rank header with minimal API stand-ins.

This is a PORTABLE C++ behavioral test, NOT Unreal Engine/UHT/Blueprint or
native Editor automation. Fixture numbers are illustrative, never stat canon.
The negative control mutates an isolated header copy and must fail.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "Source" / "ToSailTheStarrySky" / "Public"
HEADER = PUBLIC / "TSTSSLevelOneStatRanking.h"
VCVARS = Path(
    r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools"
    r"\VC\Auxiliary\Build\vcvars64.bat"
)

CORE = r'''
#pragma once
#include <string>
#include <map>
#include <vector>
#include <cstdint>
#include <initializer_list>
using int32 = int32_t;
using TCHAR = wchar_t;
#define TEXT(x) L##x
struct FName {
    std::wstring value;
    FName() = default;
    explicit FName(const wchar_t* text) : value(text ? text : L"") {}
    bool operator<(const FName& rhs) const { return value < rhs.value; }
    bool operator==(const FName& rhs) const { return value == rhs.value; }
};
static const FName NAME_None;
template<class T> struct TArray {
    std::vector<T> entries;
    TArray() = default;
    TArray(std::initializer_list<T> values) : entries(values) {}
    int32 Num() const { return static_cast<int32>(entries.size()); }
    auto begin() const { return entries.begin(); }
    auto end() const { return entries.end(); }
};
template<class K, class V> struct TMap {
    std::map<K, V> entries;
    bool Contains(const K& key) const { return entries.find(key) != entries.end(); }
    void Add(const K& key, const V& value) { entries.emplace(key, value); }
    V FindRef(const K& key) const {
        auto it = entries.find(key);
        return it == entries.end() ? V{} : it->second;
    }
};
'''

DRIVER = r'''
#include <algorithm>
#include <cstdlib>
#include <iostream>
#include "TSTSSLevelOneStatRanking.h"
using Stats = FTSTSSLevelOneRankCandidate;
static Stats Make(const wchar_t* name, int hp, int mp, int mag, int level=1) {
    Stats s;
    s.CharacterId = FName(name);
    s.Level = level;
    s.MaxHealth = hp;
    s.MaxMagicPoints = mp;
    s.MagicPower = mag;
    return s;
}
static int checks = 0;
static void Require(bool condition, const char* name) {
    ++checks;
    if (!condition) {
        std::cerr << "FAIL: " << name << "\n";
        std::exit(1);
    }
}
int main() {
    TArray<Stats> base = {
        Make(L"Ender",101,64,27), Make(L"Ionia",112,28,8),
        Make(L"Lyra",86,52,19), Make(L"Reson",123,20,9),
        Make(L"Aepex",108,38,11)
    };
    Require(FTSTSSLevelOneRankContract::Validate(base), "accepted positive");
    auto v = base;
    std::swap(v.entries[0], v.entries[4]);
    Require(FTSTSSLevelOneRankContract::Validate(v), "array order independent");
    v=base; v.entries[1].MagicPower=17; v.entries[3].MagicPower=1;
    v.entries[4].MagicPower=12;
    Require(FTSTSSLevelOneRankContract::Validate(v), "other three unranked");
    v=base; v.entries[0].MagicPower=19;
    Require(!FTSTSSLevelOneRankContract::Validate(v), "ender mag tie");
    v=base; v.entries[2].MaxMagicPoints=28;
    Require(!FTSTSSLevelOneRankContract::Validate(v), "lyra mp tie");
    v=base; v.entries[4].MaxHealth=101;
    Require(!FTSTSSLevelOneRankContract::Validate(v), "aepex hp tie");
    v=base; v.entries[1].MaxHealth=86;
    Require(!FTSTSSLevelOneRankContract::Validate(v), "ionia hp too low");
    v=base; v.entries[1].CharacterId=FName(L"Ender");
    Require(!FTSTSSLevelOneRankContract::Validate(v), "duplicate id");
    v=base; v.entries[4].CharacterId=FName(L"Talen");
    Require(!FTSTSSLevelOneRankContract::Validate(v), "unknown id");
    v=base; v.entries.pop_back();
    Require(!FTSTSSLevelOneRankContract::Validate(v), "missing id");
    v=base; v.entries[0].Level=0;
    Require(!FTSTSSLevelOneRankContract::Validate(v), "bad level");
    v=base; v.entries[0].MaxMagicPoints=1000000;
    Require(!FTSTSSLevelOneRankContract::Validate(v), "max MP bounds");
    v=base; v.entries[4].MagicPower=-1;
    Require(!FTSTSSLevelOneRankContract::Validate(v), "negative MAG");
    v=base; v.entries[2].MaxHealth=1; v.entries[0].MaxHealth=2;
    v.entries[1].MaxHealth=3; v.entries[3].MaxHealth=3;
    v.entries[4].MaxHealth=3;
    v.entries[0].MaxMagicPoints=2; v.entries[2].MaxMagicPoints=1;
    v.entries[1].MaxMagicPoints=0; v.entries[3].MaxMagicPoints=0;
    v.entries[4].MaxMagicPoints=0;
    v.entries[0].MagicPower=2; v.entries[2].MagicPower=1;
    v.entries[1].MagicPower=0; v.entries[3].MagicPower=0;
    v.entries[4].MagicPower=0;
    Require(FTSTSSLevelOneRankContract::Validate(v), "valid integer boundary");
    std::cout << "PASS: " << checks << " compiled C++ rank checks (NOT UE tests)\n";
    return 0;
}
'''

def compiler_command(tmp: Path, executable: Path, source: Path) -> list[str]:
    if os.name == "nt":
        flags = [
            "/nologo", "/std:c++17", "/EHsc", "/W3",
            f"/I{tmp}", f"/I{PUBLIC}", str(source), f"/Fe:{executable}"
        ]
        cl = shutil.which("cl")
        if cl:
            return [cl, *flags]
        if VCVARS.is_file():
            # On Windows, subprocess list2cmdline can double-escape quoted
            # multi-command strings passed directly to cmd /c. Write a tiny
            # disposable batch file instead, with no persistent VS changes.
            quoted = " ".join('"' + flag + '"' if " " in flag else flag for flag in flags)
            runner = tmp / "compile_with_msvc.cmd"
            runner.write_text(
                "@echo off\n"
                + f'call "{VCVARS}" >nul\n'
                + "if errorlevel 1 exit /b 5\n"
                + f"cl {quoted}\n"
                + "exit /b %ERRORLEVEL%\n",
                encoding="utf-8",
            )
            return ["cmd.exe", "/d", "/c", str(runner)]
        raise RuntimeError("MSVC cl.exe and vcvars64.bat unavailable")
    compiler = shutil.which("g++") or shutil.which("clang++")
    if not compiler:
        raise RuntimeError("No available C++ compiler (g++/clang++)")
    return [
        compiler, "-std=c++17", "-Wall", "-Wextra",
        "-I", str(tmp), "-I", str(PUBLIC),
        str(source), "-o", str(executable)
    ]

def compile_and_run(tmp: Path, name: str) -> subprocess.CompletedProcess[str]:
    executable = tmp / (name + (".exe" if os.name == "nt" else ""))
    source = tmp / "rank_host.cpp"
    command = compiler_command(tmp, executable, source)
    build = subprocess.run(command, capture_output=True, text=True, check=False)
    if build.returncode != 0:
        raise RuntimeError(f"C++ compile FAILED ({name}):\n{build.stdout}\n{build.stderr}")
    return subprocess.run([str(executable)], capture_output=True, text=True, check=False)

def main() -> int:
    original = HEADER.read_text(encoding="utf-8")
    anchor = "Ender->MagicPower > Lyra->MagicPower"
    if original.count(anchor) != 1:
        raise RuntimeError("Expected strict Ender/Lyra MAG expression absent/ambiguous")
    with tempfile.TemporaryDirectory(prefix="tstss_rank_host_") as directory:
        tmp = Path(directory)
        (tmp / "CoreMinimal.h").write_text(CORE, encoding="utf-8")
        (tmp / "rank_host.cpp").write_text(DRIVER, encoding="utf-8")
        positive = compile_and_run(tmp, "correct")
        if positive.returncode != 0 or "PASS: 14 compiled C++ rank checks" not in positive.stdout:
            raise RuntimeError(f"Real rank header behavioral tests FAILED: {positive.stdout} {positive.stderr}")
        print(positive.stdout.strip())

        # Deliberately break the first strict comparison in a disposable copy;
        # a harness that still passes is not a trustworthy validation gate.
        modified = original.replace(anchor, "Ender->MagicPower < Lyra->MagicPower")
        (tmp / "TSTSSLevelOneStatRanking.h").write_text(modified, encoding="utf-8")
        negative = compile_and_run(tmp, "mutant")
        if negative.returncode == 0 or "FAIL: accepted positive" not in negative.stderr:
            raise RuntimeError(
                "Mutation negative control did not fail for the expected reason: "
                f"{negative.stdout} {negative.stderr}"
            )
        print("PASS: deliberate strict-MAG comparison mutation rejected")
    print("ENGINE FREE ONLY: Unreal UHT, reflected DataAsset and Editor automation NOT run")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        sys.exit(1)
