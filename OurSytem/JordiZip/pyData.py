import relap_py as rp


case = 'noTDPBatAC_orig'
#rp.run_case(case)
data, variables = rp.extract_data('dataPull.txt', case)

