* -----------------------------------------------------------------
*   Passive system
* Look for comments with JF
* -----------------------------------------------------------------
* Trips
* -----------------------------------------------------------------
* activation signal
534   time         0 ge      null          0  1500.0        n
* -----------------------------------------------------------------
*                name          type
4620000         inlet          pipe
*              ncells
4620001             8 
*              x-area         volid
4620101      0.012272             8
*            x-length         volid
4620301         4.125             4
4620302         2.125             8
*              volume         volid
4620401           0.0             8
*          azim-angle         volid
4620501           0.0             8
*          vert-angle         volid
4620601           0.0             4
4620602          90.0             8
*              x-wall           xhd         volid
4620801        1.5e-5           0.0             8
*             x-flags         volid
4621001             0             8
*       ebt   press qual none none none id
4621201 002   6.7e6  1.0  0.0  0.0  0.0 8
*            jefvcahs       jun num
4621101      00000000             7
*                  vl            vv        unused         junid
4621301           0.0           0.0           0.0             7
*---------!---------!---------!---------!---------!---------!---------!---------
*                name          type
4640000    "unnamed"       sngljun
*         from      to        area      floss     rloss     efvcahs
4640101   462010000 465000000 0.0       0.0       0.0       0001100       
*         flow      liquid    vapor     velint
4640201   1         0.0       0.0       0.0          
*---------!---------!---------!---------!---------!---------!---------!---------
*                name          type
4650000            HX          pipe
*              ncells
4650001             3 
*              x-area         volid
4650101      0.057149             3   * JF total area 5 times more?
*            x-length         volid
4650301       1.66667             3
*              volume         volid
4650401           0.0             3
*          vert-angle         volid
4650601         -90.0             3
*              x-wall           xhd         volid
4650801        1.5e-5       0.10234             3 * JF pipes are very big, this diameter is wrong
*             x-flags         volid
4651001             0             3
*       ebt   press qual none none none id
4651201 002 6.7e6  0.0  0.0  0.0  0.0  3
*            jefvcahs       jun num
4651101      00000000             2
*                  vl            vv        unused         junid
4651301           0.0           0.0           0.0             2
*---------!---------!---------!---------!---------!---------!---------!---------
*                name          type
4660000    "unnamed"       sngljun
*         from      to        area      floss     rloss     efvcahs
4660101   465010000 467000000 0.0       0.0       0.0       0001000       
*         flow      liquid    vapor     velint
4660201   1         0.0       0.0       0.0          
*---------!---------!---------!---------!---------!---------!---------!---------
*                name          type
4670000     "unnamed"          pipe
*              ncells
4670001             8 
*              x-area         volid
4670101      0.012272             8
*            x-length         volid
4670301         3.024             4
4670302         4.125             8
*              volume         volid
4670401           0.0             8
*          azim-angle         volid
4670501           0.0             8
*          vert-angle         volid
4670601         -90.0             4
4670602           0.0             8
*              x-wall           xhd         volid
4670801        1.5e-5           0.0             8
*             x-flags         volid
4671001             0             8
*       ebt   press qual none none none id
4671201 002 6.7e6  0.0  0.0  0.0  0.0  8
*            jefvcahs       jun num
4671101      00000000             7
*                  vl            vv        unused         junid
4671301           0.0           0.0           0.0             7
*---------!---------!---------!---------!---------!---------!---------!---------
*                name          type
4680000       exitvlv         valve
*                from            to          area
4680101     467010000     174010003           0.0
*           fwd. loss     rev. loss       efvcahs
4680102           0.0           0.0           100
*           discharge       thermal       
4680103           1.0          0.14
*                flow            vl            vv        unused
4680201             0           0.0           0.0           0.0
*                type
4680300        trpvlv
*                trip
4680301           534
*---------!---------!---------!---------!---------!---------!---------!---------
*                name          type
4690000          pool          pipe
*              ncells
4690001             5 
*              x-area         volid
4690101         144.0             5
*            x-length         volid
4690301       1.66667             5
*              volume         volid
4690401           0.0             5
*          azim-angle         volid
4690501           0.0             5
*          vert-angle         volid
4690601          90.0             5
*              x-wall           xhd         volid
4690801        1.5e-5           0.0             5
*             x-flags         volid
4691001             0             5
*       ebt   press qual none none none id
4691201 004 1.013529e5 305.372  1.0  0.0  0.0  5
* 4691201 002 1.013529e5   0.0  0.0  0.0  0.0  5
*            jefvcahs       jun num
4691101      00000000             4
*                  vl            vv        unused         junid
4691301           0.0           0.0           0.0             4
*---------!---------!---------!---------!---------!---------!---------!---------
*                name          type
4700000        "porv"         valve
*                from            to          area
4700101     469000000     471000000    8.70966e-3
*           fwd. loss     rev. loss       efvcahs
4700102           0.0           0.0           100
*           discharge       thermal       
4700103           1.0          0.14
*                flow            vl            vv        unused
4700201             0           0.0           0.0           0.0
*                type
4700300        trpvlv
*                trip
4700301           610
*---------!---------!---------!---------!---------!---------!---------!---------
*                name          type
4710000        "cont"       tmdpvol
*                area        length           vol
4710101      92.90304        0.3048           0.0
*            az-angle     inc-angle            dz
4710102           0.0           0.0           0.0
*             x-rough          x-hd         flags
4710103           0.0           0.0             0
*               cword
4710200             4
*                srch         press          temp         squal
4710201           1.0    1.013529e5       305.372           1.0
*
********************************
*       Heat Structures        *
********************************
*
*n: PSS
*          nh   np      geom      ssif     leftcoord reflood
10012000    3    4         2         0       10.5e-3       0
*                 mesh        format
10012100             0             2
*            thickness      interval
10012101       6.66e-4             3
*             material      interval
10012201             2             3
*                 rpkf      interval
10012301           1.0             3
*                 temp      interval
10012401         305.0             4
*   Left Boundary Condition Data 
*            bound      incr      type      code        factor      node
10012501 465010000         0       101         1         275.0         1 * JF 165 x 1.66667
10012502 465020000         0       101         1         275.0         2 * JF 165 x 1.66667
10012503 465030000         0       101         1         275.0         3 * JF 165 x 1.66667
*   Right Boundary Condition Data 
*            bound      incr      type      code        factor      node
10012601 469010000         0       101         1         275.0         1 * JF 165 x 1.66667
10012602 469020000         0       101         1         275.0         2 * JF 165 x 1.66667
10012603 469030000         0       101         1         275.0         3 * JF 165 x 1.66667
*               source          mult          dmhl          dmhr           num
10012701             0           0.0           0.0           0.0            3
*   Left Additional Boundary Condition Data 
10012800             0
*        hthd  hlf  hlr gslf gslr glcf glcr lbf node
10012801 0.021 10.0 10.0  0.0  0.0  1.0  1.0 1.0   3
*   Right Additional Boundary Condition Data 
10012900             0
*        hthd  hlf  hlr gslf gslr glcf glcr lbf node
10012901  0.102 10.0 10.0  0.0  0.0  0.0  0.0 1.0  3
*
.
