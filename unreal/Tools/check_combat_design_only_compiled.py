#!/usr/bin/env python3
"""Compile and execute the EXACT C++ DesignOnly bridge with tiny UE API doubles.

This checks source-extracted adapter behavior with a real host C++ compiler.
It is NOT UHT, Unreal compilation, an Editor test, or runtime authorization.
The upstream FTSTSSCombatData::ValidateActions API is deliberately a stub
here; its real source has separate native regression cases.
"""
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Source/ToSailTheStarrySky/Private/TSTSSCombatSkillReconciliation.cpp"
HEADER = '#include "TSTSSCombatSkillReconciliation.h"'

STUB = r"""
#include <iostream>
#include <map>
#include <set>
#include <string>
#include <utility>
#include <vector>

using FName = std::string;
template <class T> struct TArray : std::vector<T> {
    using std::vector<T>::vector;
    bool IsEmpty() const { return this->empty(); }
};
template <class K, class V> struct TMap : std::map<K,V> {
    using std::map<K,V>::map;
    void Add(const K& k, const V& v) { (*this)[k]=v; }
};
template <class T> T&& MoveTemp(T& value) { return std::move(value); }

enum class ETSTSSActionCategory { Spell, WeaponTechnique, Attack, Support };
enum class ETSTSSActionTarget { Self, Ally, Enemy };
enum class ETSTSSBattleSkillKind { Spell, WeaponTechnique, JobArt };
enum class ETSTSSBattleSkillTarget { Self, Ally, Enemy };
enum class ETSTSSBattleSkillAdmission { DesignOnly, ReviewExecutable };
struct FTSTSSActionDefRow {
    FName ActionId;
    ETSTSSActionCategory Category=ETSTSSActionCategory::Spell;
    ETSTSSActionTarget Target=ETSTSSActionTarget::Enemy;
    int Power=0,Cost=0;
    bool bHealing=false;
};
struct FTSTSSBattleSkillRow {
    FName SkillId;
    ETSTSSBattleSkillKind Kind=ETSTSSBattleSkillKind::JobArt;
    ETSTSSBattleSkillTarget Target=ETSTSSBattleSkillTarget::Enemy;
    ETSTSSBattleSkillAdmission Admission=ETSTSSBattleSkillAdmission::DesignOnly;
    int Power=0,ResourceCost=0,RequiredMasteryRank=0;
    bool bHealing=false;
    FName RequiredSchool,RequiredWeaponClass,RequiredSecondarySchool;
};
struct FTSTSSDataIssueEntry {int code;};
struct FTSTSSCombatData {
    static bool ValidateActions(const TArray<FTSTSSActionDefRow>& rows,
                                bool shipping,TArray<FTSTSSDataIssueEntry>& issues) {
        if (shipping || rows.empty()) return false;
        std::set<FName> ids;
        for (const auto& r:rows) {
            if (r.ActionId.empty() || !ids.insert(r.ActionId).second ||
                r.Power<0 || r.Cost<0 ||
                (r.bHealing && r.Target==ETSTSSActionTarget::Enemy)) {
                issues.push_back({1}); return false;
            }
        }
        return true;
    }
};
struct FTSTSSCombatSkillReconciliation {
    static bool TryPrepareDesignOnly(
        const TArray<FTSTSSActionDefRow>& rows,
        TMap<FName,FTSTSSBattleSkillRow>& out);
};
"""
TESTS = r"""
int failures=0,tests=0;
void check(bool value,const char* label){
    ++tests;
    if(!value){++failures;std::cerr<<"FAIL "<<label<<"\n";}
}
FTSTSSActionDefRow make(const char* id,ETSTSSActionCategory category,
                        ETSTSSActionTarget target,bool heal=false){
    FTSTSSActionDefRow action;
    action.ActionId=id;action.Category=category;action.Target=target;
    action.bHealing=heal;action.Power=4;action.Cost=2;
    return action;
}
int main(){
    using A=ETSTSSActionCategory;
    using T=ETSTSSActionTarget;
    using K=ETSTSSBattleSkillKind;
    using G=ETSTSSBattleSkillTarget;
    using M=ETSTSSBattleSkillAdmission;
    const auto spell=make("DesignSpell",A::Spell,T::Enemy);
    const auto tech=make("DesignStaffMove",A::WeaponTechnique,T::Self);
    TMap<FName,FTSTSSBattleSkillRow> out;
    check(FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly({spell,tech},out),
          "valid Spell+Technique accepted");
    check(out.size()==2,"two rows exported");
    check(out.count("DesignSpell")==1 && out.count("DesignStaffMove")==1,
          "both names survive");
    if(out.count("DesignSpell")){
        const auto& r=out.at("DesignSpell");
        check(r.Kind==K::Spell && r.Target==G::Enemy,
              "spell kind/target are preserved");
        check(r.Power==4 && r.ResourceCost==2 && !r.bHealing,
              "spell mechanical metadata preserved");
        check(r.Admission==M::DesignOnly,
              "adapter never admits catalog magic");
        check(r.RequiredSchool.empty() && r.RequiredMasteryRank==0 &&
              r.RequiredSecondarySchool.empty() && r.RequiredWeaponClass.empty(),
              "no school/mastery/equipment invented");
    }
    if(out.count("DesignStaffMove")){
        const auto& r=out.at("DesignStaffMove");
        check(r.Kind==K::WeaponTechnique && r.Target==G::Self,
              "technique kind/target are preserved");
        check(r.Admission==M::DesignOnly && r.RequiredWeaponClass.empty(),
              "technique still unauthorised and unequipped");
    }
    const auto preserved=out;
    auto unsupported=make("GenericAttack",A::Attack,T::Enemy);
    check(!FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {spell,unsupported},out),"generic attack rejected atomically");
    unsupported.Category=A::Support;
    check(!FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {spell,unsupported},out),"generic support rejected atomically");
    check(!FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {spell,spell},out),"duplicate IDs rejected");
    auto heal=make("BadHeal",A::Spell,T::Enemy,true);
    check(!FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {heal},out),"enemy heal rejected");
    auto bad=make("",A::Spell,T::Enemy);
    check(!FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {bad},out),"missing action ID rejected");
    bad=make("Negative",A::Spell,T::Enemy);
    bad.Cost=-1;
    check(!FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {bad},out),"negative cost rejected");
    check(!FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {},out),"empty input rejected");
    bad=make("UnknownCategory",static_cast<A>(99),T::Enemy);
    check(!FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {bad},out),"unknown action category rejected");
    bad=make("UnknownTarget",A::Spell,static_cast<T>(99));
    check(!FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {bad},out),"unknown target rejected");
    check(out.size()==preserved.size() &&
          out.count("DesignSpell")==1 && out.count("DesignStaffMove")==1 &&
          out.at("DesignSpell").Admission==M::DesignOnly,
          "all failed conversions preserve old output");
    // A second successful conversion replaces rather than appends catalog.
    check(FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(
            {make("FriendlyDesign",A::Spell,T::Ally,true)},out),
          "valid ally heal accepted as DesignOnly");
    check(out.size()==1 && out.count("FriendlyDesign")==1,
          "success replaces old output atomically");
    if(out.count("FriendlyDesign"))check(
        out.at("FriendlyDesign").Target==G::Ally &&
        out.at("FriendlyDesign").bHealing &&
        out.at("FriendlyDesign").Admission==M::DesignOnly,
        "ally heal remains non-executable");
    std::cout<<"PASS "<<tests-failures<<"/"<<tests
             <<" source-extracted C++ adapter assertions; "
             <<"NOT a native Unreal Engine or UHT run.\n";
    return failures?1:0;
}
"""


