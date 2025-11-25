#!/bin/sh

export DETECTOR=epic
#export DETECTOR_PATH=/opt/software/linux-x86_64_v2/epic-main-eqytzhlyhxg44vvfvtv3lbzqb6uflyoh/share/epic
export DETECTOR_PATH=/home/amitbashyal/Documents/BNL-AiD2E/BIC-MOBO/share/epic
export DETECTOR_CONFIG=${1:-epic}
export DETECTOR_VERSION=25.11.0-9-g3b0f0be07

## Warn is not the right name (this script is sourced, hence $1)
if [[ "$(basename ${BASH_SOURCE[0]})" != "thisepic.sh" ]]; then
        echo "Warning: This script will cease to exist at '$(realpath --no-symlinks ${BASH_SOURCE[0]})'."
        echo "         Please use the version at '$(realpath --no-symlinks $(dirname ${BASH_SOURCE[0]})/bin/thisepic.sh)'."
fi

## Export detector libraries
if [[ "$(uname -s)" = "Darwin" ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        export DYLD_LIBRARY_PATH="/opt/software/linux-x86_64_v2/epic-main-eqytzhlyhxg44vvfvtv3lbzqb6uflyoh/lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
else
        export LD_LIBRARY_PATH="/opt/software/linux-x86_64_v2/epic-main-eqytzhlyhxg44vvfvtv3lbzqb6uflyoh/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi
