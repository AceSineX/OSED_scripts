import sys
from termcolor import colored

# Copy/Paste windbg `dd esp` output (or wherever your overflow lands) and check
# if the PAYLOAD is mangled/missing/etc.
# Copy/Paste the payload in a file skip the parenthesis E.g.
#     b"\xdb\xd5\xba\x4f\xea\x85\x39\xd9\x74\x24\xf4\x5e\x31\xc9\xb1"
#     b"\x52\x31\x56\x17\x03\x56\x17\x83\x89\xee\x67\xcc\xe9\x07\xe5"
# Leading whitespaces are ok to leave.
#
# This tool was written while studying for the OSED exam. It is provides sanity 
# check for ensuring that there are no bad/mangled characters. Only for QoL.
# 
#   Usage : Usage: python3 payloadcheck.py <payload_file> <windbg_file>
#
#  Author AceSineX
#

def process_windbg_output(windbg_output):
    lines = windbg_output.strip().split('\n')
    modified_output = []
    for line in lines:
        values = line.split()[1:]
        modified_output.extend(values)
    result = '\n'.join(modified_output)
    return result

def revert_little_endianess(input_data):
    lines = input_data.strip().split('\n')
    modified_output = []
    for line in lines:
        reversed_value = ''.join([line[i:i+2] for i in range(0, len(line), 2)][::-1])
        modified_output.append(reversed_value)
    result = '\n'.join(modified_output)
    return result

def process_payload_string(input_string):
    lines = [line.lstrip() for line in input_string.split('\n')]
    lines = [line[1:] for line in lines]
    joined_string = ''.join(lines)
    cleaned_string = joined_string.replace('"', '')
    cleaned_string = cleaned_string.replace('\\x', '')
    chunks = [cleaned_string[i:i+8] for i in range(0, len(cleaned_string), 8)]
    result = '\n'.join(chunks)
    return result

def compare_strings(str1, str2):
    lines1 = str1.strip().split('\n')
    lines2 = str2.strip().split('\n')
    result = []
    
    for i in range(min(len(lines1), len(lines2))):
        line1 = lines1[i]
        line2 = lines2[i]
        line_result = []
        
        # Compare each pair of characters
        for j in range(0, len(line1), 2):
            pair1 = line1[j:j+2]
            pair2 = line2[j:j+2]
            
            if pair1 != pair2:
                line_result.append(colored(f'{pair2}', 'red'))
            else:
                line_result.append(pair1)
        
        result_line = ''.join(line_result)
        result.append(f"[Line {i+1}] {line1} {result_line}")

    result_string = '\n'.join(result)
    return result_string

def get_user_number():
    while True:
        try:
            user_input = input("Enter Number of Nop bytes in dd output: ")
            number = int(user_input)
            return number
        except ValueError:
            print("Please enter a valid number.")

def shift_characters(input_string, num_chars):
    lines = input_string.strip().split('\n')
    single_line = ''.join(lines)
    single_line = single_line[num_chars:]
    result = []
    for i in range(0, len(single_line), 8):
        result.append(single_line[i:i+8])
    result_string = '\n'.join(result)
    return result_string


def main():
    if len(sys.argv) != 3:
        print("Usage: python3 payloadcheck.py <payload_file> <windbg_file>")
        return
    payload_file = sys.argv[1]
    windbg_file = sys.argv[2]
    
    try:
        with open(windbg_file, 'r') as file:
            windbg_output = file.read()
    except FileNotFoundError:
        print(f"File not found: {windbg_file}")
        return

    try:
        with open(payload_file, 'r') as file:
            payload_output = file.read()
    except FileNotFoundError:
        print(f"File not found: {payload_file}")
        return
    
    processed_output = process_windbg_output(windbg_output)
    processed_windbg = revert_little_endianess(processed_output)
    processed_payload = process_payload_string(payload_output)
    nop_bytes = get_user_number()
    if (nop_bytes > 0):
        processed_windbg = shift_characters(processed_windbg, nop_bytes*2)
    result = compare_strings(processed_payload, processed_windbg)
    print(result)

if __name__ == "__main__":
    main()

