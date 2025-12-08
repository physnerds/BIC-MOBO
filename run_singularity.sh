#!/usr/bin/env bash
set -euo pipefail

# Resolve the SIF path relative to this script.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SIF_PATH="/cvmfs/singularity.opensciencegrid.org/eic/eic_ci:nightly"

# Ensure the current directory is/opt/spack/share/spack/setup-env.sh bound into the container.
#export APPTAINER_BINDPATH="${APPTAINER_BINDPATH:+${APPTAINER_BINDPATH},}${SCRIPT_DIR},${PWD}"
export APPTAINER_BINDPATH="${APPTAINER_BINDPATH:+${APPTAINER_BINDPATH},}/gpfs02"
echo "Script args: $@" >&2

if [[ $# -gt 0 ]]; then
    singularity exec "${SIF_PATH}" /bin/bash -lc "export PATH=$PATH:/opt/local/bin && exec \"\$@\"" bash "$@"
else
    singularity exec "${SIF_PATH}" /bin/bash -lc "export PATH=$PATH:/opt/local/bin && exec /bin/bash"
fi

#if [[ $# -gt 0 ]]; then
#   singularity exec "${SIF_PATH}" /bin/bash -lc "source /opt/spack/share/spack/setup-env.sh && exec \"\$@\"" bash "$@"
#else
#   singularity exec "${SIF_PATH}" /bin/bash -lc "source /opt/spack/share/spack/setup-env.sh && exec /bin/bash"
#fi
