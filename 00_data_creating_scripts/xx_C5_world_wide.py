### this does not work because calibrate_to_geodetic_bias_quot_std_different_temp_bias only works for reference glaciers
# would need to do some substantial changes to allow that, probably just copying calibrate_to_geodetic_bias_quot_std_different_temp_bias
# and then adapting it until it works ... 


cluster = True
testing = False

### adapted script from http://localhost:6261/lab/tree/bayes_2022_cluster/freq_calib_ref_winter_mb_temp_b_opt.py

# calib = 'C3' #'calib_geod_opt_std_temp_b_0'
# calib = 'C1_C2' #calib_geod_opt_winter_mb_approx_std  # this also automatically calibrates calib_geod_opt_winter_mb_temp_b_0
# calib = 'C4'  #'calib_only_geod_temp_b_0_pf_cte_via_std' # updated medians!!!

# FIRST NEED TO UPDATE WINTER prcp regression
# for C5 (calib_only_geod_temp_b_0_pf_fit_via_winter_mb)

import sys
rgi_reg = str(sys.argv[1])
calib = 'C5' #str(sys.argv[1])

import os 
import warnings
warnings.filterwarnings("once", category=DeprecationWarning)  
import scipy
import json
import time
import logging

# imports from OGGM
import oggm
from oggm import utils, workflow, tasks, cfg, entity_task
import numpy as np
import pandas as pd
# imports from MBsandbox
import MBsandbox
import geopandas as gpd
from MBsandbox.mbmod_daily_oneflowline import process_w5e5_data
from MBsandbox.help_func import (calibrate_to_geodetic_bias_winter_mb_different_temp_bias_fast,
                                 calibrate_to_geodetic_bias_quot_std_different_temp_bias)

log = logging.getLogger(__name__)

cfg.initialize()
cfg.PARAMS['use_multiprocessing'] = True
cfg.PARAMS['hydro_month_nh'] = 1
cfg.PARAMS['hydro_month_sh'] = 1
cfg.PARAMS['continue_on_error'] = True

base_url = ('https://cluster.klima.uni-bremen.de/~oggm/gdirs/oggm_v1.4/'
            'L1-L2_files/elev_bands')
climate_type = 'W5E5'

# Local working directory (where OGGM will write its output)
WORKING_DIR = os.environ.get('OGGM_WORKDIR', '')
if not WORKING_DIR:
    raise RuntimeError('Need a working dir')
utils.mkdir(WORKING_DIR)
cfg.PATHS['working_dir'] = WORKING_DIR

OUTPUT_DIR = os.environ.get('OGGM_OUTDIR', '')
if not OUTPUT_DIR:
    raise RuntimeError('Need an output dir')
utils.mkdir(OUTPUT_DIR)

rgi_version = '62'
rgi_ids = gpd.read_file(utils.get_rgi_region_file(rgi_reg, version=rgi_version))
if rgi_reg == '05':
    log.workflow('Remove connectivity 2 glaciers')
    rgi_ids = rgi_ids.loc[(rgi_ids['Connect'] == 0) | (rgi_ids['Connect'] ==1)]




load = True
if load: # and calib == 'C1_C2': # in the other calib options 
    gdirs = workflow.init_glacier_directories(
                rgi_ids,
                from_prepro_level=2,
                prepro_border=10,
                prepro_base_url=base_url,
                prepro_rgi_version='62')
    t = workflow.execute_entity_task(tasks.compute_downstream_line, gdirs)
    t = workflow.execute_entity_task(tasks.compute_downstream_bedshape, gdirs)
    t = workflow.execute_entity_task(process_w5e5_data, gdirs, climate_type=climate_type,
                                     temporal_resol='daily')
    t = workflow.execute_entity_task(process_w5e5_data, gdirs, climate_type=climate_type,
                                     temporal_resol='monthly')

else:
    pass

###  '_pf_via_winter_mb_log_fit'
# output_file:
path_calib_data = '/home/users/lschuster/Schuster_et_al_phd_paper_1_cluster/oggm_run_gdir_folder'


if calib == 'C4': #'calib_only_geod_temp_b_0_pf_cte_via_std':
    # calib_only_geod_temp_b_0_pf_cte_via_std
    ### IMPORTANT -> this has to be the updated file
    #http://localhost:6261/lab/tree/Schuster_et_al_phd_paper_1_cluster/freq_5calib_options_ref_glaciers.py
    with open(f"{path_calib_data}/pf_cte_median_dict_std_quot_temp_b_0.json", "r") as outfile:
        pf_cte_dict_std_quot_temp_b_0 = json.load(outfile)
    #else:
        # I just copied it (it is created inside http://localhost:8889/lab/tree/Schreibtisch/PhD/Schuster_et_al_phd_paper_1/analysis_notebooks/frequentist_ref_glacier_distribution_performance.ipynb ) 
        
    #with open("/home/users/lschuster/bayes_2022_cluster/cluster_freq_per_glacier_calib_data/pf_cte_median_dict_std_quot_temp_b_0.json", "r") as outfile:
    #        pf_cte_dict_std_quot_temp_b_0 = json.load(outfile)

    options = [{'sfc_type_distinction':False,'melt_f_update': np.NaN, 'optimize_std_quot':False},
               {'sfc_type_distinction':True,'melt_f_update':'annual',  'optimize_std_quot':False},
               {'sfc_type_distinction':True,'melt_f_update': 'monthly',  'optimize_std_quot':False}]
    for opt in options:
        print(opt)
        workflow.execute_entity_task(calibrate_to_geodetic_bias_quot_std_different_temp_bias, gdirs,
                                     sfc_type_distinction=opt['sfc_type_distinction'], temp_b_range=[0],
                                     optimize_std_quot=opt['optimize_std_quot'],
                                     melt_f_update=opt['melt_f_update'], method='pre-check',
                                     pf_cte_dict=pf_cte_dict_std_quot_temp_b_0,
                                     pf_cte_via='_pf_cte_via_std',
                                     path=path_calib_data)


### IMPORTANT: needs updated file with winter MB regression !!!
# C5
if calib == 'C5': #'calib_only_geod_temp_b_0_pf_fit_via_winter_mb':
    options = [{'sfc_type_distinction':False, 'melt_f_update': np.NaN, 'optimize_std_quot':False},
               {'sfc_type_distinction':True, 'melt_f_update':'annual', 'optimize_std_quot':False},
               {'sfc_type_distinction':True, 'melt_f_update': 'monthly', 'optimize_std_quot':False}]
    for opt in options:
        workflow.execute_entity_task(calibrate_to_geodetic_bias_quot_std_different_temp_bias, gdirs,
                                     sfc_type_distinction=opt['sfc_type_distinction'], temp_b_range=[0],
                                     optimize_std_quot=opt['optimize_std_quot'],
                                     melt_f_update=opt['melt_f_update'], method='pre-check',
                                     pf_cte_via='_pf_via_winter_mb_log_fit',
                                     path=OUTPUT_DIR,
                                     path_w_prcp = f'{path_calib_data}/')


log.workflow('OGGM Done')