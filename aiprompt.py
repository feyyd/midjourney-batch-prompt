import time
import argparse
import pyautogui
import sys
import re
import random
import pygetwindow as gw

# This is the value you might need to modify if program is not clicking in the right place
discord_click_one = (50, 60) # dm section (top left of discord window)
# Modification should not be needed as this is set based on above click location
discord_click_two = (discord_click_one[0]+90, discord_click_one[1]) #find conversation location, clicking this area auto selects search textbox
# Toggle debug statements
DEBUG = True # perhaps change to python 'logging'
# Time between batches (9 prompts, midjourney's limit)
batch_sleep_delay = 150

# prompt modifiers
# modifies the surface of the subject.  Things like: chrome, wood, stone work well, but things like rain, clouds, stars don't have great effect
prompt_with_texture_of = ', with texture of '
# more radical than above, good with things like yarn, cotton, lace, or other effects where more than just surface modification is needed
prompt_made_of = ', made of '
# good for using someone elses style like an artist or director, also good for time periods or genre
prompt_style_of = ', in the style of '

# array values for prompt modifiers.  textures used for textureof and madeof, styleof has its own array, modify arrays or manually use {} in subject
in_the_styles_of = ['picasso', 'comic book', 'edo period'] 
textures = ['argyle', 'pinstripes']
# textures = ['argyle', 'pinstripes', 'cloth', 'fabric', 'hair', 'fur', 'lace', 'clouds', 'slime', 'yarn', 'wood', 'rainbows', 'jewelery',
# 'blood', 'rain', 'leather', 'snow', 'elements', 'plastic', 'chrome', 'glass', 'cracked glass', 'powder', 'skin', 'billboards',
# 'crystals', 'gemstones', 'muscle tissue', 'dirt', 'mud', 'brick', 'letters', 'numbers', 'holidays (christmas, easter)', 'candy cane',
# 'candysports jersey', 'uniform', 'foiliage', 'flowers', 'plants', 'moss', 'rust', 'cement', 'water', 'liquid', 'galaxies', 'stars',
# 'lego', 'hearts']

# !!!CAVEAT!!!: using the large arrays of textures or styles like above can cause huge files and prompt spaces
# for example the following prompt generates 6.5 megabytes and 29,000 queries:
# python .\aiprompt.py --subject "{Green, Red, Orange} Frog" --text --styleof --textureof --mode3
# 3 subject * 2 style of * 49 textures * 4 chaos value * 4 weird value * 2 style value * 3 stylize value = 28,800


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
    # setup console argument parsing
    parser = argparse.ArgumentParser(description='Midjourney AI Prompt Assist Tool')
    
    group1 = parser.add_mutually_exclusive_group(required=True)
    group1.add_argument('infile', nargs='?', type=argparse.FileType('r',1024,'utf-16'), default=sys.stdin)
    group1.add_argument('--subject', nargs='+', help='Prompt Subject.')
    
    parser.add_argument('--ar', nargs='*', help='Aspect Ratio. (1:1,2:1,16:9)', default=['2:1'])
    parser.add_argument('--weird', nargs='*', help='Weird. (0-3000)', default=['0'])
    parser.add_argument('--chaos', nargs='*', help='Chaos. (0-100)', default=['0'])
    parser.add_argument('--stylize', nargs='*', help='Stylize. (0-1000?)', default=['100'])
    parser.add_argument('--style', nargs='*', help='Style. 4a,4b,4c does not work with newest versions but are valid on older ones. (raw, 4a, 4b, 4c)', 
                        choices=['', 'raw', '4a', '4b', '4c'], default=[''])
    
    parser.add_argument('--text', action='store_true', help='Only print text prompts, do not push to discord')
    
    # these options will toggle the use of the topmost arrays of textures or style_ofs and will add to the end of the subject
    # WARNING:  Can cause enormous amounts of permutations so set the arrays and values in them accordingly
    group2 = parser.add_mutually_exclusive_group(required=False)
    group2.add_argument('--textureof', action='store_true', help='Adds "with the texture of" to end of subject prompt and uses internal texture array')
    group2.add_argument('--madeof', action='store_true', help='Adds "made of" to end of subject prompt and uses internal texture array')
    
    parser.add_argument('--styleof', action='store_true', help='Adds "in the style of" to end of subject prompt and uses internal styleof array')
    
    parser.add_argument('--mode1', action='store_true', help='Custom Mode1 Settings. (Decent settings for good variety)')
    parser.add_argument('--mode2', action='store_true', help='Custom Mode2 Settings. (Small amount permutations)')
    parser.add_argument('--mode3', action='store_true', help='Custom Mode3 Settings. (Personal Project settings)')
    
    
    group3 = parser.add_mutually_exclusive_group(required=False)
    # ie: 50 is passed for weird value, and 10 is passed as randomize value.  this would yield a 45-55 weird value
    group3.add_argument('--randomize_percent', nargs='?', help='Randomize numerical inputs with percentage deviation from given value.')
    # ie: 50 is passed for chaos value, and 10 is passed as randomize value.  this would yield 40-60 chaos value
    group3.add_argument('--randomize_number', nargs='?', help='Randomize numerical inputs with 0-value added or subtracted.')

    # Parse the arguments
    args = parser.parse_args()

    # readability for shorter param lists
    global arg_randomize_percent, arg_randomize_number
    arg_randomize_percent = args.randomize_percent
    arg_randomize_number = args.randomize_number
    
    args = apply_custom_modes(args)
    
    return args

    
