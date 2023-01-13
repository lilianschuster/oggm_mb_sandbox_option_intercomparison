cluster = True
testing = False

### adapted script from http://localhost:6261/lab/tree/bayes_2022_cluster/freq_calib_ref_winter_mb_temp_b_opt.py

# calib = 'C3' #'calib_geod_opt_std_temp_b_0'
# calib = 'C1_C2' #calib_geod_opt_winter_mb_approx_std  # this also automatically calibrates calib_geod_opt_winter_mb_temp_b_0
# calib = 'C4'  #'calib_only_geod_temp_b_0_pf_cte_via_std' # updated medians!!!

# FIRST NEED TO UPDATE WINTER prcp regression
# for C5 (calib_only_geod_temp_b_0_pf_fit_via_winter_mb)

import sys
calib = str(sys.argv[1])

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
from MBsandbox.mbmod_daily_oneflowline import process_w5e5_data
from MBsandbox.help_func import (calibrate_to_geodetic_bias_winter_mb_different_temp_bias_fast,
                                 calibrate_to_geodetic_bias_quot_std_different_temp_bias)

log = logging.getLogger(__name__)

base_url = ('https://cluster.klima.uni-bremen.de/~oggm/gdirs/oggm_v1.4/'
            'L1-L2_files/elev_bands')
climate_type = 'W5E5'

# get the geodetic calibration data
pd_geodetic_all = utils.get_geodetic_mb_dataframe()
# pd_geodetic_all = pd.read_hdf(path_geodetic, index_col='rgiid')
pd_geodetic = pd_geodetic_all.loc[pd_geodetic_all.period == '2000-01-01_2020-01-01']


#pd_wgms_ref_glac_analysis = pd.read_csv('/home/lilianschuster/Schreibtisch/PhD/wgms_data_analysis/wgms_data_analysis.csv', index_col=[0])
#rgis_w_mb_profiles = pd_wgms_ref_glac_analysis[pd_wgms_ref_glac_analysis.MB_profile.dropna()].index
# wgms_data_stats_20220301.csv
oggm_updated = False
if oggm_updated:
    _, path = utils.get_wgms_files()
    pd_mb_overview = pd.read_csv(path[:-len('/mbdata')] + '/mb_overview_seasonal_mb_time_periods_20220301.csv',
                                 index_col='Unnamed: 0')
    pd_wgms_data_stats = pd.read_csv(path[:-len('/mbdata')] + '/wgms_data_stats_20220301.csv',
                                     index_col='Unnamed: 0')
else:
    fp = 'https://cluster.klima.uni-bremen.de/~lschuster/ref_glaciers/data/mb_overview_seasonal_mb_time_periods_20220301.csv'
    fp_stats = ('https://cluster.klima.uni-bremen.de/~lschuster/ref_glaciers' +
                '/data/wgms_data_stats_20220301.csv')
    #fp = utils.file_downloader('https://cluster.klima.uni-bremen.de/~lschuster/ref_glaciers' +
    #                       '/data/mb_overview_seasonal_mb_time_periods_20220301.csv')
    pd_mb_overview = pd.read_csv(fp, index_col='Unnamed: 0')
    #fp_stats = utils.file_downloader('https://cluster.klima.uni-bremen.de/~lschuster/ref_glaciers' +
    #                       '/data/wgms_data_stats_20220301.csv')
    pd_wgms_data_stats = pd.read_csv(fp_stats, index_col='Unnamed: 0')
# should have at least 5 annual MB estimates in the time period 1980-2019
# (otherwise can also not have MB profiles or winter MB!)
pd_wgms_data_stats = pd_wgms_data_stats.loc[pd_wgms_data_stats.len_annual_balance>=5]
# seasonal_mb_candidates = pd_wgms_data_stats.rgi_id.unique()
ref_candidates = pd_wgms_data_stats.rgi_id.unique()  # seasonal_mb_candidates 
# oggm.utils.get_ref_mb_glaciers_candidates()


# for tests
if testing:
    ref_candidates = ['RGI60-11.01450'] #rgis_w_mb_profiles #oggm.utils.get_ref_mb_glaciers_candidates()
# working_dir = utils.gettempdir(dirname='OGGM_seasonal_mb_calib', reset=True)
working_dir = os.environ['WORKDIR']  # $WORKDIR # utils.gettempdir(dirname='OGGM_seasonal_mb_calib', reset=False)

cfg.initialize()
cfg.PARAMS['use_multiprocessing'] = True
cfg.PATHS['working_dir'] = working_dir
cfg.PARAMS['hydro_month_nh'] = 1
cfg.PARAMS['hydro_month_sh'] = 1
cfg.PARAMS['continue_on_error'] = True

