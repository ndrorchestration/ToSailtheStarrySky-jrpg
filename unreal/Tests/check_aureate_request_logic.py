from pathlib import Path
import subprocess
import tempfile

source = (Path(__file__).resolve().parents[1] / 'Source/ToSailTheStarrySky/Private/AureateWakePreviewActor.cpp').read_text()
start = source.index('bool AAureateWakePreviewActor::RequestForm(')
end = source.index('\nvoid AAureateWakePreviewActor::Tick', start)
method = source[start:end]
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
    EAureateWakeForm CurrentForm=EAureateWakeForm::Skyborne, TargetForm=CurrentForm;
    float StartSailBlend=0, OrbiterSailBlend=0, TargetSailBlend=0, TransitionElapsed=0;
    Array<int> StartWingTransforms,TargetWingTransforms,StartFoilTransforms,TargetFoilTransforms;
    static int WingPose(EAureateWakeForm,int){return 0;}
    static int FoilPose(EAureateWakeForm,int){return 0;}
    bool RequestForm(EAureateWakeForm);
};
'''
main = r'''
int main(){
    int failures=0, cases=0;
    for(int from=0;from<4;++from) for(int to=0;to<4;++to){
        if(from==to) continue;
        Component components[6];
        AAureateWakePreviewActor actor;
        for(int i=0;i<4;++i) actor.Wings.Add(&components[i]);
        for(int i=4;i<6;++i){components[i].visible=from==1;actor.Hydrofoils.Add(&components[i]);}
        actor.CurrentForm=static_cast<EAureateWakeForm>(from);
        bool accepted=actor.RequestForm(static_cast<EAureateWakeForm>(to));
        bool expected=(from==1 || to==1);
        bool ok=accepted && actor.bTransitioning && components[4].visible==expected && components[5].visible==expected;
        ++cases;
        if(!ok){++failures;std::cout<<"FAIL foil visibility "<<from<<" -> "<<to<<"\n";}
    }
    std::cout<<cases<<" directed requests; "<<failures<<" failures. Isolated C++ method only; NOT Unreal verification.\n";
    return failures ? 1 : 0;
}
'''
with tempfile.TemporaryDirectory() as folder:
    cpp=Path(folder)/'probe.cpp'
    exe=Path(folder)/'probe'
    cpp.write_text(stub+method+main)
    subprocess.run(['g++','-std=c++17','-Wall','-Wextra',str(cpp),'-o',str(exe)],check=True)
    raise SystemExit(subprocess.run([str(exe)]).returncode)
