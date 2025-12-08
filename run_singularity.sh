#!/usr/bin/env bash
set -euo pipefail

# Resolve the SIF path relative to this script.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#SIF_PATH="${SCRIPT_DIR}/epic-docker/eic_container_25.11.sif"
#SIF_PATH="${SCRIPT_DIR}/eic_ci/eic_ci_master.sif"
#SIF_PATH="/cvmfs/singularity.opensciencegrid.org/eicweb/eic_xl:25.11-stable"
SIF_PATH="/cvmfs/singularity.opensciencegrid.org/eic/eic_ci:nightly"

# Ensure the current directory is/opt/spack/share/spack/setup-env.sh bound into the container.
export APPTAINER_BINDPATH="${APPTAINER_BINDPATH:+${APPTAINER_BINDPATH},}${PWD}"

if [[ $# -gt 0 ]]; then
    singularity exec "${SIF_PATH}" /bin/bash -lc "export PATH=$PATH:/opt/local/bin && exec \"\$@\"" bash "$@"
else
    singularity exec "${SIF_PATH}" /bin/bash -lc "export PATH=$PATH:/opt/local/bin && exec /bin/bash"
fi
