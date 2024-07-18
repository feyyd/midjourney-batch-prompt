# Midjourney AI Prompt Assist Tool
_**midjourney-batch-prompt**_

Python script for batching Midjourney requests to overcome the 9 prompt submission limit.  This script will
create all combinations of desired prompt and values then inject them into discord using pyautogui.  Python is _not_
my primary language.

# Setup

Script clicks Discord icon in Taskbar to bring to foreground, then it clicks the current Discord text input field.  Yes, this is very prone to error.

    "discord_icon_location", "discord_message_location" - Tuple of x,y coordinates where the program clicks (Taskbar,Input field respectively)
        These will almost certainly need to be changed or modified in some way
    "batch_sleep_delay" default 150 - is the number of seconds between batches of 9 that can be adjusted depending on the workload.
    "DEBUG" default False - enable/disable debug statements
    "timer_fragments" default 20 - subdivisions of progress output (print statement every 5%, 100 would print every 1%)

# usage
    usage: aiprompt.py [-h] [--subject SUBJECT [SUBJECT ...]] [--ar [AR ...]] [--weird [WEIRD ...]] [--chaos [CHAOS ...]] [--stylize [STYLIZE ...]] 
          [--style [{,raw,4a,4b,4c} ...]] [--text] [--textureof | --madeof] [--styleof] [--mode1] [--mode2] [--mode3] [infile]

**required arguments:**
  
  --subject OR infile

**mutually exclusive**
  
  --madeof, --textureof

**positional arguments:**
  
  infile

**options:**
  
    -h, --help            show this help message and exit
    --subject SUBJECT [SUBJECT ...]
                          Prompt Subject.
    --ar [AR ...]         Aspect Ratio. (1:1,2:1,16:9)    Default: 2:1
    --weird [WEIRD ...]   Weird. (0-3000)                 Default: 0
    --chaos [CHAOS ...]   Chaos. (0-100)                  Default: 0
    --stylize [STYLIZE ...]
                          Stylize. (0-1000?)              Default: 100
    --style [{,raw,4a,4b,4c} ...]                         Default: ''
                          Style. 4a,4b,4c does not work with newest versions but are valid on older ones. (raw, 4a, 4b, 4c)
    --text                Only print text prompts, do not push to discord
    --textureof           Adds "with the texture of" to end of subject prompt and uses internal texture array
    --madeof              Adds "made of" to end of subject prompt and uses internal texture array
    --styleof             Adds "in the style of" to end of subject prompt and uses internal styleof array
    --mode1               Custom Mode1 Settings. (Decent settings for good variety)
    --mode2               Custom Mode2 Settings. (Small amount permutations)
    --mode3               Custom Mode3 Settings. (Personal Project settings)

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

  _Text output with expansion:_
  
    python .\aiprompt.py --subject "{Brown, Green, Yellow} bananas in sunlight" --ar 2:1 --stylize 400 --text

    output:
    Brown bananas in sunlight --ar 2:1 --chaos 0 --weird 0 --stylize 400
    Green bananas in sunlight --ar 2:1 --chaos 0 --weird 0 --stylize 400
    Yellow bananas in sunlight --ar 2:1 --chaos 0 --weird 0 --stylize 400

  _Read from file (blank lines and leading/trailing whitespace will be removed):_

    python .\aiprompt.py test.txt
  
  _Text output with madeof & styleof_

    python .\aiprompt.py --subject "{Brown, Green} Bananas" --madeof --styleof --text

    output (internal arrays 2 styles, 2 textures):
    Brown Bananas, made of argyle, in the style of picasso --ar 2:1 --chaos 0 --weird 0 --stylize 100
    Brown Bananas, made of argyle, in the style of van gough --ar 2:1 --chaos 0 --weird 0 --stylize 100
    Brown Bananas, made of pinstripe, in the style of picasso --ar 2:1 --chaos 0 --weird 0 --stylize 100
    Brown Bananas, made of pinstripe, in the style of van gough --ar 2:1 --chaos 0 --weird 0 --stylize 100
    Green Bananas, made of argyle, in the style of picasso --ar 2:1 --chaos 0 --weird 0 --stylize 100
    Green Bananas, made of argyle, in the style of van gough --ar 2:1 --chaos 0 --weird 0 --stylize 100
    Green Bananas, made of pinstripe, in the style of picasso --ar 2:1 --chaos 0 --weird 0 --stylize 100
    Green Bananas, made of pinstripe, in the style of van gough --ar 2:1 --chaos 0 --weird 0 --stylize 100


  One can run multiple prompts with --text option and redirect output to file (make sure DEBUG is false to avoid errors) and then run
  said file, ie (powershell):

    #create with expansion of terms within {}
    python .\aiprompt.py --subject "{Brown, Green, Yellow} Bananas" --ar 2:1 --weird 0 10 20 --chaos 5 10 --stylize 400 --text > myprompts.txt
    #append
    python .\aiprompt.py --subject Giant mech canaries --ar 1:1 --weird 0 7 20 --chaos 5 10 --stylize 400 --text >> myprompts.txt
    #execute all generated prompts
    python .\aiprompt.py myprompts.txt
