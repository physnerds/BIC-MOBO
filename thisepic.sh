#!/bin/sh

export DETECTOR=epic
#export DETECTOR_PATH=/opt/detector/epic-main/share/epic
export DETECTOR_PATH=${PWD}/share/epic
export DETECTOR_CONFIG=${1:-epic}
export DETECTOR_VERSION=25.12.0-3-gdf5195a2f

## Warn is not the right name (this script is sourced, hence $1)
if [[ "$(basename ${BASH_SOURCE[0]})" != "thisepic.sh" ]]; then
        echo "Warning: This script will cease to exist at '$(realpath --no-symlinks ${BASH_SOURCE[0]})'."
        echo "         Please use the version at '$(realpath --no-symlinks $(dirname ${BASH_SOURCE[0]})/bin/thisepic.sh)'."
fi

## Export detector libraries
if [[ "$(uname -s)" = "Darwin" ]] || [[ "$OSTYPE" == "darwin"* ]]; then
        export DYLD_LIBRARY_PATH="/opt/software/linux-x86_64_v2/epic-git.df5195a2f85e7cf63ec69b81b40fbca774010f83_main-2wzfab2p3w3qvasjgrh4t43t4aem3asx/lib${DYLD_LIBRARY_PATH:+:$DYLD_LIBRARY_PATH}"
else
        export LD_LIBRARY_PATH="/opt/software/linux-x86_64_v2/epic-git.df5195a2f85e7cf63ec69b81b40fbca774010f83_main-2wzfab2p3w3qvasjgrh4t43t4aem3asx/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
fi