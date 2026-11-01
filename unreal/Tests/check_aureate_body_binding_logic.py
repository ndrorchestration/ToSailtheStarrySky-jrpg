#!/usr/bin/env python3
"""Compile/execute the EXACT Unreal preview body-binding method with C++ doubles.

This is a portable behavioral gate, not Unreal/UHT, mesh, or render proof.
"""
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp"
BEGIN = "bool AAureateWakePreviewActor::RefreshBodyReviewMeshes()"
END = "\nvoid AAureateWakePreviewActor::RefreshWingMeshes()"

STUB = r'''
#include <string>
#include <iostream>
#include <cmath>
#define TEXT(x) x
struct FVector {
    float X,Y,Z;
    constexpr FVector(float x=0,float y=0,float z=0):X(x),Y(y),Z(z){}
    static const FVector ZeroVector,OneVector;
};
const FVector FVector::ZeroVector{0,0,0},FVector::OneVector{1,1,1};
struct FRotator {
    float P,Y,R;
    constexpr FRotator(float p=0,float y=0,float r=0):P(p),Y(y),R(r){}
    static const FRotator ZeroRotator;
};
const FRotator FRotator::ZeroRotator{0,0,0};
struct FString {
    std::string Str;
    bool StartsWith(const char* prefix) const {return Str.rfind(prefix,0)==0;}
};
struct UStaticMesh {
    std::string Path;
    FString GetPathName() const {return {Path};}
};
template<class T> struct TObjectPtr {
    T* Ptr=nullptr;
    TObjectPtr()=default;
    explicit TObjectPtr(T* p):Ptr(p){}
    T* Get() const {return Ptr;}
};
struct UStaticMeshComponent {
    UStaticMesh* Mesh=nullptr;
    FVector Location{33,44,55},Scale{9,9,9};
    FRotator Rotation{11,22,33};
    int Writes=0;
    void SetStaticMesh(UStaticMesh* p){Mesh=p;Writes++;}
    void SetRelativeLocation(FVector p){Location=p;Writes++;}
    void SetRelativeRotation(FRotator p){Rotation=p;Writes++;}
    void SetRelativeScale3D(FVector p){Scale=p;Writes++;}
};
enum class EAureateWakeForm {Skyborne,Seaborne,Submersible,Orbiter};
struct AAureateWakePreviewActor {
    UStaticMeshComponent *Hull=nullptr,*ForwardBridge=nullptr;
    bool bTransitioning=false,bUseAuthoredBodyReview=false;
    EAureateWakeForm CurrentForm=EAureateWakeForm::Skyborne;
    TObjectPtr<UStaticMesh> OriginalCubeWingMesh,AuthoredHullReviewMesh,AuthoredBridgeDomeReviewMesh;
    bool RefreshBodyReviewMeshes();
};
'''
TESTS = r'''
static bool eq(float a,float b){return std::abs(a-b)<.0001f;}
static bool eq(FVector a,FVector b){
    return eq(a.X,b.X)&&eq(a.Y,b.Y)&&eq(a.Z,b.Z);
}
static bool eq(FRotator a,FRotator b){
    return eq(a.P,b.P)&&eq(a.Y,b.Y)&&eq(a.R,b.R);
}
struct State {
    UStaticMesh* Mesh;
    FVector Loc,Scale;
    FRotator Rot;
    int Writes;
    explicit State(const UStaticMeshComponent& c):
        Mesh(c.Mesh),Loc(c.Location),Scale(c.Scale),Rot(c.Rotation),Writes(c.Writes){}
    bool unchanged(const UStaticMeshComponent& c) const {
        return Mesh==c.Mesh&&eq(Loc,c.Location)&&eq(Scale,c.Scale)
            &&eq(Rot,c.Rotation)&&Writes==c.Writes;
    }
};
int main(){
    UStaticMesh cube{"/Engine/BasicShapes/Cube.Cube"};
    UStaticMesh oldH{"/Game/OldHull"},oldB{"/Game/OldBridge"};
    UStaticMesh hull{"/Game/TSTSS/Review/ShipArt/HullCandidateV1/Source/StaticMeshes/Hull.Hull"};
    UStaticMesh dome{"/Game/TSTSS/Review/ShipArt/BridgeDomeCandidateV1/Source/StaticMeshes/Dome.Dome"};
    UStaticMesh wrongH{"/Game/TSTSS/Review/ShipArt/OtherCandidate/Bad.Bad"};
    UStaticMesh wrongB{"/Game/TSTSS/Review/ShipArt/BridgeDomeCandidateV2/Dome.Dome"};
    struct Case{
        int id;bool review;int form;bool transitioning,hasH,hasB;
        UStaticMesh *cube,*hull,*bridge;bool expected;
    };
    const Case cases[]={
        {0,false,0,false,true,true,&cube,nullptr,nullptr,true},
        {1,false,1,false,true,true,&cube,nullptr,nullptr,true},
        {2,true,0,false,true,true,&cube,&hull,&dome,true},
        {3,true,1,false,true,true,&cube,&hull,&dome,true},
        {4,true,2,false,true,true,&cube,&hull,&dome,true},
        {5,true,3,false,true,true,&cube,&hull,&dome,false},
        {6,false,3,false,true,true,&cube,nullptr,nullptr,false},
        {7,true,0,true,true,true,&cube,&hull,&dome,false},
        {8,false,0,true,true,true,&cube,nullptr,nullptr,false},
        {9,true,0,false,true,true,&cube,nullptr,&dome,false},
        {10,true,0,false,true,true,&cube,&hull,nullptr,false},
        {11,true,0,false,true,true,&cube,&wrongH,&dome,false},
        {12,true,0,false,true,true,&cube,&hull,&wrongB,false},
        {13,true,0,false,false,true,&cube,&hull,&dome,false},
        {14,true,0,false,true,false,&cube,&hull,&dome,false},
        {15,false,0,false,true,true,nullptr,&hull,&dome,false},
        {16,true,0,false,true,true,nullptr,&hull,&dome,true},
        {17,false,2,false,true,true,&cube,&hull,nullptr,true},
    };
    int failed=0;
    for(const auto& t:cases){
        UStaticMeshComponent hc,bc;
        hc.Mesh=&oldH;bc.Mesh=&oldB;
        AAureateWakePreviewActor actor;
        actor.Hull=t.hasH?&hc:nullptr;
        actor.ForwardBridge=t.hasB?&bc:nullptr;
        actor.bUseAuthoredBodyReview=t.review;
        actor.bTransitioning=t.transitioning;
        actor.CurrentForm=static_cast<EAureateWakeForm>(t.form);
        actor.OriginalCubeWingMesh=TObjectPtr<UStaticMesh>(t.cube);
        actor.AuthoredHullReviewMesh=TObjectPtr<UStaticMesh>(t.hull);
        actor.AuthoredBridgeDomeReviewMesh=TObjectPtr<UStaticMesh>(t.bridge);
        State oldHull(hc),oldBridge(bc);
        bool accepted=actor.RefreshBodyReviewMeshes();
        bool ok=accepted==t.expected;
        if(!t.expected)ok=ok&&oldHull.unchanged(hc)&&oldBridge.unchanged(bc);
        if(t.expected&&t.review){
            ok=ok&&hc.Mesh==t.hull&&bc.Mesh==t.bridge;
            ok=ok&&eq(hc.Scale,FVector::OneVector)&&eq(bc.Scale,FVector::OneVector);
            ok=ok&&eq(hc.Location,FVector::ZeroVector)&&eq(bc.Location,FVector(240,0,95));
            ok=ok&&eq(hc.Rotation,FRotator::ZeroRotator)&&eq(bc.Rotation,FRotator::ZeroRotator);
        }
        if(t.expected&&!t.review){
            ok=ok&&hc.Mesh==&cube&&bc.Mesh==&cube;
            ok=ok&&eq(hc.Scale,FVector(8,1.5f,.65f))
                &&eq(bc.Scale,FVector(2.1f,1.1f,1.1f));
            ok=ok&&eq(hc.Location,FVector::ZeroVector)
                &&eq(bc.Location,FVector(240,0,95));
        }
        ok=ok&&actor.CurrentForm==static_cast<EAureateWakeForm>(t.form)
             &&actor.bTransitioning==t.transitioning;
        if(!ok){failed++;std::cout<<"FAILED case "<<t.id<<"\n";}
    }
    std::cout<<(sizeof(cases)/sizeof(Case))
             <<" compiled source-extracted body review requests; "<<failed
             <<" failures. NOT a native Unreal engine test.\n";
    return failed?1:0;
}
'''


def main():
    code=SOURCE.read_text(encoding="utf-8")
    if code.count(BEGIN)!=1 or code.count(END)!=1:
        raise SystemExit("HOLD: body binding source markers not unique")
    body=code[code.index(BEGIN):code.index(END,code.index(BEGIN))]
    if not 1000<len(body)<7000:
        raise SystemExit("HOLD: unexpected body binding code size")
    compiler=next((p for name in ("g++","clang++","c++")
                   if (p:=shutil.which(name))),None)
    if compiler is None:
        raise SystemExit("HOLD: no real C++ compiler; no source-only bypass")
    with tempfile.TemporaryDirectory() as td:
        source=Path(td)/"body_binding.cpp"
        binary=Path(td)/"body_binding"
        source.write_text(STUB+body+TESTS,encoding="utf-8")
        subprocess.run([compiler,"-std=c++17","-O2","-Wall","-Wextra",
                        "-Werror","-pedantic",str(source),"-o",str(binary)],check=True)
        subprocess.run([str(binary)],check=True)


if __name__=="__main__":
    main()
