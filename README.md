# oggm_mb_sandbox_option_intercomparison

scripts to reproduce figures and analysis of [Schuster et al. (2023), doi: 10.1017/aog.2023.57](https://doi.org/10.1017/aog.2023.57).

The scripts work together with the [OGGM development version 1.5.4.dev60+g9d17303](https://github.com/OGGM/oggm/commit/9d173038862f36a21838034da07243bd189ef2d0) and this [OGGM massbalance-sandbox commit](https://github.com/OGGM/massbalance-sandbox/tree/3c46e97effa1632c920661000541d132afba7619). Installing them can be done by e.g.:

    $ pip install --no-deps "git+https://github.com/OGGM/oggm.git@9d173038862f36a21838034da07243bd189ef2d0"
    $ pip install --no-deps "git+https://github.com/OGGM/massbalance-sandbox.git@3c46e97effa1632c920661000541d132afba7619"

- In `00_data_creating_scripts/`, you can find the scripts to create the data and to postprocess them. The actual data is publicly available via Zenodo: https://doi.org/10.5281/zenodo.7660887

- In `analysis_notebooks/`, you can find all the juypter notebooks that were used to create figures for the paper and the supplementary material. There are also some additional plots and analysis that were used to do statements without figures in the text. 


---
**When using the code, please refer to the below original publication in addition to this repository:**
- Schuster L, Rounce DR, Maussion F. Glacier projections sensitivity to temperature-index model choices and calibration strategies. Annals of Glaciology. 2023:1-16. [doi:10.1017/aog.2023.57](https://doi.org/10.1017/aog.2023.57)
---

If you have questions, don't hesitate to contact me via writing an issue or an email to lilian.schuster@uibk.ac.at. 
