#!/bin/bash
#
#SBATCH --job-name=t_m_-1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=32
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
WORKDIR_R="/work/$SLURM_JOB_USER/node_folder"

mkdir -p "$WORKDIR_R"
mkdir -p "$WORKDIR_R/cache/cluster.klima.uni-bremen.de"


WORKDIR="/home/users/lschuster/Schuster_et_al_phd_paper_1_cluster/oggm_run_gdir_folder/node_folder"

echo "$WORKDIR"

ln -s /home/www/fmaussion "$WORKDIR_R/cache/cluster.klima.uni-bremen.de/~fmaussion"
ln -s /home/www/lschuster "$WORKDIR_R/cache/cluster.klima.uni-bremen.de/~lschuster"

#preprocessed directory in www

# Export the WORKDIR as environment variable so our script can use it to find its working directory.
export WORKDIR


# Use the local data download cache
export OGGM_DOWNLOAD_CACHE=/home/data/download
export OGGM_DOWNLOAD_CACHE_RO=1

# Run the actual job. The srun invocation starts it as individual step for slurm.
srun -n 1 -c "${SLURM_JOB_CPUS_PER_NODE}" singularity exec /home/users/lschuster/images/oggm_20220426.sif bash -s <<EOF
	set -e
    # Setup a fake home dir inside of our workdir, so we don't clutter the actual shared homedir with potentially incompatible stuff.
    export HOME="$WORKDIR_R/fake_home"
	#if [ $1 = "C1_C2" ] 
    #then
    #    mkdir "\$HOME"
    #fi
	# Create a venv that _does_ use system-site-packages, since everything is already installed on the container.
	# We cannot work on the container itself, as the base system is immutable.
    python3 -m venv --system-site-packages "$WORKDIR_R/oggm_env"
    source "$WORKDIR_R/oggm_env/bin/activate"
	# Make sure latest pip is installed
	pip install --upgrade pip setuptools
	# OPTIONAL: install another OGGM version
    # before strange pull request (https://github.com/OGGM/oggm/pull/1500)
    pip install --upgrade "git+https://github.com/OGGM/oggm.git@a3123b56b3b5bac964eaab7742aa73bc2507c067"
	#pip install --upgrade "git+https://github.com/OGGM/oggm.git@b0b4aae84a587c2f99cea2ba51bcb1342ef32f66"
	#pip install --upgrade "git+https://github.com/lilianschuster/massbalance-sandbox.git@d5c9d713af35fd724f21d98c67d28c5f598894a2"
    pip install --upgrade "git+https://github.com/lilianschuster/massbalance-sandbox.git@d310e7982521dace575a18160e1ebae9a8e15788"
    
    # the actual run
    python3 /home/users/lschuster/oggm_mb_sandbox_option_intercomparison/00_data_creating_scripts/x_C1_t_melt_-1_options_ref_glacier.py "C1_C2"
EOF

# Print a final message so you can actually see it being done in the output log.
echo "SLURM DONE"
