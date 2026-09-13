import asyncio, json, sys, hashlib
from pathlib import Path
sys.path.insert(0, "/usr/local/lib/hermes-agent")
from dotenv import load_dotenv
load_dotenv("/root/.hermes/.env")
from tools.vision_tools import vision_analyze_tool, check_vision_requirements
from hermes_cli.config import load_config
from agent.auxiliary_client import set_runtime_main, resolve_vision_provider_client
root=Path(__file__).resolve().parents[2]
async def main():
    cfg=load_config()
    meta={"configured_vision":{k:v for k,v in cfg.get("auxiliary",{}).get("vision",{}).items() if k in ("provider","model","timeout")},"default_requirements":check_vision_requirements()}
    # Child Python does not inherit Hermes runtime context; mirror this task session, not CLI default DeepSeek. No persistent config edits.
    set_runtime_main("openai","gpt-6-astra")
    route,client,model=resolve_vision_provider_client()
    meta.update(runtime_requirements=check_vision_requirements(),runtime_route=route,runtime_model=model,client_available=client is not None)
    (root/"docs/node2-s132/capability.json").write_text(json.dumps(meta,indent=2)+chr(10))
    print(json.dumps(meta),flush=True)
    paths=sys.argv[1:] or ["evidence/arena/n2-s132-720p/overview.png"]
    async def inspect(rel):
        p=root/rel
        question="Inspect these actual renderer pixels critically. Assess perspective/3D depth cues, differently lit faces, visible ground contact, arena legibility, blue/red actor silhouettes, airborne amber cube readability and clipping. State concrete visible observations and limitations. Do not infer motion, physics, combat, audio, or acceptance from a still image. If pixels are unavailable say so."
        result=await vision_analyze_tool(str(p),question)
        record={"image":rel,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"question":question,"response":json.loads(result)}
        dest=root/"docs/node2-s132"/(p.parent.name+"-"+p.stem+"-vision.json")
        dest.write_text(json.dumps(record,indent=2)+chr(10))
        print(json.dumps(record,indent=2),flush=True)
        return record["response"].get("success",False)
    for offset in range(0,len(paths),4):
        passed=await asyncio.gather(*(inspect(rel) for rel in paths[offset:offset+4]))
        if not all(passed): break
asyncio.run(main())