def main():
    source=SOURCE.read_text(encoding="utf-8")
    if source.count(HEADER)!=1 or source.count(
        "FTSTSSCombatSkillReconciliation::TryPrepareDesignOnly(")!=1:
        raise SystemExit("HOLD: adapter C++ source signature drift")
    prefix,rest=source.split(HEADER,1)
    if prefix.strip() or not 1200<len(rest)<8000 or "#include" in rest:
        raise SystemExit("HOLD: unexpected adapter source shape")
    # Windows build agents commonly have MSVC through Visual Studio Build
    # Tools without GCC/Clang on PATH. Discover the actual vcvars64 environment
    # rather than declaring a compiler missing or installing anything.
    env = None
    compiler = next((p for name in ("g++","clang++","c++")
                     if (p:=shutil.which(name))),None)
    msvc = False
    if not compiler and sys.platform == "win32":
        where = Path(os.environ.get("ProgramFiles(x86)",
                     r"C:\\Program Files (x86)")) / "Microsoft Visual Studio" / "Installer" / "vswhere.exe"
        if where.is_file():
            result = subprocess.run(
                [str(where), "-latest", "-products", "*", "-requires",
                 "Microsoft.VisualStudio.Component.VC.Tools.x86.x64",
                 "-property", "installationPath"],
                capture_output=True, text=True, check=True)
            install = Path(result.stdout.strip()) if result.stdout.strip() else None
            vcvars = install / "VC" / "Auxiliary" / "Build" / "vcvars64.bat" if install else None
            if vcvars and vcvars.is_file():
                # Python 3.14 Windows list2cmdline re-quotes the batch
                # pathname incorrectly with cmd /c. The validated trusted
                # vcvars64 path comes only from installed VS Build Tools.
                export = subprocess.run(
                    f'call "{vcvars}" >nul && set', shell=True,
                    capture_output=True, text=True, check=True)
                env = dict(os.environ)
                for entry in export.stdout.splitlines():
                    if "=" in entry and not entry.startswith("="):
                        key, value = entry.split("=", 1)
                        env[key] = value
                compiler = shutil.which("cl.exe", path=env.get("PATH"))
                msvc = bool(compiler)
    if not compiler:
        raise SystemExit("HOLD: no configured GCC/Clang or MSVC compiler; fail closed")
    with tempfile.TemporaryDirectory() as td:
        src=Path(td)/"combat_bridge.cpp"
        exe=Path(td)/("combat_bridge.exe" if msvc else "combat_bridge")
        src.write_text(STUB+rest+TESTS,encoding="utf-8")
        if msvc:
            subprocess.run([compiler, "/nologo", "/std:c++17", "/O2",
                            "/EHsc", "/W4", "/WX", str(src),
                            "/Fe:" + str(exe)], cwd=td, env=env, check=True)
        else:
            subprocess.run([compiler,"-std=c++17","-O2","-Wall","-Wextra",
                            "-Werror","-pedantic",str(src),"-o",str(exe)],check=True)
        subprocess.run([str(exe)],check=True)


if __name__=="__main__":
    main()
