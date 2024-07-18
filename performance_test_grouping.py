import re
import time

template_string = "hello there {world, guys, mom, duck, batch, finnish, ladies, gentlement, more, terms, here}"

# Regular Expression Approach
def generate_strings_regex(template):
    match = re.search(r"\{([^}]+)\}", template)
    if not match:
        return [template]
    words = [word.strip() for word in match.group(1).split(",")]
    return [template[:match.start()] + word + template[match.end():] for word in words]

# String Methods Approach
def generate_strings_string_methods(template):
    start = template.find('{')
    end = template.find('}', start)
    if start == -1 or end == -1:
        return [template]
    words_section = template[start+1:end]
    words = [word.strip() for word in words_section.split(",")]
    prefix = template[:start]
    suffix = template[end+1:]
    return [f"{prefix}{word}{suffix}" for word in words]

# Timing Regular Expression Approach
start_time = time.time()
for _ in range(100000):
    generate_strings_regex(template_string)
regex_duration = time.time() - start_time

# Timing String Methods Approach
start_time = time.time()
for _ in range(100000):
    generate_strings_string_methods(template_string)
string_methods_duration = time.time() - start_time

print(f"Regex approach duration: {regex_duration:.6f} seconds")
print(f"String methods approach duration: {string_methods_duration:.6f} seconds")