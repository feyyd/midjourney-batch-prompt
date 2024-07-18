import time
import argparse
import pyautogui
import sys

#---------------------------UNUSED ATM-------------------------
# prompt "with the texture of" - modifies the surface of the subject.  Things like: chrome, wood, stone work well, but things like rain, clouds, stars don't have great effect
promptWithTextureOf = 'with texture of {0}'
# prompt "made of" - more radical than above, good with things like yarn, cotton, lace, or other effects where more than just surface modification is needed
promptMadeOf = 'made of {0}'

textures = 'argyle', 'pinstripe', 'cloth', 'fabric', 'hair', 'fur', 'lace', 'clouds', 'slime', 'yarn', 'wood', 'rainbows', 'jewelery',
'blood', 'rain', 'leather', 'snow', 'elements', 'plastic', 'chrome', 'glass', 'cracked glass', 'powder', 'skin', 'billboards',
'crystals', 'gemstones', 'muscle tissue', 'dirt', 'mud', 'brick', 'letters', 'numbers', 'holidays (christmas, easter)', 'candy cane',
'candysports jersey', 'uniform', 'foiliage', 'flowers', 'plants', 'moss', 'rust', 'cement', 'water', 'liquid', 'galaxies', 'stars',
'lego', 'hearts'
#--------------------------------------------------------------

# Program is dumb, it just clicks taskbar discord icon, then clicks the text input bar at these locations and types, these values need setup per machine
discordIconLocation = (1225,1408)
discordMessageLocation = (507,1320)
# Time between batches (9 prompts, midjourney's limit)
batchSleepDelay = 150
# Toggle debug statements
DEBUG = False # perhaps change to python "logging"

def ApplyCustomModes(args):
    # When a custom mode is selected, replace command line arguments
    if ( args.mode1 is True ):
        args.chaos = [0, 10, 25]
        args.weird = [0, 25, 75, 210]
        args.style = ['', 'raw']
        args.stylize = [33, 100, 150]
        args.ar = ['1:1']
    elif ( args.mode2 is True ):
        args.chaos = [0]
        args.weird = [0]
        args.style = ['', 'raw']
        args.stylize = [33, 100]
        args.ar = ['2:1']
    elif ( args.mode3 is True ):
        args.chaos = [0, 5, 10, 25]
        args.weird = [0, 24, 54, 210]
        args.style = ['', 'raw']
        args.stylize = [55, 89, 111]
        args.ar = ['1:1']
        
    return args

def SetupArgumentParser():
    #setup console argument parsing
    parser = argparse.ArgumentParser(description='Midjourney AI Prompt Assist Tool')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('infile', nargs='?', type=argparse.FileType('r',1024,'utf-16'), default=sys.stdin)
    group.add_argument('--subject', nargs='+', help='Prompt Subject.')
    
    parser.add_argument('--ar', nargs='*', help='Aspect Ratio. (1:1,2:1,16:9)', default=['2:1'])
    parser.add_argument('--weird', nargs='*', help='Weird. (0-3000)', default=['0'])
    parser.add_argument('--chaos', nargs='*', help='Chaos. (0-100)', default=['0'])
    parser.add_argument('--stylize', nargs='*', help='Stylize. (0-1000?)', default=['100'])
    parser.add_argument('--style', nargs='*', help='Style. 4a,4b,4c does not work with newest versions but are valid on older ones. (raw, 4a, 4b, 4c)', 
                        choices=['', 'raw', '4a', '4b', '4c'], default=[''])
    
    parser.add_argument('--text', action='store_true', help='Only print text prompts, do not push to discord')
    
    parser.add_argument('--mode1', action='store_true', help='Custom Mode1 Settings. (Nice after subject setup)')
    parser.add_argument('--mode2', action='store_true', help='Custom Mode2 Settings. (Test small amt permutations)')
    parser.add_argument('--mode3', action='store_true', help='Custom Mode3 Settings. (Slots)')
    
    # the idea is that a single percentage value can be passed and we will give a deviation off the other values
    # ie: 10 is passed for weird value, and 100 is passed as randomize value.  this would yield a 0-20 weird value
    # ie: 50 is passed for chaos value, and 10 is passed as randomize value.  this would yield 45-55 chaos value
    #parser.add_argument('--randomize', nargs='?', help='Randomize with percentage deviation from given value.')

    # Parse the arguments
    args = parser.parse_args()   
    args = ApplyCustomModes(args)
    
    return args
    
