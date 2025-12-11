#!/usr/bin/env bash
set -euo pipefail

# Resolve the SIF path relative to this script.
SINGULARITY_CMD="${SINGULARITY:-/cvmfs/oasis.opensciencegrid.org/mis/singularity/current/bin/singularity}"
echo "Using Singularity command: ${SINGULARITY_CMD}" >&2
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIF_PATH="/cvmfs/singularity.opensciencegrid.org/eic/eic_ci:nightly"

# Ensure the current directory is/opt/spack/share/spack/setup-env.sh bound into the container.
#export APPTAINER_BINDPATH="${APPTAINER_BINDPATH:+${APPTAINER_BINDPATH},}${SCRIPT_DIR},${PWD}"
#bind with gpfs02 only in local machine
# if pwd has /gpfs02/ then bind /gpfs02 ...to keep run_singularity.sh work in rcf machines as well
if [[ "${PWD}" == /gpfs02/* ]]; then
    export APPTAINER_BINDPATH="${APPTAINER_BINDPATH:+${APPTAINER_BINDPATH},},/cvmfs,${PWD},/gpfs02"
fi

echo "Script args: $@" >&2

if [[ $# -gt 0 ]]; then
    ${SINGULARITY_CMD} exec "${SIF_PATH}" /bin/bash -lc "export PATH=$PATH:/opt/local/bin && exec \"\$@\"" bash "$@"
else
    ${SINGULARITY_CMD} exec "${SIF_PATH}" /bin/bash -lc "export PATH=$PATH:/opt/local/bin && exec /bin/bash"
fi

