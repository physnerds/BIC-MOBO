import json
import os,sys
import AID2ETestTools as att
import EICMOBOTestTools as emt
import datetime,re

main_path, main_file = emt.SplitPathAndFile(
    os.path.realpath(__file__)
)

time = str(datetime.datetime.now())
time = re.sub(r'[.\-:\ ]', '', time)
tag = f"AxTrial{time}"


print ("Main path and file ", main_path, main_file)

run_path = main_path + "/configuration/run.config"
par_path = main_path + "/configuration/parameters.config"
obj_path = main_path + "/configuration/objectives.config"

cfg_run = emt.ReadJsonFile(run_path)
cfg_par = emt.ReadJsonFile(par_path)
det_path = cfg_run["det_path"]
print("Detector path from run config: ", det_path)

params = {}
for par_name, par_config in cfg_par["parameters"].items():
    params[par_name] = par_config.get("default", par_config.get("value", "0"))


trial = emt.TrialManager(
    run_path,
    par_path,
    obj_path
)

script, ofiles = trial.MakeTrialScript(params)
print("Printing the scripts and ofiles ", script,ofiles)

if not os.path.exists(script):
    raise FileNotFoundError(f"Script {script} not found!")
else:
    print(f"Script {script} found!")
    os.chmod(script, 0o755)
command = cfg_run["eic_shell"] + " -- " + script
print(f"Running command: {command}")