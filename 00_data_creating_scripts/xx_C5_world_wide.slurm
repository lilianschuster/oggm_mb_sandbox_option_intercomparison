#!/bin/bash
#
#SBATCH --job-name=world_C5
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=64
#SBATCH --time=48:00:00
#SBATCH --mail-user=lilian.schuster@student.uibk.ac.at
#SBATCH --mail-type=ALL
#SBATCH --qos=normal

# Abort whenever a single step fails. Without this, bash will just continue on errors.
set -e

# Load the required environment modules for OGGM
module load oggm-binary-deps/4 python/3.8 
# Activate our local OGGM virtualenv
# source ~/oggm_env/bin/activate
# source ./oggm_venv/bin/activate
# On every node, when slurm starts a job, it will make sure the directory
# /work/username exists and is writable by the jobs user.
# We create a sub-directory there for this job to store its runtime data at.
echo "Recreate new preprocessed gdirs"
echo "$SLURM_JOB_USER"

OGGM_WORKDIR="/work/$SLURM_JOB_USER/node_folder"

mkdir -p "$OGGM_WORKDIR"
mkdir -p "$OGGM_WORKDIR/cache/cluster.klima.uni-bremen.de"
OGGM_WORKDIR="/work/$SLURM_JOB_USER/node_folder"
echo "$OGGM_WORKDIR"
mkdir -p "$OGGM_WORKDIR"
echo "$OGGM_WORKDIR"

ln -s /home/www/fmaussion "$OGGM_WORKDIR/cache/cluster.klima.uni-bremen.de/~fmaussion"
ln -s /home/www/lschuster "$OGGM_WORKDIR/cache/cluster.klima.uni-bremen.de/~lschuster"

#preprocessed directory in www

# Export the OGGM_WORKDIR as environment variable so our script can use it to find its working directory.
export OGGM_WORKDIR


# Use the local data download cache
export OGGM_DOWNLOAD_CACHE=/home/data/download
export OGGM_DOWNLOAD_CACHE_RO=1
export OGGM_EXTRACT_DIR="/work/$SLURM_JOB_USER/$SLURM_JOB_ID/oggm_tmp"
export OGGM_USE_MULTIPROCESSING=1

# Add other useful defaults
export LRU_MAXSIZE=1000

OGGM_OUTDIR="/work/$SLURM_JOB_USER/$SLURM_JOB_ID/out"
export OGGM_OUTDIR
echo "Output dir for this run: $OGGM_OUTDIR"

# Try to make mp better
# export OGGM_USE_MP_SPAWN=1

# Run the actual job. The srun invocation starts it as individual step for slurm.
srun -n 1 -c "${SLURM_JOB_CPUS_PER_NODE}" singularity exec /home/users/lschuster/images/oggm_20220426.sif bash -s <<EOF
	set -e
    # Setup a fake home dir inside of our OGGM_WORKDIR, so we don't clutter the actual shared homedir with potentially incompatible stuff.
    export HOME="$OGGM_WORKDIR/fake_home"
	if [ $1 = "C1_C2" ] 
    then
        mkdir "\$HOME"
    fi
	# Create a venv that _does_ use system-site-packages, since everything is already installed on the container.
	# We cannot work on the container itself, as the base system is immutable.
    python3 -m venv --system-site-packages "$OGGM_WORKDIR/oggm_env"
    source "$OGGM_WORKDIR/oggm_env/bin/activate"
	# Make sure latest pip is installed
	pip install --upgrade pip setuptools
	# OPTIONAL: install another OGGM version
    # before strange pull request (https://github.com/OGGM/oggm/pull/1500)
    pip install --upgrade "git+https://github.com/OGGM/oggm.git@a3123b56b3b5bac964eaab7742aa73bc2507c067"
	#pip install --upgrade "git+https://github.com/OGGM/oggm.git@b0b4aae84a587c2f99cea2ba51bcb1342ef32f66"
	#pip install --upgrade "git+https://github.com/lilianschuster/massbalance-sandbox.git@d5c9d713af35fd724f21d98c67d28c5f598894a2"
    pip install --upgrade "git+https://github.com/lilianschuster/massbalance-sandbox.git@3c46e97effa1632c920661000541d132afba7619"
    # d310e7982521dace575a18160e1ebae9a8e15788"
    #
    # the actual run
    python3 /home/users/lschuster/oggm_mb_sandbox_option_intercomparison/00_data_creating_scripts/xx_C5_world_wide.py $1
EOF


echo "Copying files..."
# Once a slurm job is done, slurm will clean up the /work directory on that node from any leftovers from that user.
# So copy any result data you need from there back to your home dir!
# $SLURM_SUBMIT_DIR points to the directory from where the job was initially commited.
# Copy any neccesary result data (here basically the per_glacier stuff that we need.
OUTDIR=/home/users/lschuster/oggm_mb_sandbox_option_intercomparison/oggm_run_gdir_folder/xx_worldwide_test
#cp -R "${OGGM_WORKDIR}" 
rsync -avzh "$OGGM_OUTDIR/" "${OUTDIR}/"
rsync -avzh "$OGGM_WORKDIR/" "${OUTDIR}/"



# Print a final message so you can actually see it being done in the output log.
echo "SLURM DONE"



#####################

