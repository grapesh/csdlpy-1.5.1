#!/bin/bash

## Load Python 2.7.13
#module use /usrx/local/dev/modulefiles
#module load python/2.7.13

export pyPath="/Users/svinogra/anaconda/bin"
export platform="/Users/svinogra/mirrors/wcoss/surge"

export myModules=${platform}"/gpfs/hps3/nos/noscrub/nwprod/csdlpy-1.5.1"
export pythonCode=${platform}"/gpfs/hps3/nos/noscrub/nwprod/csdlpy-1.5.1/csdlpy/etss/etss.py"

#export ofsDir=${platform}"/gpfs/hps/nco/ops/com/estofs/prod/"
#export stormCycle="2018111701" #"latest"

cd ${tmpDir}
PYTHONPATH=${myModules} ${pyPath}/python -W ignore ${pythonCode}
