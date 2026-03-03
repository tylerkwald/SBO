* Title: Indications for peforming a cooldown of 55 K/h
* Date: 2025-03-28
* Author: Jordi Freixa
*
* The cooldown procedure is performed by reducing the pressure in the SGs. The
* pressure is reduced by means of the relief valves. The operators change the 
* setpoint of the relief valves and with doing so they are open for longer periods
* of time.
* 
* In the provided input, the relief valves setpoints are fixed at the default value
* (opening and closing for both loops):
* 
551      p 180010000 gt     null 0    7584233.0 n * SG relief setpoint
552      p 180010000 gt     null 0    7791076.0 n * SG relief setpoint
*
561      p 280010000 gt     null 0      7584233.0 n * SG relief setpoint
562      p 280010000 gt     null 0      7791076.0 n * SG relief setpoint
* 
* What we are going to do is to change it and use a control variable that we can
* adjust. The closing setpoint will be a dp similar to the one above (about 2 bar)
* 
551      p 180010000 gt     cntrlvar 835    0.0 n * SG relief setpoint
552      p 180010000 gt     cntrlvar 835    201076.0 n * SG relief setpoint
*
561      p 280010000 gt     cntrlvar 835    0.0 n * SG relief setpoint
562      p 280010000 gt     cntrlvar 835    201076.0 n * SG relief setpoint
* 
* Now we need to construct the control variable 835 (arbitrary number) such that
* when we give the order it will start to reduce at the correct rate (55K/h).
* For this purpose we are going to use a function type control var.
* We build a control bar that reads a table after a trip is true as time advances.
* Below you have the example of the input. tasks you need to do:
* 
* 1- make a trip to start the cooldown and insert it in the table (TTT)
* 2- In the table calculate the saturation pressure corresponding to the 55K/h 
   * reduction. I put some times but 10 lines should be more than enough. 
   * Remember that the pressure is only reduced to 15 bar, so you can already 
   * calculate the total time duration of the procedure.
  * -  Free logical trips: 630 to 650
  * -  Free analog trips: 530 to 550
* 
20583500   bllpi   function 1.0  0.0 0 *unc 1.0 0.0  0
20583501    time  0        004
*
20200400    power      TTT 
20200401  -1.0         7584233.0
20200402   300.0       Enter the saturation pressure after 300 seconds
20200403   600.0       Enter the saturation pressure after 600 seconds
20200404   900.0       Enter the saturation pressure after 900 seconds
20200405   1200.0      ...
.
.
.
202004NN   time?     1500000.0 * we finish the action when we reach 15 bar
*
* Finally you will encounter an error because RELAP does not want to compare a 
* pressure with the table (which RELAP understands as power). To bypass this
* we will put p-180010000 into a controlvar like this:
* 
20583600 setpoint  sum 1.0  0.0     1     0
*                   a0         scale     name         param
20583601           0.0        1.0      p     180010000
* then the trips would be like this:
551      cntrlvar 836 gt     cntrlvar 835    0.0 n * SG relief setpoint
552      cntrlvar 836 gt     cntrlvar 835    201076.0 n * SG relief setpoint *
.

