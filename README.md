# Midjourney AI Prompt Assist Tool
_**midjourney-batch-prompt**_

Python script for batching Midjourney requests to overcome the 9 prompt submission limit.  This script will
create all combinations of desired prompt and values then inject them into discord using pyautogui.  Python is _not_
my primary language.

# Setup

Script clicks Discord icon in Taskbar to bring to foreground, then it clicks the current Discord text input field.  Yes, this is very prone to error.

    "discordIconLocation", "discordMessageLocation" - Tuple of x,y coordinates where the program clicks (Taskbar,Input field respectively)
        These will almost certainly need to be changed or modified in some way
    "batchSleepDelay" default 150 - is the number of seconds between batches of 9 that can be adjusted depending on the workload.
    "DEBUG" default False - enable/disable debug statements
    "timerFragments" default 20 - subdivisions of progress output (print statement every 5%, 100 would print every 1%)

# usage
    usage: aiprompt.py [-h] [--subject SUBJECT [SUBJECT ...]] [--ar [AR ...]] [--weird [WEIRD ...]] [--chaos [CHAOS ...]]
                   [--stylize [STYLIZE ...]] [--style [{,raw,4a,4b,4c} ...]] [--text] [--mode1] [--mode2] [--mode3]
                   [infile]

**required arguments:**
  
  --subject OR infile

**positional arguments:**
  
  infile

**options:**
  
    -h, --help                        show this help message and exit
    --subject SUBJECT [SUBJECT ...]   Prompt Subject.
    --ar [AR ...]                     Aspect Ratio. (1:1,2:1,16:9)
    --weird [WEIRD ...]               Weird. (0-3000)
    --chaos [CHAOS ...]               Chaos. (0-100)
    --stylize [STYLIZE ...]           Stylize. (0-1000?)
    --style [{,raw,4a,4b,4c} ...]     Style. 4a,4b,4c does not work with newest versions but are valid on older ones. (raw, 4a, 4b, 4c)
    --text                            Only print text prompts, do not push to discord
    --mode1                           Custom Mode1 Settings. (Nice after subject setup)
    --mode2                           Custom Mode2 Settings. (Test small amt permutations)
    --mode3                           Custom Mode3 Settings. (Slots)

  **examples (powershell):**
  
  _Inject into Discord via pyautogui:_
  
    python .\aiprompt.py --subject Brown bananas in sunlight --ar 2:1 --weird 0 10 20 --chaos 5 10 --stylize 400
  
  _Text output only:_
  
    python .\aiprompt.py --subject Brown bananas in sunlight --ar 2:1 --weird 0 10 20 --chaos 5 10 --stylize 400 --text

    output:
    Brown bananas in sunlight --ar 2:1 --chaos 5 --weird 0 --stylize 400
    Brown bananas in sunlight --ar 2:1 --chaos 10 --weird 0 --stylize 400
    Brown bananas in sunlight --ar 2:1 --chaos 5 --weird 10 --stylize 400
    Brown bananas in sunlight --ar 2:1 --chaos 10 --weird 10 --stylize 400
    Brown bananas in sunlight --ar 2:1 --chaos 5 --weird 20 --stylize 400
    Brown bananas in sunlight --ar 2:1 --chaos 10 --weird 20 --stylize 400

  _Read from file (blank lines and leading/trailing whitespace will be removed):_

    python .\aiprompt.py test.txt
  
  One can run multiple prompts with --text option and redirect output to file (make sure DEBUG is false to avoid errors) and then run
  said file, ie (powershell):

    #create
    python .\aiprompt.py --subject Brown bananas in sunlight --ar 2:1 --weird 0 10 20 --chaos 5 10 --stylize 400 --text > myprompts.txt
    #append
    python .\aiprompt.py --subject Giant mech canaries --ar 2:1 --weird 0 7 20 --chaos 5 10 --stylize 400 --text >> myprompts.txt
    python .\aiprompt.py --subject Tiny red octopi --ar 2:1 --weird 2 10 20 --chaos 5 10 --stylize 400 --text >> myprompts.txt
    #execute all generated prompts
    python .\aiprompt.py myprompts.txt

  Future:

  Expansion of terms, the following _WOULD_ net the same result:

    python .\aiprompt.py --subject {Brown bananas in sunlight, Giant mech canaries, Tiny red octopi} --ar 2:1 --weird 0 7 20 --chaos 5 10 --stylize 400

  Custom list injection for different tags, "with texture of X", "made of X", "in the style of X" where X is a list of terms.
  
  