load = True
if load: # and calib == 'C1_C2': # in the other calib options 
    gdirs = workflow.init_glacier_directories(
                ref_candidates,
                from_prepro_level=2,
                prepro_border=10,
                prepro_base_url=base_url,
                prepro_rgi_version='62')
    t = workflow.execute_entity_task(tasks.compute_downstream_line, gdirs)
    t = workflow.execute_entity_task(tasks.compute_downstream_bedshape, gdirs)
    #if baseline_climate == 'W5E5':
    #if mb_type != 'mb_monthly':
    t = workflow.execute_entity_task(process_w5e5_data, gdirs, climate_type=climate_type,
                                     temporal_resol='daily')
    t = workflow.execute_entity_task(process_w5e5_data, gdirs, climate_type=climate_type,
                                     temporal_resol='monthly')
    #else:
    #t = workflow.execute_entity_task(process_w5e5_data, gdirs, climate_type=baseline_climate,
    #                              temporal_resol='monthly')
    #else:
    #t = workflow.execute_entity_task(process_w5e5_data, gdirs, climate_type=baseline_climate,
    #                          temporal_resol='daily')
    #t = workflow.execute_entity_task(process_era5_daily_data, gdirs, #climate_type=baseline_climate,
                              #temporal_resol='daily'process_era5_daily_data(gd)
    #                                )
else:
    pass

###  '_pf_via_winter_mb_log_fit'
# output_file:
if cluster:
    path_calib_data = '/home/users/lschuster/Schuster_et_al_phd_paper_1_cluster/oggm_run_gdir_folder'
    # '/home/users/lschuster/bayes_2022_cluster/cluster_freq_per_glacier_calib_data'
else:
    path_calib_data = '/home/lilianschuster/Schreibtisch/PhD/Schuster_et_al_phd_paper_1/data/per_glacier_calib_data'

if calib == 'C1_C2': #calib_geod_opt_winter_mb_approx_std':
    # It makes only sense for those glaciers where we have at least 5 winter MB !!!
    ref_candidates_winter_mb = pd_mb_overview.loc[pd_mb_overview['at_least_5_winter_mb']].rgi_id.unique()    
    ref_candidates = ref_candidates_winter_mb #[]
    # this was just to reduce the number of glaciers that we look into,
    # if some already got computed ... 
    
    #ref_candidates_l = []
    #for rgi in ref_candidates_winter_mb:
    #    try:
    #       # this is just to reduce the number of glaciers that we look into,
    #       # but actually it is not really necessary 
    #        calib_t = 'calib_winter_mb_monthly_melt_f_update'
    #        p = f'{path_calib_data}/{calib_t}_{rgi}_methodpre-check.csv'
    #        pd.read_csv(p)
    #    except:
    #        ref_candidates_l.append(rgi)
    #print('amount of glaciers that need recalibration:')
    #print(len(ref_candidates_l))
    #print(ref_candidates)
    #ref_candidates = ref_candidates_l

gdirs = workflow.init_glacier_directories(
                ref_candidates)


# takes a bit long -> will be optimised later!
method = 'pre-check'
start = time.time()




# C1 & C2
if calib == 'C1_C2': #calib_geod_opt_winter_mb_approx_std':
    # calib_geod_opt_winter_mb_approx_std and calib_geod_opt_winter_mb_temp_b_0
    # this has to be done on the cluster because it takes otherwise too long!
    # gdirs = workflow.init_glacier_directories(
    #        missing_rgi_winter_mb[n*16:(n+1)*16])
    temp_b_range = np.arange(-8,8,0.25)
    print(temp_b_range)
    
    for three_step_calib_sfc_type_distinction in [False, True]: #[False, True]:
        workflow.execute_entity_task(calibrate_to_geodetic_bias_winter_mb_different_temp_bias_fast,
                                     gdirs,
                                     temp_b_range=temp_b_range,
                                     method=method, 
                                     sfc_type_distinction=three_step_calib_sfc_type_distinction,                                                                  path=path_calib_data)
    
    
### C3
if calib == 'C3':  #calib_geod_opt_std_temp_b_0':
    options = [{'sfc_type_distinction':False,'melt_f_update': np.NaN, 'optimize_std_quot':True},
               {'sfc_type_distinction':True,'melt_f_update':'annual',  'optimize_std_quot':True},
               {'sfc_type_distinction':True,'melt_f_update': 'monthly',  'optimize_std_quot':True}]
    print(len(gdirs))
    for opt in options:
        workflow.execute_entity_task(calibrate_to_geodetic_bias_quot_std_different_temp_bias, gdirs,
                                     sfc_type_distinction=opt['sfc_type_distinction'],                                                      temp_b_range=[0],
                                     optimize_std_quot=opt['optimize_std_quot'],
                                     melt_f_update=opt['melt_f_update'], method='pre-check',
                                     path=path_calib_data)

# todo: need to have a script that creates the necessary file 
### C4
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
                                     sfc_type_distinction=opt['sfc_type_distinction'],                                                      temp_b_range=[0],
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
                                     sfc_type_distinction=opt['sfc_type_distinction'],                                                      temp_b_range=[0],
                                     optimize_std_quot=opt['optimize_std_quot'],
                                     melt_f_update=opt['melt_f_update'], method='pre-check',
                                     pf_cte_via='_pf_via_winter_mb_log_fit',
                                     path=path_calib_data,
                                     path_w_prcp = f'{path_calib_data}/')


