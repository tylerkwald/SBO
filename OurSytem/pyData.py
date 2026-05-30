import relap_py as rp


case = 'first'
#rp.run_case(case)
data, variables = rp.extract_data('dataPull.txt', case)

