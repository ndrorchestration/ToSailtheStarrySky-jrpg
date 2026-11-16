"""Source contracts for converter CLI and Unreal recorder."""
import ast, copy, json, subprocess, sys, tempfile, unittest
from pathlib import Path
from test_aureate_envelope_records import snapshot, LABELS
ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/"Tools"/"run_aureate_envelope_export_native.py"
REC=ROOT/"Tools"/"export_aureate_envelopes_native.py"
class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.p=Path(self.tmp.name)
        self.start=self.p/"start.json"; self.end=self.p/"end.json"; self.labels=self.p/"labels.json"; self.out=self.p/"result.json"
        self.start.write_text(json.dumps(snapshot())); self.end.write_text(json.dumps(snapshot()))
        self.labels.write_text(json.dumps({"start":LABELS,"end":LABELS}))
    def call(self,*extra):
        return subprocess.run([sys.executable,str(TOOL),"combine","--start",str(self.start),"--end",str(self.end),"--labels",str(self.labels),"--clearance","0","--output",str(self.out),*extra],capture_output=True,text=True)
    def test_valid_input_writes_source_only_result_with_provenance(self):
        r=self.call()
        self.assertEqual(r.returncode,0,r.stderr)
        d=json.loads(self.out.read_text()); self.assertEqual(d["verifier"]["verdict"],"CLEAR_UNDER_ENVELOPES")
        self.assertFalse(d["native_collision_verified"]); self.assertFalse(d["creator_approved"])
        self.assertEqual(len(d["snapshot_sha256"]["start"]),64)
    def test_does_not_overwrite_existing_output(self):
        self.out.write_text("KEEP"); r=self.call()
        self.assertNotEqual(r.returncode,0); self.assertEqual(self.out.read_text(),"KEEP")
    def test_invalid_snapshot_fails_without_output(self):
        d=snapshot(); d["actors"].append(copy.deepcopy(d["actors"][0])); self.start.write_text(json.dumps(d))
        self.assertNotEqual(self.call().returncode,0); self.assertFalse(self.out.exists())
    def test_collision_box_is_rejected_but_result_is_preserved(self):
        d=snapshot(); d["actors"][4]["position"]=list(d["actors"][0]["position"])
        self.start.write_text(json.dumps(d)); self.end.write_text(json.dumps(d))
        r=self.call()
        self.assertEqual(r.returncode,1,r.stderr)
        result=json.loads(self.out.read_text())
        self.assertEqual(result["verifier"]["verdict"],"REJECT_CLEARANCE_VIOLATION")
        self.assertFalse(result["native_collision_verified"])
    def test_moving_static_obstacle_is_rejected_without_output(self):
        d=snapshot(); d["actors"][0]["position"][0]=0.00000001
        self.end.write_text(json.dumps(d)); r=self.call()
        self.assertEqual(r.returncode,2); self.assertFalse(self.out.exists())
    def test_native_recorder_has_no_scene_mutation_calls(self):
        tree=ast.parse(REC.read_text())
        banned={"save_current_level","save_map","spawn_actor_from_class","set_actor_location","set_actor_rotation","set_actor_scale3d"}
        names={x.func.attr for x in ast.walk(tree) if isinstance(x,ast.Call) and isinstance(x.func,ast.Attribute)}
        self.assertFalse(names & banned,names & banned)


class RecorderExecutionTests(unittest.TestCase):
    def test_native_recorder_collects_local_bounds_and_component_transform(self):
        import hashlib, importlib.util, os, types
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); project=root/"project"; scenes=project/"Content/TSTSS/Review/Scenes"; scenes.mkdir(parents=True)
            (project/"AureateCinematicV4Sandbox.uproject").write_text(json.dumps({"Description":"AUREATE_CINEMATIC_V4_REVIEW_ONLY"}))
            m=scenes/"Test.umap"; m.write_bytes(b"map"); digest=hashlib.sha256(m.read_bytes()).hexdigest()
            v=lambda x,y,z:types.SimpleNamespace(x=x,y=y,z=z)
            class Mesh:
                def get_bounding_box(self): return types.SimpleNamespace(min=v(-1,-2,-3),max=v(3,4,5))
                def get_path_name(self): return "/Game/Mesh"
            class Component:
                def get_editor_property(self,name): return Mesh()
                def get_world_transform(self): return types.SimpleNamespace(translation=v(10,20,30),rotation=types.SimpleNamespace(x=0,y=0,z=0,w=1),scale3d=v(2,3,4))
            class Instanced(Component): pass
            class Actor:
                def get_actor_label(self): return "test_actor"
                def get_components_by_class(self,cls): return [Component()]
            class Level: pass
            class Actors: pass
            levels=types.SimpleNamespace(is_in_play_in_editor=lambda:False,load_level=lambda p:True)
            actors=types.SimpleNamespace(get_all_level_actors=lambda:[Actor()])
            fake=types.SimpleNamespace(StaticMeshActor=Actor,StaticMeshComponent=Component,StaticMesh=Mesh,InstancedStaticMeshComponent=Instanced,
                Paths=types.SimpleNamespace(project_dir=lambda:str(project)),SystemLibrary=types.SimpleNamespace(get_engine_version=lambda:"5.8.4"),
                LevelEditorSubsystem=Level,EditorActorSubsystem=Actors,
                EditorLoadingAndSavingUtils=types.SimpleNamespace(get_dirty_map_packages=lambda:[],get_dirty_content_packages=lambda:[]),
                get_editor_subsystem=lambda cls:levels if cls is Level else actors,log=lambda x:None)
            spec=importlib.util.spec_from_file_location("native_rec",REC); mod=importlib.util.module_from_spec(spec)
            out=root/"snapshot.json"
            env={"TSTSS_ENVELOPE_EXPORT_EXPLICIT":"1","TSTSS_ENVELOPE_MAP":"/Game/TSTSS/Review/Scenes/Test","TSTSS_ENVELOPE_MAP_SHA":digest,"TSTSS_ENVELOPE_OUTPUT":str(out),"TSTSS_ENVELOPE_FRAME":"shared"}
            with patch.dict(sys.modules,{"unreal":fake}), patch.dict(os.environ,env):
                spec.loader.exec_module(mod); mod.SANDBOX=project.resolve(); mod.main()
                row=json.loads(out.read_text())["actors"][0]
                self.assertEqual(row["bounds_min"],[-1,-2,-3]); self.assertEqual(row["position"],[10,20,30]); self.assertEqual(row["scale"],[2,3,4])
                with self.assertRaisesRegex(RuntimeError,"output path"): mod.main()

if __name__=="__main__": unittest.main()
