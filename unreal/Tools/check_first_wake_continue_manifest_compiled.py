"""Compile/run actual First Wake manifest validation C++ with tiny API doubles.

Not an Unreal build, UHT check, gameplay simulation, or proof of real F6.
Use after MSVC vcvars64.bat. No save files, actor states or maps touched.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
CPP = ROOT/"Source/ToSailTheStarrySky/Private/TSTSSReviewContinueManifest.cpp"

STUB = r"""
#pragma once
#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cwctype>
#include <iostream>
#include <string>
#include <vector>
using uint8=std::uint8_t;
#define TEXT(x) L##x
namespace ESearchCase { enum Type {CaseSensitive,IgnoreCase}; }
class FString {
public:
    std::wstring value;
    FString()=default;
    FString(const wchar_t* x):value(x){}
    FString(const std::wstring& x):value(x){}
    bool operator!=(const FString& other) const {return value!=other.value;}
    bool operator==(const FString& other) const {return value==other.value;}
    int Len() const {return (int)value.size();}
    bool Equals(const FString& other,ESearchCase::Type cs) const {
        if(cs==ESearchCase::CaseSensitive)return value==other.value;
        if(value.size()!=other.value.size())return false;
        for(size_t i=0;i<value.size();++i)
            if(std::towlower(value[i])!=std::towlower(other.value[i]))return false;
        return true;
    }
    bool StartsWith(const FString& prefix)const{
        return value.size()>=prefix.value.size() &&
            value.compare(0,prefix.value.size(),prefix.value)==0;
    }
};
struct FMath {
    static bool IsFinite(double v){return std::isfinite(v);}
    static double Abs(double v){return std::fabs(v);}
};
struct FVector {double X=0,Y=0,Z=0; FVector()=default;
    FVector(double x,double y,double z):X(x),Y(y),Z(z){}};
struct FRotator {double Pitch=0,Yaw=0,Roll=0; FRotator()=default;
    FRotator(double p,double y,double r):Pitch(p),Yaw(y),Roll(r){}};
