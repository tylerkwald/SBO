import relap_py as rp
import pandas as pd
import matplotlib.pyplot as plt

#case = 'reflood_trialsFlatProfile'
case = 'ss31'
#rp.run_case(case)
rp.set_figures_loc('./figures/')
nodes = [
    '1000110',
    '1000210',
    '1000310',
    '1000410',
    '1000510',
    '1000610',
    '1000710',
    '1000810',
    '1000910',
    '1001010',
    '1001110',
    '1001210',
    '1001310',
    '1001410',
    '1001510',
    '1001610',
    '1001710'
]

water_nodes = [
    1020000,
    1030000,
    1040000,
    1050000,
    1060000,
    1070000,
    1080000,
    1090000,
    1100000,
    1110000,
    1120000,
    1130000,
    1140000,
    1150000,
    1160000,
    1170000,
    1180000,
]
times = [30.,80.,120.,150.,180.,210.,240.,270.,300.,330.,360.,]
rp.plot_profile('httemp', nodes,times, case)
data, variables = rp.extract_data('dataPull.txt', case)