def safe_format(template, **kwargs):
    # format options weren't letting me replace subset of placeholders, regex method allows it though, written by ChatGPT

    # Create a pattern to match named placeholders
    pattern = re.compile(r'\{(\w+)\}')
    
    # Function to replace placeholders with given values or leave unchanged
    def replacer(match):
        key = match.group(1)
        return str(kwargs[key]) if key in kwargs else match.group(0)
    
    # Use the replacer function to format the string
    return pattern.sub(replacer, template)
    
def randomize_arg_min0(arg_value):
    is_random_percent = arg_randomize_percent is not None
    is_random_number = arg_randomize_number is not None
    return_value = arg_value = float(arg_value)
        
    # randomize values if --randomize is set
    if (is_random_percent):
        # base value + positive or negative percentage of base value
        #          base val  + base val  *  sign and scale            * input percent
        return_value = arg_value + arg_value * (random.uniform(-.01, .01) * float(arg_randomize_percent))
                
                   
    elif(is_random_number):
        #         base value + sign and scale     * input number
        return_value = arg_value + random.uniform(-1,1) * float(arg_randomize_number)
        
    return int(max(0,return_value))
    
def generate_full_strings(args):
    # Convert subject array of strings into a single string separated by spaces
    subject_as_string = ' '.join(map(str, args.subject))
    # Extract any embedded multiples in subject ie 'test {opt1, opt2}' -> ['test opt1', 'test opt2']
    expanded_subjects = expand_strings(subject_as_string)    
    all_prompt_strings = []
    
    def process_styles(expanded_subject, arg_style, arg_stylize, arg_chaos, arg_weird, arg_ar, texture, made_of):
        if args.styleof:
            for style_of_value in in_the_styles_of:
                all_prompt_strings.append(
                    inject_string_with_values(expanded_subject, arg_style, arg_stylize, arg_chaos, arg_weird, arg_ar, texture, made_of, f'{prompt_style_of}{style_of_value}')
                )
        else:
            all_prompt_strings.append(
                inject_string_with_values(expanded_subject, arg_style, arg_stylize, arg_chaos, arg_weird, arg_ar, texture, made_of, '')
            )
    
    def inject_string_with_values(expanded_subject, arg_style, arg_stylize, arg_chaos, arg_weird, arg_ar, texture, made_of, style_of_value):
        # Define the formattable string template
        formattable_prompt_string = '{subject}{texture_of}{made_of}{style_of} --ar {aspectRatio} --chaos {chaos} --weird {weird} --stylize {stylize} {style}'
        # add --style if style was set in options, doing this here to avoid having user input '--style' with the option
        style_string = f'--style {arg_style}' if (arg_style != '') else arg_style
        
        replace_values = {
            'subject':expanded_subject, 
            'aspectRatio':arg_ar, 
            'chaos':randomize_arg_min0(arg_chaos), 
            'weird':randomize_arg_min0(arg_weird), 
            'stylize':randomize_arg_min0(arg_stylize),
            'style':style_string,
            'texture_of': texture,
            'made_of': made_of,
            'style_of': style_of_value
        }
        formatted_string = safe_format(formattable_prompt_string, **replace_values)
        return formatted_string

    for arg_ar in args.ar:
        for arg_weird in args.weird:
            for arg_chaos in args.chaos:
                for arg_stylize in args.stylize:
                    for arg_style in args.style:
                        for expanded_subject in expanded_subjects:
                            if args.textureof or args.madeof:
                                for texture in textures:
                                    if args.textureof:
                                        process_styles(expanded_subject, arg_style, arg_stylize, arg_chaos, arg_weird, arg_ar, f'{prompt_with_texture_of}{texture}', '')
                                    elif args.madeof:
                                        process_styles(expanded_subject, arg_style, arg_stylize, arg_chaos, arg_weird, arg_ar, '', f'{prompt_made_of}{texture}')
                            else:
                                process_styles(expanded_subject, arg_style, arg_stylize, arg_chaos, arg_weird, arg_ar, '', '')

    return all_prompt_strings