enum class ETSTSSFirstWakeBeat : uint8 {
    FlyerDiscovered,IoniaHired,BoardedAureateWake,EngineeringChecked,
    Launched,SeaContact,FlotationConfirmed,EmptyReserveInspected,ReturnedToBerth
};
struct DummyRoster {int count=0; int Num()const{return count;}};
struct UTSTSSSaveGame {
    static constexpr int CurrentVersion=2;
    bool valid=true;
    DummyRoster PartyRoster;
    bool bFirstWakeStarted=true;
    ETSTSSFirstWakeBeat FirstWakeBeat=ETSTSSFirstWakeBeat::IoniaHired;
    uint8 InspectionMask=0;
    bool IsStructurallyValid() const {return valid;}
    bool IsSupportedVersion() const {return valid;}
};
template<class T> bool IsValid(const T* p){return p!=nullptr;}
struct UTSTSSReviewContinueManifest {
    static constexpr int CurrentReviewVersion=1;
    int ReviewVersion=CurrentReviewVersion;
    FString ReviewProtocol=TEXT("TSTSS_FIRST_WAKE_PIE_CONTINUE_V1");
    FString PrimarySlot=TEXT("tstss_prelude_pie_quick");
    FString ProjectRoot=TEXT("C:/TSTSS_ReviewSandbox/unreal/");
    FString ReviewMapPackage=
        TEXT("/Game/TSTSS/Review/FirstWake_LaunchWaterGreybox_V1");
    FString PrimaryBlake3_160=TEXT("aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa");
    int PrimarySchemaVersion=2;
    bool bSavedStoryStarted=true;
    ETSTSSFirstWakeBeat SavedBeat=ETSTSSFirstWakeBeat::IoniaHired;
    uint8 SavedInspectionMask=0;
    FVector SavedPawnLocation=FVector(-1300,0,90);
    FRotator SavedPawnRotation;
    FRotator SavedControlRotation;
    bool IsBoundFor(const UTSTSSSaveGame*, const FString&,
        const FString&, const FString&, const FString&) const;
};
"""
HARNESS=r"""
#include "TSTSSReviewContinueManifest.h"
#include <limits>
int main(){
    UTSTSSSaveGame p;
    UTSTSSReviewContinueManifest m;
    const FString slot=TEXT("tstss_prelude_pie_quick");
    const FString project=m.ProjectRoot, map=m.ReviewMapPackage, hash=m.PrimaryBlake3_160;
    int passed=0,failed=0;
    auto check=[&](const char* name,bool expected,bool actual){
        if(expected==actual){++passed;std::cout<<"PASS "<<name<<"\n";}
        else{++failed;std::cout<<"FAIL "<<name<<"\n";}
    };
    auto ok=[&](){return m.IsBoundFor(&p,slot,project,map,hash);};
    check("valid_bound_rosterfree_prelaunch",true,ok());
    check("null_primary",false,m.IsBoundFor(nullptr,slot,project,map,hash));
    check("foreign_project",false,m.IsBoundFor(&p,slot,TEXT("D:/AnotherGame/"),map,hash));
    check("foreign_map",false,m.IsBoundFor(&p,slot,project,TEXT("/Game/AnotherMap"),hash));
    check("modified_primary_digest",false,m.IsBoundFor(&p,slot,project,map,
        TEXT("bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb")));
    m.ReviewVersion=99;check("future_manifest",false,ok());m.ReviewVersion=1;
    m.ReviewProtocol=TEXT("OTHER");check("unknown_protocol",false,ok());
    m.ReviewProtocol=TEXT("TSTSS_FIRST_WAKE_PIE_CONTINUE_V1");
    m.PrimarySlot=TEXT("other");check("foreign_slot",false,ok());
    m.PrimarySlot=slot;
    m.PrimarySchemaVersion=99;check("unknown_save_schema",false,ok());
    m.PrimarySchemaVersion=2;
    p.PartyRoster.count=1;check("combat_roster_forbidden",false,ok());p.PartyRoster.count=0;
    m.SavedPawnLocation.X=100001;check("out_of_bounds_pawn",false,ok());
    m.SavedPawnLocation.X=-1300;
    m.SavedPawnLocation.X=std::numeric_limits<double>::quiet_NaN();
    check("nan_pawn",false,ok());m.SavedPawnLocation.X=-1300;
    m.SavedControlRotation.Yaw=std::numeric_limits<double>::infinity();
    check("infinite_view_rotation",false,ok());m.SavedControlRotation.Yaw=0;
    m.SavedInspectionMask=1;check("mask_disagrees_with_primary",false,ok());
    m.SavedInspectionMask=0;
    m.SavedBeat=ETSTSSFirstWakeBeat::Launched;
    p.FirstWakeBeat=ETSTSSFirstWakeBeat::Launched;p.InspectionMask=7;
    m.SavedInspectionMask=7;check("uncaptured_flight_rejected",false,ok());
    p.FirstWakeBeat=ETSTSSFirstWakeBeat::IoniaHired;p.InspectionMask=0;
    m.SavedBeat=ETSTSSFirstWakeBeat::IoniaHired;m.SavedInspectionMask=0;
    p.valid=false;check("structurally_bad_primary",false,ok());p.valid=true;
    check("recovery_to_valid_after_negatives",true,ok());
    std::cout<<"TOTAL "<<passed<<" "<<failed<<"\n";
    return failed?1:0;
}
"""
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--self-test",action="store_true")
    ap.parse_args()
    if "bool UTSTSSReviewContinueManifest::IsBoundFor(" not in CPP.read_text():
        raise RuntimeError("Real manifest C++ signature absent")
    with tempfile.TemporaryDirectory(prefix="tstss-continue-msvc-") as td:
        tmp=Path(td)
        (tmp/"TSTSSReviewContinueManifest.h").write_text(STUB)
        (tmp/"TSTSSSaveGame.h").write_text('#include "TSTSSReviewContinueManifest.h"\n')
        (tmp/"checks.cpp").write_text(HARNESS)
        binary=tmp/"continue_api_doubles.exe"
        cmd=["cl","/nologo","/std:c++20","/EHsc",
             "/I"+str(tmp),str(CPP),str(tmp/"checks.cpp"),"/Fe:"+str(binary)]
        built=subprocess.run(cmd,cwd=tmp,text=True,capture_output=True)
        if built.returncode:
            print(built.stdout[-5000:],built.stderr[-5000:])
            raise RuntimeError("Actual C++ body rejected by MSVC API doubles")
        result=subprocess.run([str(binary)],cwd=tmp,text=True,capture_output=True)
        print(result.stdout)
        if result.returncode or "TOTAL 17 0" not in result.stdout:
            raise RuntimeError("Compiled source contract checks failed")
        print("MSVC_SOURCE_BODY_API_DOUBLE_17_OF_17_PASS_NOT_NATIVE_UE")
if __name__=="__main__":main()
