from pathlib import Path
import argparse
import shutil
import subprocess
import sys
import tempfile

parser = argparse.ArgumentParser(description="Isolated, real C++ request logic executable test")
parser.add_argument(
    "--source-only", action="store_true",
    help="Explicit source-bound screen on hosts without a C++ compiler; NOT an execution PASS")
args = parser.parse_args()

source = (Path(__file__).resolve().parents[1] / 'Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp').read_text()
start = source.index('bool AAureateWakePreviewActor::RequestForm(')
end = source.index('\nvoid AAureateWakePreviewActor::Tick', start)
method = source[start:end]
if args.source_only:
    # This mode is deliberately weaker than compiling and running RequestForm.
    # Linux CI must continue using the default executable C++ mode.
    for marker in ("bTransitioning || RequestedForm == CurrentForm",
                   "Wings.Num() != 4 || Hydrofoils.Num() != 2",
                   "bUseRootPivotedWingPose && !AuthoredWingMesh",
                   "RequestedForm == EAureateWakeForm::Orbiter || CurrentForm == EAureateWakeForm::Orbiter",
                   "Hydrofoils[Index]->SetVisibility("):
        if marker not in method:
            raise SystemExit("SOURCE HOLD missing RequestForm guard: " + marker)
    print("SOURCE SCREEN ONLY: request guards present; no C++ compiler or runtime executed")
    raise SystemExit(0)
compiler = next((p for name in ("g++", "clang++", "c++")
                 if (p := shutil.which(name))), None)
if compiler is None:
    print("C++ TOOLCHAIN UNAVAILABLE: g++/clang++/c++ required for executable RequestForm check; "
          "use --source-only only for an explicitly weaker audit", file=sys.stderr)
    raise SystemExit(2)
# Compile the actual RequestForm body against minimal boundary substitutes.
# This executes request logic, not Unreal components, transforms or rendering.
stub = r'''
#include <vector>
#include <iostream>
using int32 = int;
enum class EAureateWakeForm : unsigned char { Skyborne, Seaborne, Submersible, Orbiter };
struct FMath { static bool IsWithinInclusive(int v,int a,int b){return v>=a && v<=b;} };
template<class T> struct Array : std::vector<T> {
    int Num() const { return this->size(); }
    void Reset(){this->clear();}
    void Add(T value){this->push_back(value);}
};
struct Component {
    bool visible = false;
    int GetRelativeTransform() const {return 0;}
    void SetVisibility(bool value){visible=value;}
};
struct AAureateWakePreviewActor {
    Array<Component*> Wings, Hydrofoils;
    bool bTransitioning=false, bAllowOrbiterPreview=true;
    bool bUseRootPivotedWingPose=false, AuthoredWingMesh=false;
    EAureateWakeForm CurrentForm=EAureateWakeForm::Skyborne, TargetForm=CurrentForm;
    float StartSailBlend=0, OrbiterSailBlend=0, TargetSailBlend=0, TransitionElapsed=0;
    Array<int> StartWingTransforms,TargetWingTransforms,StartFoilTransforms,TargetFoilTransforms;
    static int WingPoseForMesh(EAureateWakeForm,int){return 0;}
    static int FoilPose(EAureateWakeForm,int){return 0;}
    bool RequestForm(EAureateWakeForm);
};
'''
main = r'''
int main(){
    int failures=0, cases=0;
    for(int mode=0;mode<4;++mode) for(int from=0;from<4;++from) for(int to=0;to<4;++to){
        if(from==to) continue;
        Component components[6];
        AAureateWakePreviewActor actor;
        for(int i=0;i<4;++i) actor.Wings.Add(&components[i]);
        for(int i=4;i<6;++i){components[i].visible=from==1;actor.Hydrofoils.Add(&components[i]);}
        actor.bUseRootPivotedWingPose=(mode==1 || mode==2);
        actor.AuthoredWingMesh=(mode==1);
        actor.bAllowOrbiterPreview=(mode!=3);
        actor.CurrentForm=static_cast<EAureateWakeForm>(from);
        bool accepted=actor.RequestForm(static_cast<EAureateWakeForm>(to));
        // Modes: cube unlocked, authored present, authored missing, cube locked.
        bool wantAccepted = mode==0 || (mode==1 && from!=3 && to!=3) || (mode==3 && to!=3);
        bool expected=wantAccepted ? (from==1 || to==1) : from==1;
        bool ok=accepted==wantAccepted && actor.bTransitioning==wantAccepted &&
            components[4].visible==expected && components[5].visible==expected &&
            actor.CurrentForm==static_cast<EAureateWakeForm>(from);
        if(!wantAccepted) ok=ok && actor.StartWingTransforms.empty() && actor.StartFoilTransforms.empty();
        ++cases;
        if(!ok){++failures;std::cout<<"FAIL mode "<<mode<<" foil visibility "<<from<<" -> "<<to<<"\n";}
    }
    std::cout<<cases<<" directed requests; "<<failures<<" failures. Isolated C++ method only; NOT Unreal verification.\n";
    return failures ? 1 : 0;
}
'''
with tempfile.TemporaryDirectory() as folder:
    cpp=Path(folder)/'probe.cpp'
    exe=Path(folder)/'probe'
    cpp.write_text(stub+method+main)
    subprocess.run([compiler, '-std=c++17', '-Wall', '-Wextra', str(cpp), '-o', str(exe)], check=True)
    raise SystemExit(subprocess.run([str(exe)]).returncode)