def GenerateFullStrings(args):
    formattablePromptString = '{subject} --ar {aspectRatio} --chaos {chaos} --weird {weird} --stylize {stylize} {style}'

    # Convert subject array of strings into a single string separated by spaces
    subjectAsString = ' '.join(map(str,args.subject))
    
    #for each combination, insert into a string, then add that string to a list
    allPromptStrings = []
    for arg_ar in args.ar:
        for arg_weird in args.weird:
            for arg_chaos in args.chaos:
                for arg_stylize in args.stylize:
                    for arg_style in args.style:
                        #add --style if style was set in options
                        styleString = f'--style {arg_style}' if (arg_style != '') else arg_style
                        newString = formattablePromptString.format(
                            subject=subjectAsString, aspectRatio = arg_ar, chaos = arg_chaos, weird = arg_weird, stylize = arg_stylize, style = styleString)
                        allPromptStrings.append(newString)                        
        
    return allPromptStrings                          

def PrintFullStrings(fullStrings):
    for index, string in enumerate(fullStrings):
        if index % 9 == 0:
            print() #empty line
        print(string)
    
def DiscordPromptInjection(fullStrings):
    imagineString = '/imagine'
    timerFragments = 20
    totalPrompts = remainingPrompts = fullStrings.__len__()
    
    
    # Discord Icon Location
    pyautogui.click(discordIconLocation, clicks=1, interval=1, button='left')
    time.sleep(.2)
    
    # Discord Message Location
    pyautogui.click(discordMessageLocation, clicks=1, interval=1, button='left')
    time.sleep(.2)
    
    while (remainingPrompts > 0):
        # Keyboard type the 9 strings and remove strings from list that we are processing
        for j in range(9):
            if (remainingPrompts > 0 ):
                pyautogui.typewrite( f'{imagineString} {fullStrings.pop()}')
                remainingPrompts -= 1
                time.sleep(.33)
                pyautogui.press('enter')
                time.sleep(1)
        
        # 2 decimal precision
        remainingPercentage = "{:.2f}".format((1-(remainingPrompts/totalPrompts)) * 100)
        print(f'{remainingPrompts}/{totalPrompts} prompts remain. ({remainingPercentage}% complete.)')
        #don't sleep if list is empty
        if (fullStrings.__len__() > 0 ):
            for k in range(timerFragments):                
                # Sleep progress percentage
                print(f'{((k * 100/timerFragments))}% through current sleep.')
                time.sleep(batchSleepDelay/timerFragments)

def main():
    args = SetupArgumentParser()
    if (DEBUG): print(args)
    
    # Don't generate strings if we are using an input file
    fullStrings = [''] if args.subject is None else GenerateFullStrings(args)

    # text
    if (args.text is True):
        PrintFullStrings(fullStrings)
        sys.exit()
    # infile
    elif (args.infile.name != '<stdin>'):
        print("Using file " + args.infile.name + " for Discord injection, ignoring prompt args\n")
        fullStrings = args.infile.readlines()
    
    # Remove blank lines and remove trailing/leading white space (that were added for human readability)
    nonBlankStrings = [s.strip() for s in fullStrings if s.strip() != ""]
    if (DEBUG): print(nonBlankStrings)

    # infile/--subject
    DiscordPromptInjection(nonBlankStrings)


if __name__ == "__main__":
    main() 
