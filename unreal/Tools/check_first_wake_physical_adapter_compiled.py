#!/usr/bin/env python3
"""Compile the actual First Wake water adapter Tick method with narrow C++ API doubles.

Checks the production adapter's physics/overlap/waterline/provenance path.
No Unreal reflection, PIE, real collision, graphics, or SaveGame is exercised.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile

SRC = (Path(__file__).resolve().parents[1] /
       "Source/ToSailTheStarrySky/Private/TSTSSWaterContactAdapter.cpp")
SIGNATURE = "void ATSTSSWaterContactAdapter::Tick(float DeltaSeconds)"

API = r"""
#include <algorithm>
#include <cmath>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <vector>
#define TEXT(v) v
using FName = std::string;
template <class T> using TArray = std::vector<T>;
template <class T> struct TNumericLimits {
    static T Max() { return std::numeric_limits<T>::max(); }
};
struct FVector {
    float X=0, Y=0, Z=0;
    FVector() = default;
    FVector(float x, float y, float z):X(x),Y(y),Z(z){}
};
struct FBoxSphereBounds { FVector Origin, BoxExtent; };
struct FMath {
    static bool IsFinite(float v) { return std::isfinite(v); }
    static float Max(float a,float b) { return std::max(a,b); }
    static float Clamp(float v,float lo,float hi) { return std::max(lo,std::min(v,hi)); }
};
struct AActor {
    virtual ~AActor() = default;
    virtual void Tick(float) {}
    virtual bool ActorHasTag(const FName&) const { return false; }
    virtual void GetActorBounds(bool, FVector&, FVector&) const {}
    static int StaticClass() { return 0; }
};
template<class T> bool IsValid(const T* p) { return p != nullptr; }
struct UTSTSSFirstWakeState {
    enum Beat { Other, Launched, SeaContact, FlotationConfirmed } CurrentBeat=Launched;
    Beat GetCurrentBeat() const { return CurrentBeat; }
};
using ETSTSSFirstWakeBeat = UTSTSSFirstWakeState::Beat;
struct ATSTSSExplorerCharacter : AActor {
    UTSTSSFirstWakeState* State=nullptr;
    UTSTSSFirstWakeState* GetFirstWakeState() { return State; }
};
template<class T> T* Cast(AActor* p) { return dynamic_cast<T*>(p); }
struct UGameplayStatics {
    static AActor* Player;
    static AActor* GetPlayerCharacter(AActor*,int) { return Player; }
};
AActor* UGameplayStatics::Player=nullptr;
struct WaterActor : AActor {
    FName Tag="TSTSSWaterVolume";
    FVector Origin{0,0,0}, Extent{100,100,100};
    bool ActorHasTag(const FName& t) const override { return t==Tag; }
    void GetActorBounds(bool,FVector& o,FVector& e) const override { o=Origin;e=Extent; }
};
struct UStaticMeshComponent {
    bool Physics=true;
    FVector Location{0,0,120}, Extent{50,50,30}, Velocity{0,0,0};
    float Mass=100;
    std::vector<AActor*> Overlaps;
    int Forces=0;
    float LastForceZ=0;
    bool IsSimulatingPhysics() const { return Physics; }
    void GetOverlappingActors(TArray<AActor*>& out,int) const { out=Overlaps; }
    FBoxSphereBounds GetBounds() const { return {Location,Extent}; }
    FVector GetPhysicsLinearVelocity() const { return Velocity; }
    float GetMass() const { return Mass; }
    void AddForce(FVector f) { ++Forces; LastForceZ=f.Z; }
};
struct UTSTSSWaterLandingGate {
    int Resets=0, Samples=0;
    bool LastWet=false;
    float LastSpeed=0, LastDt=0;
    void Reset() { ++Resets; }
    bool Observe(float dt,bool wet,float speed,UTSTSSFirstWakeState*) {
        ++Samples; LastWet=wet; LastSpeed=speed; LastDt=dt; return false;
    }
};
struct ATSTSSWaterContactAdapter : AActor {
    using Super=AActor;
    UStaticMeshComponent* Hull=nullptr;
    UTSTSSFirstWakeState* Story=nullptr;
    UTSTSSWaterLandingGate* Gate=nullptr;
    bool bAutoBindPlayerStory=false;
    bool bEnablePrototypeBuoyancy=false;
    FName WaterVolumeTag="TSTSSWaterVolume";
    float HullDraftCm=120.f;
    float MaxBuoyantAccelerationCms2=1800.f;
    float VerticalDampingPerSecond=1.5f;
    void BindStory(UTSTSSFirstWakeState* next) { Story=next; if(Gate) Gate->Reset(); }
    void Tick(float DeltaSeconds) override;
};
"""
TEST = r"""
int checks=0;
void require(bool ok,const char* name) {
    if(!ok) throw std::runtime_error(name);
    ++checks;
}
int main() {
    try {
        UTSTSSFirstWakeState story, replacement;
        UTSTSSWaterLandingGate gate;
        UStaticMeshComponent hull;
        WaterActor water;
        ATSTSSWaterContactAdapter adapter;
        adapter.Gate=&gate;
        adapter.Story=&story;
        adapter.Hull=&hull;
        water.Origin=FVector(0,0,0); water.Extent=FVector(100,100,100);
        hull.Overlaps.push_back(&water);
        hull.Physics=false;
        adapter.Tick(0.1f);
        require(gate.Samples==0,"non_physics_hull_allowed");
        hull.Physics=true;
        water.Tag="NotWater";
        adapter.Tick(0.1f);
        require(gate.Samples==1 && !gate.LastWet,"untagged_volume_allowed");
        water.Tag="TSTSSWaterVolume";
        water.Extent.Z=50.f; // surface=50, below the true hull bottom=90
        adapter.Tick(0.1f);
        require(gate.Samples==2 && !gate.LastWet,"false_waterline_allowed");
        water.Extent.Z=100.f; // surface=100 > hull bottom=90
        adapter.Tick(0.1f);
        require(gate.Samples==3 && gate.LastWet && gate.LastDt==0.1f,
                "genuine_bounded_overlap_not_observed");
        require(hull.Forces==0,"buoyancy_enabled_without_authorization");
        hull.Velocity.Z=15.f;
        adapter.Tick(0.1f);
        require(gate.Samples==4 && gate.LastWet && gate.LastSpeed==15.f,
                "physical_vertical_speed_not_used");
        hull.Velocity.Z=std::numeric_limits<float>::quiet_NaN();
        int resets=gate.Resets;
        adapter.Tick(0.1f);
        require(gate.Samples==4 && gate.Resets>resets,"invalid_velocity_not_rejected");
        hull.Velocity.Z=0.f;
        water.Extent.Z=std::numeric_limits<float>::quiet_NaN();
        adapter.Tick(0.1f);
        require(gate.Samples==5 && !gate.LastWet,"nonfinite_water_bounds_allowed");
        water.Extent.Z=100.f;
        adapter.HullDraftCm=-1.f;
        resets=gate.Resets;
        adapter.Tick(0.1f);
        require(gate.Samples==5 && gate.Resets>resets,"invalid_hull_draft_not_rejected");
        adapter.HullDraftCm=120.f;
        adapter.bEnablePrototypeBuoyancy=true;
        adapter.Tick(0.1f);
        require(gate.Samples==6 && gate.LastWet && hull.Forces==1 && hull.LastForceZ>0,
                "optin_force_not_bounded_to_valid_overlap");
        water.Tag="NotWater";
        adapter.Tick(0.1f);
        require(hull.Forces==1 && gate.Samples==7 && !gate.LastWet,
                "force_applied_without_water");
        water.Tag="TSTSSWaterVolume";
        adapter.bEnablePrototypeBuoyancy=false;
        adapter.bAutoBindPlayerStory=true;
        ATSTSSExplorerCharacter player;
        player.State=&replacement;
        UGameplayStatics::Player=&player;
        resets=gate.Resets;
        adapter.Tick(0.1f);
        require(adapter.Story==&replacement && gate.Resets>resets && gate.LastWet,
                "possession_story_not_rebound");
        replacement.CurrentBeat=UTSTSSFirstWakeState::Other;
        adapter.Tick(0.1f);
        require(gate.Samples==8,"invalid_story_beat_not_held");
        std::cout<<"PASS: "<<checks<<" compiled real water adapter Tick checks (API doubles; not UE collision/PIE)\n";
        return 0;
    } catch(const std::exception& e) {
        std::cerr<<"ADAPTER_BEHAVIOR_FAILURE: "<<e.what()<<"\n";
        return 2;
    }
}
"""

def extract(source: str) -> str:
    if source.count(SIGNATURE) != 1:
        raise RuntimeError("Missing or duplicate production Tick method")
    start = source.index(SIGNATURE)
    opening = source.index("{", start)
    depth = 0
    for index in range(opening, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return source[start:index + 1]
    raise RuntimeError("Unterminated water adapter method")

def compile_run(compiler: str, method: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory(prefix="tstss-physical-adapter-") as tmp:
        root=Path(tmp)
        src=root/"water_adapter.cpp"
        exe=root/("water_adapter.exe" if Path(compiler).name.lower()=="cl.exe" else "water_adapter")
        src.write_text(API+"\n"+method+"\n"+TEST,encoding="utf-8")
        if Path(compiler).name.lower()=="cl.exe":
            cmd=[compiler,"/nologo","/std:c++17","/EHsc",str(src),
                 "/Fo:"+str(root/"water_adapter.obj"),"/Fe:"+str(exe)]
        else:
            cmd=[compiler,"-std=c++17","-O0",str(src),"-o",str(exe)]
        compile_result=subprocess.run(cmd,capture_output=True,text=True,timeout=45)
        if compile_result.returncode:
            raise RuntimeError("Adapter portable compile failed: "+(compile_result.stdout+compile_result.stderr)[-6000:])
        return subprocess.run([str(exe)],capture_output=True,text=True,timeout=15)

def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--self-test",action="store_true")
    args=parser.parse_args()
    compiler=next((found for name in ("g++","clang++","c++","cl")
                   if (found:=shutil.which(name))),None)
    if not compiler:
        raise RuntimeError("C++17 compiler required; source-only test cannot run")
    method=extract(SRC.read_text(encoding="utf-8"))
    result=compile_run(compiler,method)
    if result.returncode:
        raise RuntimeError(result.stderr+result.stdout)
    print(result.stdout.strip())
    if args.self_test:
        mutations=[
            ("|| !Hull->IsSimulatingPhysics()","", "non_physics_hull_allowed"),
            ("Other->ActorHasTag(WaterVolumeTag)","true","untagged_volume_allowed"),
            ("bBelowSurface && Submersion > 0.01f","Submersion > 0.01f","false_waterline_allowed"),
        ]
        for original, replacement, failure in mutations:
            if method.count(original)!=1:
                raise RuntimeError("Mutation marker missing or duplicated: "+original)
            negative=compile_run(compiler,method.replace(original,replacement,1))
            if negative.returncode!=2 or negative.stderr.strip()!="ADAPTER_BEHAVIOR_FAILURE: "+failure:
                raise RuntimeError("Unsafe mutation not rejected as intended: "+failure+
                                   " stdout="+negative.stdout+" stderr="+negative.stderr)
            print("PASS: rejected mutation "+failure)
    print("Actual Tick body compiled with stand-ins, NOT an Unreal physics simulation.")

if __name__=="__main__":
    main()
