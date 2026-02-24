## Instructions on instructoins_bnl.md is outdated.

## Merged panda-run branch with main (fork BIC-MOBO) and then merged Derek's post changes main into forked BIC-MOBO main

**Changes in files currently between panda-run and main of the forked repository**

```bash
(scheduler_epic) bash-5.1$ git diff panda-run main --stat
 AID2ETestTools/AxHelper.py                                |  196 +++++++++++++++++++++++++++++++++++++++++++++-----
 AID2ETestTools/__init__.py                                |    5 +-
 EICMOBOTestTools/AnaGenerator.py                          |   55 ++++++++++----
 EICMOBOTestTools/FileManager.py                           |   47 +++++++-----
 EICMOBOTestTools/GeometryEditor.py                        |  121 ++++++++++++++++++++++++++++++-
 EICMOBOTestTools/RecGenerator.py                          |   85 ++++++++++++++++++----
 EICMOBOTestTools/SimGenerator.py                          |   67 +++++++++++++++--
 EICMOBOTestTools/TrialManager.py                          |  132 ++++++++++++++++++++++++++++------
 EICMOBOTestTools/__init__.py                              |    3 +-
 ISSUES.md                                                 |   11 ---
 README.md                                                 |   96 ++++++++++++++++---------
 bin/this-mobo.csh                                         |   20 ++++++
 bin/this-mobo.sh                                          |   15 ++++
 bin/this-mobo.tcsh                                        |   20 ++++++
 bin/this-mobo.zsh                                         |   16 +++++
 configuration/objectives.config                           |    7 +-
 configuration/problem.config                              |   12 ++--
 configuration/run.config                                  |    3 +-
 configuration/template.slurm                              |    8 +++
 examples/objectives_extended.config                       |   21 ++++++
 {scripts => interfaces}/RunObjectives.py                  |   99 ++++++++++++++------------
 interfaces/__init__.py                                    |    5 ++
 launch-mobo                                               |   36 ++++++++++
 objectives/BICClustAngReso.py                             |  241 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 objectives/{BICEnergyResolution.py => BICClustEneReso.py} |   50 ++++++++-----
 objectives/BICHitAngReso.py                               |  453 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 panda-idds-bic-mobo-simple.py                             |  224 ---------------------------------------------------------
 run-analyses.py                                           |  848 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++---------------------------------
 run-bic-mobo.py                                           |  186 ++++++++++++++++++-----------------------------
 scripts/rerun-brut-analyses.py                            | 1045 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 scripts/run-mobo-en-brut.py                               |   31 ++++----
 setup.py                                                  |    2 +-
 tests/test-eic-tools.py                                   |   24 ++++---
 33 files changed, 3476 insertions(+), 708 deletions(-)
(scheduler_epic) bash-5.1$ 
```


# Clarification on initialization of the environment
```bash
    # Now need to initialize the environment for the Panda runner
    # setup_mamba contains ax related environment that might be neded during a PanDA job. 
    logging.info("Initializing the environment for the Panda runner")
    init_env = [
        "command -v singularity &> /dev/null || export SINGULARITY=/cvmfs/oasis.opensciencegrid.org/mis/singularity/current/bin/singularity;",
        "export AIDE_HOME=$(pwd);",
        "export AIDE_WORKDIR=$(pwd);",
        "export SIF=/cvmfs/singularity.opensciencegrid.org/eic/eic_ci:nightly;",
        "export DETECTOR_PATH=${SIF}/opt/detector/epic-main/share/epic;",
        "echo DETECTOR_PATH: ${DETECTOR_PATH};",
        "echo AIDE_HOME: ${AIDE_HOME};",
        "echo AIDE_WORKDIR: ${AIDE_WORKDIR};",
        # Also copy the epic files...
        "mkdir -p ${AIDE_WORKDIR}/share/epic;",
        "${SINGULARITY} exec --bind $(pwd):$(pwd) ${SIF} /bin/bash -c \"cp -RLrf /opt/detector/epic-main/share/epic/* \${AIDE_WORKDIR}/share/epic/\";",
        # Install micromamba (minimal)
        "export MAMBA_ROOT_PREFIX=${AIDE_WORKDIR}/micromamba;",
        "export MAMBA_EXE=${MAMBA_ROOT_PREFIX}/bin/micromamba;",
        "mkdir -p ${MAMBA_ROOT_PREFIX}/bin;",
        'curl -Ls https://micromamba.snakepit.net/api/micromamba/linux-64/latest | tar -xj -C ${MAMBA_ROOT_PREFIX} bin/micromamba;',
        "chmod a+rx ${MAMBA_ROOT_PREFIX};",
        "${MAMBA_EXE} config append --system channels conda-forge;",
        # Install Python 3.13
        "${MAMBA_EXE} install -y -r ${MAMBA_ROOT_PREFIX} -n base python=3.13;",
        "${MAMBA_EXE} clean -a -y;",
        # Activate micromamba and install packages via pip
        'eval "$(${MAMBA_EXE} shell hook -s posix)";',
        "micromamba activate base;",
        "pip install pandas seaborn botorch ax-platform==1.0.0 numpy matplotlib torch;",
        # Make sure to use mamba python
        'export PATH=${MAMBA_ROOT_PREFIX}/bin:$PATH;',
        #echo the python being used
        'echo "python version being used " $(python --version; which python);',
        # Singularity setup
        'export SINGULARITY_OPTIONS="--bind /cvmfs:/cvmfs,$(pwd):$(pwd)";',
        "export SIF=/cvmfs/singularity.opensciencegrid.org/eic/eic_ci:nightly;",
        "export SINGULARITY_BINDPATH=/cvmfs;",
        "env;"
    ]
    init_env = " ".join(init_env)

```
## Clarification based on section

```bash
        "export SIF=/cvmfs/singularity.opensciencegrid.org/eic/eic_ci:nightly;",
        "export DETECTOR_PATH=${SIF}/opt/detector/epic-main/share/epic;",
        "echo DETECTOR_PATH: ${DETECTOR_PATH};",
```

## Output from the panda log
```bash
DETECTOR_PATH: /cvmfs/singularity.opensciencegrid.org/eic/eic_ci:nightly/opt/detector/epic-main/share/epic
AIDE_HOME: /srv
AIDE_WORKDIR: /srv

```

## Running BIC-MOBO in eicsub01 machine (My documentation)
```bash
bash
conda activate scheduler_epic
source setup_panda_bnl.sh
python panda-idds-bic-mobo.py
```

This is because Derek had made some changes in the previous merge request for BIC-MOBO. I introduced those changes but I did not do the tests properly. 
Claude says the issue was because *AID2ETestTools/AxHelper.py* now returns *cfg_par, cfg_obj* instead of *cfg_par* only. 