def print_full_strings(full_strings):
    for index, string in enumerate(full_strings):
        if index % 9 == 0:
            print() #empty line
        print(string)
        
# string methods word extraction approach (faster than regex (tested non-recursively at least), more readable)
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
            # Nested { or } would cause prompts to do weird stuff when injecting into Discord, so I'm just disallowing it and halting program if this happens
            append_string = f'{prefix}{word}{expanded_suffix}'
            if ( '{' in append_string or '}' in append_string ):
                print(f'Nested brackets {{ }} are not allowed. Offender: {append_string}\n')
                sys.exit()
            else:
                expanded_strings.append(append_string)

    return expanded_strings
    
def inject_discord_prompts(full_strings):
    imagine_string = '/imagine'
    timer_fragments = 20
    total_prompts = remaining_prompts = len(full_strings)
    
    windows = gw.getWindowsWithTitle("Discord")
    if (windows):
        discord_window = windows[0]
        discord_window.maximize()
        discord_window.activate()
    else:
        print("No Discord window found.")
        sys.exit()    
    
    
    while (remaining_prompts > 0):
        # select Midjourney Bot, least error prone way I have found
        pyautogui.click(discord_click_one, clicks=1, interval=1, button='left')
        time.sleep(.2)
        pyautogui.click(discord_click_two, clicks=1, interval=1, button='left')
        time.sleep(.2)
        
        pyautogui.typewrite('Midjourney Bot')
        time.sleep(.33)
        pyautogui.press('enter')
    
        # Keyboard type the 9 strings and remove strings from list that we are processing
        for _ in range(9):
            if (remaining_prompts > 0 ):
                pyautogui.typewrite( f'{imagine_string} {full_strings.pop()}')
                remaining_prompts -= 1
                time.sleep(.33)
                pyautogui.press('enter')
                time.sleep(1.25)
        
        # percentatge complete, 2 decimal precision
        percent_complete = '{:.2f}'.format((1-(remaining_prompts/total_prompts)) * 100)
        print(f'{remaining_prompts}/{total_prompts} prompts remain. ({percent_complete}% complete.)\n')
        
        # don't sleep if list is empty
        if ( remaining_prompts > 0 ):
            for k in range(timer_fragments+1):
                # Sleep progress percentage
                time.sleep(batch_sleep_delay/timer_fragments)
                print(f'{((k * 100/timer_fragments))}% through current sleep.')

def main():
    args = setup_argument_parser()
    if (DEBUG):
        # print argparse arguments
        print(args, end='\n\n')
        # print window location if one needs to change the discord click locations
        print(pyautogui.position())
    
    # Don't generate strings if we are using an input file
    full_strings = generate_full_strings(args) if args.subject else ['']
        
    # text
    if (args.text is True):
        print_full_strings(full_strings)
        if DEBUG: print(f'Line Count w/ Spaces:{len(full_strings)}')
        sys.exit()
    # infile
    elif (args.infile.name != '<stdin>'):
        print(f'Using file {args.infile.name} for Discord injection, ignoring prompt args\n')
        full_strings = args.infile.readlines()

    # Remove blank lines and remove trailing/leading white space (that were added for human readability)
    non_empty_strings = [s.strip() for s in full_strings if s.strip() != '']
    
    # infile/--subject
    inject_discord_prompts(non_empty_strings)

if __name__ == '__main__':
    print() # Easier to read command line with separation
    main()
