# Winegard_Carryout_Rotor

Addison Wolf, Email: wolfaddison100@gmail.com

This is code for running a portable Carryout Rotor using a Winegard Carryout and GPredict, developed for use by Ali Abedi's Research Lab at UW-Madison, based
partially on the work of Gabe Emerson which can be found here: https://github.com/saveitforparts/Carryout-Rotor

This read me shall go over the hardware requirements, Software requirements, and general good to knows around working with our particular model of Winegard Rotor

## Hardware Requirements

WIP

## Connecting to Winegard

Once the hardware concerns are out of the way connecting your computer to the winegard is fairly straightforward. On windows you just need to know the baud rate and what port you are using to connect to it via a serial terminal. The carryout that this code has been tested on utilized a baud rate of 115200 but other carryouts have been known to use lower baud rates. filling these out in the code where carryout is defined should be enough to allow the program to connect to the carryout. If you need to access the carryout manually an easy way to do this that we have utilized has been to use [putty](https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html).

## Stopping the auto-searching behavior

Immediately upon powering on the winegard what you will likely notice first is that the winegard has an automatic search function. This is unideal for independent uses and thus must be stopped. Luckily with the model this code was designed for there is a very straight forward way to do this. After connecting to the winegard via the serial terminal enter the NVS menu, within this menu you can do a few things, most relevant to this issue is displaying current values, editing the values, and saving the values. You can use d to display the values and somewhere within the list will typically be a value that says something along the lines of "Disable Tracker Proc". If you use e to edit this value and set it to true, then save it using the s command then the auto-searching behavior should cease

This however does lead to the unfortunate fact about many if not all of these antennas. So these antenna's were designed so that everytime they start up they must find the limits of their gears, they do this via slamming into the limits at start up before the tracking process begins. Now it's very important that the antenna does this limit finding both so you're antenna knows where it's angles are supposed to be and so that you aren't forced to hear the awful grinding sounds that still haunt me in my nightmares to this day. This is where we run into the fact that these antennas generally have that limit finding process connected to the tracker process, therefore in order to run this process every time you connect to the carryout from this point on you will need to go into the motor menu and manually home the motors using the home command, which can be done using 'h \*" . This should manually run the homing process allowing you to utilize the carryout without fearing for your ears. The code that is in this repository does it automatically at the start of every session so you do not have to.

## useful commands

It is likely that at some point during your time working with winegard carryouts that you will need to access it manually, whether that be to change the settings or to do some deeper debugging. Therefore we have compiled the following lists of commands of interest for the particular model and firmware that this code was designed for, applicability to other models may vary. If you wish to see the commands that your particular model uses the help menu can be accessed via the standard ?. Note for all commands that carryouts tend not to support backspace and therefore if you make a mistake you just need to flush out the garbage by sending the command which naturally will be promptly ignored.

### Mot

under the motor menu are the following commands

a - go to angle
This command does what it says on the tin, it takes two parameters the motor that you wish to move and the angle that you wish to move it to. Notably in the model this code was designed for it does not take commands for multiple angles like some carryouts seem to.

h - home motors
This is perhaps the most pertinent command for you to be aware of, as it is the command that allows us to do useful things with the antenna despite turning off the automatic tracking mode. This command homes the motors which causes them to find their limits and return to a default position. You can home the motors individually using their motor number or together by entering \* instead of the motor number
