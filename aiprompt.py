import time
import argparse
import pyautogui
import sys

#---------------------------UNUSED ATM-------------------------
# prompt 'with the texture of' - modifies the surface of the subject.  Things like: chrome, wood, stone work well, but things like rain, clouds, stars don't have great effect
prompt_with_texture_of = 'with texture of {0}'
# prompt 'made of' - more radical than above, good with things like yarn, cotton, lace, or other effects where more than just surface modification is needed
prompt_made_of = 'made of {0}'
prompt_style_of = 'in the style of {0}'

textures = 'argyle', 'pinstripe', 'cloth', 'fabric', 'hair', 'fur', 'lace', 'clouds', 'slime', 'yarn', 'wood', 'rainbows', 'jewelery',
'blood', 'rain', 'leather', 'snow', 'elements', 'plastic', 'chrome', 'glass', 'cracked glass', 'powder', 'skin', 'billboards',
'crystals', 'gemstones', 'muscle tissue', 'dirt', 'mud', 'brick', 'letters', 'numbers', 'holidays (christmas, easter)', 'candy cane',
'candysports jersey', 'uniform', 'foiliage', 'flowers', 'plants', 'moss', 'rust', 'cement', 'water', 'liquid', 'galaxies', 'stars',
'lego', 'hearts'
#--------------------------------------------------------------

# Program is dumb, it just clicks taskbar discord icon, then clicks the text input bar at these locations and types, these values need setup per machine
discord_icon_location = (1225,1408)
discord_message_location = (507,1320)
# Time between batches (9 prompts, midjourney's limit)
batch_sleep_delay = 150
# Toggle debug statements
DEBUG = False # perhaps change to python 'logging'

def apply_custom_modes(args):
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

def setup_argument_parser():
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
    args = apply_custom_modes(args)
    
    return args
    
def generate_full_strings(args):
    formattable_prompt_string = '{subject} --ar {aspectRatio} --chaos {chaos} --weird {weird} --stylize {stylize} {style}'

    # Convert subject array of strings into a single string separated by spaces
    subject_as_string = ' '.join(map(str,args.subject))
    # extract any embedded multiples in subject ie 'test {opt1, opt2}' -> ['test opt1' 'test opt2']
    expanded_subjects = expand_strings(subject_as_string)
    #for each combination, insert into a string, then add that string to a list
    all_prompt_strings = []
    for arg_ar in args.ar:
        for arg_weird in args.weird:
            for arg_chaos in args.chaos:
                for arg_stylize in args.stylize:
                    for arg_style in args.style:
                        for expanded_subject in expanded_subjects:
                            #add --style if style was set in options, doing this here to avoid having user input '--style' with the option
                            style_string = f'--style {arg_style}' if (arg_style != '') else arg_style
                            formatted_string = formattable_prompt_string.format(
                                subject=expanded_subject, aspectRatio = arg_ar, chaos = arg_chaos, weird = arg_weird, stylize = arg_stylize, style = style_string)
                            all_prompt_strings.append(formatted_string)                        
        
    return all_prompt_strings                          

def print_full_strings(full_strings):
    for index, string in enumerate(full_strings):
        if index % 9 == 0:
            print() #empty line
        print(string, end='\n')
        
# string methods word extraction approach (faster than regex, more readable)
def expand_strings(template):
    start = template.find('{')
    end = template.find('}', start)
    if start == -1 or end == -1:
        return [template]

    words_section = template[start+1:end]
    words = [word.strip() for word in words_section.split(',')]
    prefix = template[:start]
    suffix = template[end+1:]

    expanded_strings = []
    for word in words:
        # recursive call to handle any nested braces in the suffix
        for expanded_suffix in expand_strings(suffix):
            expanded_strings.append(f'{prefix}{word}{expanded_suffix}')

    return expanded_strings
    
def inject_discord_prompts(full_strings):
    imagine_string = '/imagine'
    timer_fragments = 20
    total_prompts = remaining_prompts = full_strings.__len__()
    
    
    # Discord Icon Location
    pyautogui.click(discord_icon_location, clicks=1, interval=1, button='left')
    time.sleep(.2)
    
    # Discord Message Location
    pyautogui.click(discord_message_location, clicks=1, interval=1, button='left')
    time.sleep(.2)
    
    while (remaining_prompts > 0):
        # Keyboard type the 9 strings and remove strings from list that we are processing
        for j in range(9):
            if (remaining_prompts > 0 ):
                pyautogui.typewrite( f'{imagine_string} {full_strings.pop()}')
                remaining_prompts -= 1
                time.sleep(.33)
                pyautogui.press('enter')
                time.sleep(1)
        
        # 2 decimal precision
        remaining_percentage = '{:.2f}'.format((1-(remaining_prompts/total_prompts)) * 100)
        print(f'{remaining_prompts}/{total_prompts} prompts remain. ({remaining_percentage}% complete.)')
        #don't sleep if list is empty
        if (full_strings.__len__() > 0 ):
            for k in range(timer_fragments):                
                # Sleep progress percentage
                print(f'{((k * 100/timer_fragments))}% through current sleep.')
                time.sleep(batch_sleep_delay/timer_fragments)

def main():
    args = setup_argument_parser()
    if (DEBUG):
        print(args, end='\n\n')
    
    # Don't generate strings if we are using an input file
    full_strings = [''] if args.subject is None else generate_full_strings(args)
        
    # text
    if (args.text is True):
        print_full_strings(full_strings)
        sys.exit()
    # infile
    elif (args.infile.name != '<stdin>'):
        print('Using file ' + args.infile.name + ' for Discord injection, ignoring prompt args\n')
        full_strings = args.infile.readlines()

    # Remove blank lines and remove trailing/leading white space (that were added for human readability)
    non_empty_strings = [s.strip() for s in full_strings if s.strip() != '']

    # infile/--subject
    inject_discord_prompts(non_empty_strings)

def test_expand_strings():
    print(expand_strings('static text {ab,yz}'))

if __name__ == '__main__':
    print() # Easier to read command line with separator
    main() 
