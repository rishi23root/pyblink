# pyblink 👁👀
many people have problems due to not blinking eyes like eye-strains, etc.
That can be super painful in the long-term so the use of this program can help you to work longer on a computer screen.

### working 👷‍
The program count the blinks of the user and notify user of his status.
and all the data will save in csv file in chunks add all blinks data and divide with sum of time then multiply with 60 to get the average time of the user  

`Note`: good camera provide better and more accurate results 


## Steps for setup the program 🔨
  1. `git clone `
  2. `cd pyblink`
  3. `pip install -r requirement.txt` complete requiremnts

## Arguments 🕵️‍
**Use help to get full detail** `python .\blink.py -h`
``` 
usage: blink.py [-h] [-o] [-d] [-b]

optional arguments:
  -h, --help        show this help message and exit
  -o, --once        run the program in background for only 2 mins and show results
  -d, --debug       run the program in with gui to check the realtime actions
  -b, --background  run the program in background and keep notify you with 20 min intervals if your blink is not proper
 ```

### There are 3 versions of program 
  1. once version to run only for 2 min and anaylse the data
  
    `python blink.py -o`
  2. debuging version to see how your camera is working
  
     `python blink.py -d`
  3. background version to run in the background and analyse the data
  
    `python blink.py -b` simple in background 
    `python blink.py -b -d`  check the backgroud working 


**show the notification in the corner of the screen**

<img src='https://github.com/rishabhjainfinal/pyblink/blob/main/ss.png'>


## Additional
**If notifications are not working then try these :**
  1. `python -m pip install setuptools --upgrade`
  2. problem in notification - [link to Stack-Overflow page](https://stackoverflow.com/questions/45755475/why-is-this-simple-python-toast-notification-not-working)
  
  
