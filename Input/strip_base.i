= stripf 
0000100 strip fmtout
101  run 
103  0 
*--------------------------------------------------------------------- 
*
*  LEVELS
*
1001 cntrlvar 21      * core level
1002 cntrlvar 22      * upper plenum level
1003 cntrlvar 23      * downcomer level
1004 cntrlvar 150     * pressurizer level
1005 cntrlvar 176     * SG intact DC level
1006 cntrlvar 276     * SG broken DC level
*
*  POWER
*
1007 rktpow 0         * core power
1008 cntrlvar 833     * PZR heaters power
*
*  RCP VELOCITIES
*
1009 pmpvel 113       * RCP intact loop
1010 pmpvel 209       * RCP broken loop
*
*  CLAD TEMPERATURES (axial nodes 1-12, surface point 17)
*
1011 httemp 336000117 
1012 httemp 336000217 
1013 httemp 336000317 
1014 httemp 336000417 
1015 httemp 336000517 
1016 httemp 336000617 
1017 httemp 336000717 
1018 httemp 336000817 
1019 httemp 336000917 
1020 httemp 336001017 
1021 httemp 336001117 
1022 httemp 336001217  * core exit clad temp (max)
*
*  PRESSURES
*
1023 p 150010000      * primary pressure (pressurizer)
1024 p 180010000      * secondary pressure intact SG
1025 p 280010000      * secondary pressure broken SG
*
*  PRIMARY TEMPERATURES
*
1026 tempf 340010000  * core inlet temperature (intact)
1027 tempg 340010000  * core inlet vapor temp (intact)
1028 tempf 330010000  * core outlet temperature
1029 tempg 330010000  * core outlet vapor temp
1030 tempf 100010000  * hot leg intact temperature
1031 tempf 270060000  * hot leg broken temperature
1032 tempf 114010000  * cold leg intact temperature
1033 tempf 210010000  * cold leg broken temperature
*
*  MASS FLOWS - PRIMARY CIRCUIT
*
1034 mflowj 200010000  * intact loop flow
1035 mflowj 100010000  * broken loop flow
*
*  MASS FLOWS - FEEDWATER AND AFW
*
1036 mflowj 181000000  * intact SG feedwater/AFW
1037 mflowj 281000000  * broken SG feedwater/AFW
1038 mflowj 183000000  * intact AFW motor-driven
1039 mflowj 283000000  * broken AFW motor-driven
1040 mflowj 473000000  * intact TDP (uncontrolled)
1041 mflowj 475000000  * broken TDP (uncontrolled)
*
*  MASS FLOWS - RCP SEAL LEAKS
*
1042 mflowj 506000000  * intact loop small seal leak
1043 mflowj 507000000  * broken loop small seal leak
1044 mflowj 508000000  * intact loop large seal leak
1045 mflowj 509000000  * broken loop large seal leak
*
*  MASS FLOWS - PZR RELIEF AND SAFETY VALVES
*
1046 mflowj 155000000  * PZR safety valve
1047 mflowj 157000000  * PZR relief valve (PORV)
*
*  MASS FLOWS - SG RELIEF VALVES
*
1048 mflowj 187000000  * intact SG relief valve
1049 mflowj 287000000  * broken SG relief valve
*
*  MASS FLOWS - HPSI AND LPSI (after AC recovery at 12h)
*
1050 mflowj 196000000  * intact LPSI
1051 mflowj 198000000  * intact HPSI
1052 mflowj 296000000  * broken LPSI
1053 mflowj 298000000  * broken HPSI
*
*  ACCUMULATOR LEVELS
*
1054 acvliq 190        * intact accumulator liquid volume
1055 acvliq 290        * broken accumulator liquid volume
*
*  INTEGRAL VARIABLES
*
1056 cntrlvar 500      * integral PZR PORV+safety mass flow
1057 cntrlvar 502      * integral ECCS mass flow
1058 cntrlvar 504      * integral RCP seal leak mass flow
.
