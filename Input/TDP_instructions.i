* These are the instructions to fulfill the right managing of the TDP
* When TDP works with batteries the flow is adjusted to have a good SG level
* When TDP has not batteries, we will consider that it injects a constant flow until the SG
* is flooded.
* To perform this operation we will use two tmdpjun, one for each situation 
* (and then two for each loop)
* The first part will be carried out by the normal AFW block.
* The second part by the "Turbo driven Auxiliary Feedwater at constant rate"
********************************************************************************
*     First part (normal AFW)
********************************************************************************
* Change the trips in the AFW system to start and end the AFW 
* - Start with SBO
* - End 5h after SBO
* use the following trips to start and end (adjust them):
515   time         0 ge    timeof        750 3.0e9   l * AFW signal with delay
491   time         0 lt    timeof        515 1.0e9   n * availability of the system 
758          515      and       491                      n
* replace trip 515 by 758 in cards:
1830200             1          515  cntrlvar           176
2830200             1          515   cntrlvar           276
********************************************************************************
*     Second part (Turbo driven Auxiliary Feedwater at constant rate)
********************************************************************************
* Change the trips in the TDP-AFW system to start and end
* - Start 5h after SBO
* - End when separator is flooded
* use the following trips to start and end:
* Start will be -491
* End for each loop:
492   voidf 171010000 ge      null           0    0.5    l * finish turbo driven AFW
493   voidf 271010000 ge      null           0    0.5    l * finish turbo driven AFW
* combined
755          750      and      -491                      n
756          755      and      -492                      n
757          755      and      -493                      n
