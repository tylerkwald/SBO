= SBO_exercise
100 restart transnt
101 run
103 0 * restart block
*
201  2000.0    1.0-7   0.1   3    50     50000  50000
*
*
*****************************************************************************************************
*
*  Variables of interest
*
*****************************************************************************************************{{{
*  what      where        variable
*-----------------------------------------------
*  level     core         cntrlvar-021  
*  level     UpperPlenum  cntrlvar-022  
*  level     Downcomer    cntrlvar-023  
*  level     Pressurizer  cntrlvar-150  
*  level     SGIntactDC   cntrlvar-176  
*  level     SGbrokenDC   cntrlvar-276  
*  power     core         rktpow-0      
*  power     PZRheaters   cntrlvar-833
*  velocity  RCPIntact    pmpvel-113
*  velocity  RCPBroken    pmpvel-209
*  cladtemp  core         httemp-336000117 to httemp-336001217
*
*-----------------------------------------------
* Integral of Pressurizer and safety valve mass flow
20550000 PZRporvs  sum 1.0  0.0     1     0
*                   a0         scale     name         param
20550001           0.0        1.0      mflowj     155000000
20550002                      1.0      mflowj     157000000
*
20550100   PZRporvs   integral    1.0         0.0         1
20550101             cntrlvar    500
*-----------------------------------------------
* Integral of ECCS mass flow
20550200 PZRporvs  sum 1.0  0.0     1     0
*                   a0         scale     name         param
20550201           0.0        1.0      mflowj     190010000
20550202                      1.0      mflowj     290010000
20550203                      1.0      mflowj     196000000
20550204                      1.0      mflowj     198000000
20550205                      1.0      mflowj     296000000
20550206                      1.0      mflowj     298000000
*
20550300   PZRporvs   integral    1.0         0.0         1
20550301             cntrlvar    502
*-----------------------------------------------
* Integral of RCP seal break mass flow
20550400 PZRporvs  sum 1.0  0.0     1     0
*                   a0         scale     name         param
20550401           0.0        1.0      mflowj     506000000
20550402                      1.0      mflowj     507000000
*
20550500   PZRporvs   integral    1.0         0.0         1
20550501             cntrlvar    504
*}}}
*****************************************************************************************************
*
*  SCRAM and other signals
*****************************************************************************************************{{{
*
*            Analogical trips
*-----------------------------------------------------------------------
*      var     param  r       var      param       acon l
*-----------------------------------------------------------------------
452   time         0 ge      null          0   1.0e3     l * SBO starting time
501      p 150010000 le      null          0  1.2824e+7  l * scram signal
505      p 150010000 le      null          0 1.226998e7  l * safety injection signal
455 httemp 336001017 ge      null          0 1700.0      n * stop the case
504   time         0 le      null          0   0.0       n
600  455
*
*                         Logicla trips
*-----------------------------------------------------------------------
*           trip1          oper         trip2             l
*-----------------------------------------------------------------------
610          -501            or           501             n * always true
611          -501           and           501             n * always false
691          -750           and          -750             n * not SCRAM
750           501            or           452             n * SCRAM
*
*}}}
*****************************************************************************************************
*
*  PZR relief valve (to containment)
*****************************************************************************************************{{{
*
508      p 150010000 ge      null          0 1.620268e7       n * PZR relief setpoint
509      p 150010000 ge      null          0 1.606478e7       n * PZR relief setpoint
462  time          0 gt      null          0 1.0e9            l * open PZR relief valve as manual action
463  time          0 gt      null          0 1.0e9            l * open PZR relief valve at time
464  time          0 lt    timeof        604 30.0             n * close PZR relief valve after time
465 acvliq       290 le      null          0 -1.0             n * close PZR relief valve when Acc volume is low 
*
601           603           and           509                 n 
602           601            or           508                 n
603           602           and           509                 n * automatic
604           462            or           463                 n * PZR relief manual opening
605           464            or          -465                 n * PZR relief manual closing
606           604           and           605                 n * PZR relief manual opening/closing
607           603            or           606                 n * PZR relief all
*
*                name          type
1570000        "porv"         valve
*                from            to          area
1570101     158010001     150010001        1.70966e-2
*           fwd. loss     rev. loss       efvcahs
1570102           0.0           0.0           100
*           discharge       thermal       
1570103           1.0          0.14
*                flow            vl            vv        unused
1570201             0           0.0           0.0           0.0
*                type
1570300        trpvlv
*                trip
1570301           607
*
*                name          type
1580000        "cont"       tmdpvol
*                area        length           vol
1580101      92.90304        0.3048           0.0
*            az-angle     inc-angle            dz
1580102           0.0           0.0           0.0
*             x-rough          x-hd         flags
1580103           0.0           0.0             0
*               cword
1580200             4
*                srch         press          temp         squal
1580201           1.0    1.013529e5       305.372           1.0
*
*}}}
*****************************************************************************************************
*
*   RCP trip
*****************************************************************************************************{{{
*
715           511           or         511  n * RCP trip 511=normal operation actuation
716           512           or         512  n * RCP trip 512=normal operation actuation
*}}}
*****************************************************************************************************
*
*  PZR safety valve (to containment)
*
*****************************************************************************************************{{{
*
*
460      p 150010000 ge      null          0 1.720268e7 n * PZR safety setpoint
461      p 150010000 ge      null          0 1.706478e7 n * PZR safety setpoint
*
711           713           and           461             n
712           711            or           460             n
713           712           and           461             n * PZR relief
*
*                name          type
1550000        "porv"         valve
*                from            to          area
1550101     156010001     150010001    1.70966e-2
*           fwd. loss     rev. loss       efvcahs
1550102           0.0           0.0           100
*           discharge       thermal       
1550103           1.0          0.14
*                flow            vl            vv        unused
1550201             0           0.0           0.0           0.0
*                type
1550300        trpvlv
*                trip
1550301           713
*
*                name          type
1560000        "cont"       tmdpvol
*                area        length           vol
1560101      92.90304        0.3048           0.0
*            az-angle     inc-angle            dz
1560102           0.0           0.0           0.0
*             x-rough          x-hd         flags
1560103           0.0           0.0             0
*               cword
1560200             4
*                srch         press          temp         squal
1560201           1.0    1.013529e5       305.372           1.0
*
*}}}
*****************************************************************************************************
*
*  Auxiliary Feedwater
*****************************************************************************************************{{{
*
515   time         0 ge    timeof        750 30.0 l * AFW signal with delay
*
*                name          type
1830000    "iauxfeed"       tmdpjun
*                from            to          area       jefvcahs
1830101     184010001     174010001    0.20512991             
*             control          trip         alpha           num
1830200             1          515  cntrlvar           176
*                srch           mfl           mfv        unused
1830201          -1.0           0.0           0.0           0.0
1830202           0.0          37.5    0.0           0.0
1830203           0.1          37.5    0.0           0.0
1830204           7.7          37.5    0.0           0.0
1830205          8.15           0.0           0.0           0.0
*
*                name          type
1840000    "iauxfeed"       tmdpvol
*                area        length           vol
1840101     278.70912        0.3048           0.0
*            az-angle     inc-angle            dz
1840102           0.0           0.0           0.0
*             x-rough          x-hd         flags
1840103           0.0         15.24             0
*               cword
1840200             3
*                srch         press          temp
1840201           0.0    4.853909e6       310.928
*
*                name          type
2830000    "bauxfeed"       tmdpjun
*                from            to          area       jefvcahs
2830101     284010001     274010001   0.068376638             
*             control          trip         alpha           num
2830200             1          515   cntrlvar           276
*                srch           mfl           mfv        unused
2830201          -1.0           0.0           0.0           0.0
2830202           0.0           12.5    0.0           0.0
2830203           0.1           12.5    0.0           0.0
2830204           7.7           12.5    0.0           0.0
2830205          8.15           0.0           0.0           0.0
*
*                name          type
2840000    "bauxfeed"       tmdpvol
*                area        length           vol
2840101      92.90304        0.3048           0.0
*            az-angle     inc-angle            dz
2840102           0.0           0.0           0.0
*             x-rough          x-hd         flags
2840103           0.0         15.24             0
*               cword
2840200             3
*                srch         press          temp
2840201           0.0    4.853909e6       310.928
*
*
*}}}
*****************************************************************************************************
*
*  Turbo driven Auxiliary Feedwater at constant rate
*****************************************************************************************************{{{
*
490   time          0 ge    timeof         750   30.0e9  l * turbo driven AFW signal with delay
491   time          0 lt      null           0   1.0e9   n * availability of the system 
492   voidf 171010000 ge      null           0    0.5    l * finish turbo driven AFW
493   voidf 271010000 ge      null           0    0.5    l * finish turbo driven AFW
755          490      and       491                      n
756          755      and      -492                      n
757          755      and      -493                      n
*
*                name          type
4730000    "iauxfeed"       tmdpjun
*                from            to          area       jefvcahs
4730101     474010001     174010001    0.20512991             
*             control          trip
4730200             1           756
*                srch           mfl           mfv        unused
4730201          -1.0           0.0           0.0           0.0
4730202           0.0          24.0           0.0           0.0
*
*                name          type
4740000    "iauxfeed"       tmdpvol
*                area        length           vol
4740101     278.70912        0.3048           0.0
*            az-angle     inc-angle            dz
4740102           0.0           0.0           0.0
*             x-rough          x-hd         flags
4740103           0.0         15.24             0
*               cword
4740200             3
*                srch         press          temp
4740201           0.0    4.853909e6       310.928
*
*                name          type
4750000    "bauxfeed"       tmdpjun
*                from            to          area       jefvcahs
4750101     476010001     274010001   0.068376638             
*             control          trip
4750200             1           757 
*                srch           mfl           mfv        unused
4750201          -1.0           0.0           0.0           0.0
4750202           0.0           8.0           0.0           0.0
*
*                name          type
4760000    "bauxfeed"       tmdpvol
*                area        length           vol
4760101      92.90304        0.3048           0.0
*            az-angle     inc-angle            dz
4760102           0.0           0.0           0.0
*             x-rough          x-hd         flags
4760103           0.0         15.24             0
*               cword
4760200             3
*                srch         press          temp
4760201           0.0    4.853909e6       310.928
*
*
*}}}
*****************************************************************************************************
*
*  Accumulators
*****************************************************************************************************{{{
*
591 acvliq       190 ge      null          0 0.4247527 n * Acc isolation signal
592 acvliq       290 ge      null          0 0.1415842 n * Acc isolation signal
*
*}}}
*****************************************************************************************************
*
*  Volumetrical control system
*
*****************************************************************************************************{{{
*
*                name          type
1610000       "pzrin"       tmdpjun
*                from            to          area       jefvcahs
1610101     162010002     112040001           0.0             
*             control          trip         alpha           num
1610200             1           691      cntrlvar           150
*                srch           mfl           mfv        unused
1610201          -1.0           0.0           0.0           0.0
1610202          8.15      11.07769           0.0           0.0
1610203          8.55      5.718458           0.0           0.0
1610204          8.70           0.0           0.0           0.0
1610205          8.90           0.0           0.0           0.0
1610206          9.05     -2.718458           0.0           0.0
1610207          9.35      -6.07769           0.0           0.0
*
*                name          type
1620000        "cont"       tmdpvol
*                area        length           vol
1620101     2.7870912           0.0     0.8495054
*            az-angle     inc-angle            dz
1620102           0.0           0.0           0.0
*             x-rough          x-hd         flags
1620103           0.0           0.0             0
*               cword
1620200             3
*                srch         press          temp
1620201           0.0    1.586104e7       560.928
*
*}}}
*
*****************************************************************************************************
*
*   SG Relief valves
*
******************************************************************************************************{{{
*
422  time          0 gt      null          0 1.0e9  l * open SG intact loop relief valve at time
423  time          0 gt      null          0 1.0e9   l * open SG broken loop relief valve at time
654           651           and           422             n
655           653           and           422             n
664           661           and           423             n
665           663           and           423             n
*
551      p 180010000 gt     null 0    7584233.0 n * SG relief setpoint
552      p 180010000 gt     null 0    7791076.0 n * SG relief setpoint
*
651           551           and           652             n * SG relief
652           552            or           651             n * SG relief
653          -652            or          -551             n * SG relief
*
561      p 280010000 gt     null 0      7584233.0 n * SG relief setpoint
562      p 280010000 gt     null 0      7791076.0 n * SG relief setpoint
*
661           561           and           662             n * SG relief
662           562            or           661             n * SG relief
663          -662            or          -561             n * SG relief
*                name          type
1870000    "sgi-porv"         valve
*                from            to          area
1870101     180010002     189010001   6.967728e-3
*           fwd. loss     rev. loss       efvcahs
1870102           0.0           0.0           100
*           discharge       thermal      
1870103           1.0          0.14
*                flow            vl            vv        unused
1870201             0           0.0           0.0           0.0
*                type
1870300        mtrvlv
*               topen        tclose         vrate          ipos
1870301           654           655         0.556           0.0
*
*                name          type
2870000    "sgb-porv"         valve
*                from            to          area
2870101     280010002     289010001   2.32257e-3
*           fwd. loss     rev. loss       efvcahs
2870102           0.0           0.0           100
*           discharge       thermal      
2870103           1.0          0.14
*                flow            vl            vv        unused
2870201             0           0.0           0.0           0.0
*                type
2870300        mtrvlv
*               topen        tclose         vrate          ipos
2870301           664           665         0.556           0.0
*
*}}}
*****************************************************************************************************
*
*  Pump seal leak
* 1.0e7 1  
*****************************************************************************************************{{{
*
454   time         0 gt      timeof       452     0.0             n * start of leaking time after SBO
458   time         0 lt      null          0      1.0e9           n * end of RCP leak
770           458           and           454                     n 
*
*                name          type
5020000     "contain"       tmdpvol
*                area        length           vol
5020101        1.54e4           0.0        2.98e7
*            az-angle     inc-angle            dz
5020102           0.0          90.0         100.0
*             x-rough          x-hd         flags
5020103           0.0           0.0            10
*               cword
5020200             2
*                srch         press         squal
5020201           0.0    1.013529e5           1.0
*
*                name          type
5070000    "breakvlv"         valve
*                from            to          area
5070101     210010006     502010001         1.e-5
*           fwd. loss     rev. loss       efvcahs
5070102           0.0           0.0       1010100
*           discharge       thermal       
5070103           1.0          0.14
*                flow           mfl           mfv        unused
5070201             1           0.0           0.0           0.0
*                type
5070300        trpvlv
*                trip
5070301           770
*
*                name          type
5010000     "contain"       tmdpvol
*                area        length           vol
5010101        1.54e4           0.0        2.98e7
*            az-angle     inc-angle            dz
5010102           0.0          90.0         100.0
*             x-rough          x-hd         flags
5010103           0.0           0.0            10
*               cword
5010200             2
*                srch         press         squal
5010201           0.0    1.013529e5           1.0
*
*                name          type
5060000    "breakvlv"         valve
*                from            to          area
5060101     114010006     501010001        3.0e-5
*           fwd. loss     rev. loss       efvcahs
5060102           0.0           0.0       1010100
*           discharge       thermal       
5060103           1.0          0.14
*                flow           mfl           mfv        unused
5060201             1           0.0           0.0           0.0
*                type
5060300        trpvlv
*                trip
5060301           770 
*}}}
*****************************************************************************************************
*
*  HPIS
*****************************************************************************************************{{{
503      p 150010000 le      null          0 1.261741e7 l * HPSI
*                name          type
1970000       "ihpis"       tmdpvol
*                area        length           vol
1970101           1.0           0.0          30.0
*            az-angle     inc-angle            dz
1970102          90.0           0.0           0.0
*             x-rough          x-hd         flags
1970103           0.0         0.167             0
*               cword
1970200             3
*                srch         press          temp
1970201           0.0         2.0e6       310.928
*
*                name          type
1980000       "ihpis"       tmdpjun
*                from            to          area       jefvcahs
1980101     197010002     116010001        0.0654             0
*             control          trip         alpha           num
1980200             1           503             p     116010000
*                srch           mfl           mfv      unused
1980201          -1.0           0.0           0.0         0.0
1980202       1.00d+5          16.0           0.0         0.0
1980208       4.00d+6         11.52           0.0         0.0
1980214       1.00d+7          6.27           0.0         0.0
1980215       1.10d+7         5.248           0.0         0.0
1980217       1.23d+7         4.016           0.0         0.0
1980218       1.23d+7           0.0           0.0         0.0
*
*                name          type
2970000       "bhpis"       tmdpvol
*                area        length           vol
2970101           1.0           0.0          30.0
*            az-angle     inc-angle            dz
2970102          90.0           0.0           0.0
*             x-rough          x-hd         flags
2970103           0.0         0.167             0
*               cword
2970200             3
*                srch         press          temp
2970201           0.0         2.0e6       310.928
*
*                name          type
2980000       "bhpis"       tmdpjun
*                from            to          area       jefvcahs
2980101     297010002     212010001        0.0654             0
*             control          trip         alpha           num
2980200             1           503       p     116010000
*                srch           mfl           mfv      unused
2980201          -1.0           0.0           0.0         0.0
2980202       1.00d+5          48.0           0.0         0.0
2980208       4.00d+6         33.52           0.0         0.0
2980214       1.00d+7         18.27           0.0         0.0
2980215       1.10d+7        15.248           0.0         0.0
2980217       1.23d+7        12.016           0.0         0.0
2980218       1.23d+7           0.0           0.0         0.0
*
*}}}
*****************************************************************************************************
*
*  LPIS
*
*****************************************************************************************************{{{
*
520      p 345010000 lt      null          0    1.42e+6 l * LPSI
*                name          type
1950000       "ilpis"       tmdpvol
*                area        length           vol
1950101           1.0           0.0          30.0
*            az-angle     inc-angle            dz
1950102          90.0           0.0           0.0
*             x-rough          x-hd         flags
1950103           0.0         0.167             0
*               cword
1950200             3
*                srch         press          temp
1950201           0.0         2.0e6       310.928
*
*                name          type
1960000       "ilpis"       tmdpjun
*                from            to          area       jefvcahs
1960101     195010002     116010001        0.0654             0
*             control          trip         alpha           num
1960200             1           520             p     116010000
*                srch           mfl           mfv        unused
1960201          -1.0           0.0           0.0           0.0
1960202           0.0           0.0           0.0           0.0
1960203        1.01e5         122.4           0.0           0.0
1960204        1.01e6         122.4           0.0           0.0
1960205        1.42e6           0.0           0.0           0.0
*
*                name          type
2950000       "blpis"       tmdpvol
*                area        length           vol
2950101           1.0           0.0          30.0
*            az-angle     inc-angle            dz
2950102          90.0           0.0           0.0
*             x-rough          x-hd         flags
2950103           0.0         0.167             0
*               cword
2950200             3
*                srch         press          temp
2950201           0.0         2.0e6       310.928
*
*                name          type
2960000       "blpis"       tmdpjun
*                from            to          area       jefvcahs
2960101     295010002     212010001        0.0654             0
*             control          trip         alpha           num
2960200             1           520             p     212010000
*                srch           mfl           mfv        unused
2960201          -1.0           0.0           0.0           0.0
2960202           0.0           0.0           0.0           0.0
2960203        1.01e5          40.8           0.0           0.0
2960204        1.01e6          40.8           0.0           0.0
2960205        1.42e6           0.0           0.0           0.0
*
*
*}}}
.