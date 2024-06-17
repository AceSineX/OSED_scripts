#!/usr/bin/python3
import sys

# Copy/Paste windbg `dd esp` output (or wherever your overflow lands) and check
# if the characters are mangled/missing/etc.
#
# This tool was written while studying for the OSED exam. It is provides sanity 
# check for ensuring that there are no bad/mangled characters. Only for QoL.
# 
#   Usage : python3 badcharscheck.py /path/to/file <starting_hex_char> <ending_hex_char>
#   Example : python3 badcharscheck.py ./windbgoutput.txt 41 ef
#
#  Author AceSineX
#

proper_sequence = "0102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f202122232425262728292a2b2c2d2e2f303132333435363738393a3b3c3d3e3f404142434445464748494a4b4c4d4e4f505152535455565758595a5b5c5d5e5f606162636465666768696a6b6c6d6e6f707172737475767778797a7b7c7d7e7f808182838485868788898a8b8c8d8e8f909192939495969798999a9b9c9d9e9fa0a1a2a3a4a5a6a7a8a9aaabacadaeafb0b1b2b3b4b5b6b7b8b9babbbcbdbebfc0c1c2c3c4c5c6c7c8c9cacbcccdcecfd0d1d2d3d4d5d6d7d8d9dadbdcdddedfe0e1e2e3e4e5e6e7e8e9eaebecedeeeff0f1f2f3f4f5f6f7f8f9fafbfcfdfeff"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"

###
def putLineInOrder(ln):
    splitted = ln.split()
    ordered = ""
    for element in splitted[1:5]:
    # Check if valid
        if len(element) != 8:
            print("Invalid element found, exitting")
            quit
        ordered = ordered + element[6:] + element[4:6] + element[2:4] + element[:2]
    return(ordered)
###

# In order to avoid split running into wrong position
# We take advantage of characters being in order.
def findPos(character):
    return int(character, 16)*2-2

# We start with the sequence from 01 to ff, this function
# edits that sequence from a starting to an ending character
def editSequence(startingChar, endingChar="ff"):
    edited_sequence = proper_sequence[findPos(startingChar):findPos(endingChar)+2]
    return edited_sequence

## BUG fixed, if starting character is missing, we have an endless loop.
## This function fixes that.
def firstCharPresent(sequence_found, starting_char):
    while(sequence_found[0:2] != starting_char):
        sequence_found = sequence_found[2:]
        if(len(sequence_found) == 0):
            return False
    return True

def numOfCharPresent(sequence_found, starting_char):
    num_of_chars_not_present = 0
    #print(f"Original sequence found : {sequence_found}")
    while(not firstCharPresent(sequence_found, starting_char)):
        num_of_chars_not_present = num_of_chars_not_present + 1
        #print(f"Updated sequence : {sequence_found}")
        # update starting character
        starting_char = format((int(starting_char, 16) + 1), 'x')
        if(len(starting_char) == 1):
            starting_char = "0" + starting_char
            print(f"Change of starting char to : \"{starting_char}\"")
        if(len(starting_char) == 3):
            print("Couldn't find a single match")
            print(f"Was about to look for \"{starting_char}\"")
            print("Exiting")
            quit()
    return num_of_chars_not_present


sequence_expected = proper_sequence
starting_char = "01"
ending_character = "ff"
if(len(sys.argv) == 2):
    path = sys.argv[1]
    print(f"Looking for : {YELLOW}{sequence_expected}{RESET}")
### Custom Starting Argument
elif(len(sys.argv) == 3):
    path = sys.argv[1]
    if(len(sys.argv[2]) != 2):
        print("Incorrect second argument")
        print("Second Argument should be the starting byte E.G. 41")
        print("Usage: python3 badcharscheck.py /path/to/file 41")
        quit()
    starting_char = sys.argv[2]
    print(proper_sequence[findPos(starting_char):findPos(starting_char)+2])
    sequence_expected = editSequence(starting_char)
    print(f"Looking for : {YELLOW}{sequence_expected}{RESET}")
### Custom Starting And Ending Argument
elif(len(sys.argv) == 4):
    path = sys.argv[1]
    if(len(sys.argv[2]) != 2):
        print("Incorrect second argument")
        print("Second Argument should be the starting byte E.G. 41")
        print("Usage: python3 badcharscheck.py /path/to/file 41")
        quit()
    starting_char = sys.argv[2]
    if(len(sys.argv[3]) != 2):
        print("Incorrect second/third argument")
        print("Second Argument should be the starting byte E.G. 41")
        print("Third Argument should be the ending byte E.G. 61")
        print("Usage: python3 badcharscheck.py /path/to/file 41 61")
        quit()
    ending_character = sys.argv[3]
    sequence_expected = editSequence(starting_char, ending_character)
    print(f"Looking for : {YELLOW}{sequence_expected}{RESET}\n")
else:
    print("Incorrect amount of arguments, Please provide path to file")
    print("Usage: python3 badcharscheck.py /path/to/file")
    print("Usage: python3 badcharscheck.py /path/to/file 41")
    print("Usage: python3 badcharscheck.py /path/to/file 41 61")
    quit()


blob = open(path, 'r')
line = blob.readline()
sequence_found = ""
while(line):
    sequence_found = sequence_found + putLineInOrder(line)
    line = blob.readline()

## BUG (fixed), if starting character is missing, we have an endless loop.
## Solved
num_of_starting_chars_not_found = numOfCharPresent(sequence_found, starting_char)
offset = num_of_starting_chars_not_found * 2
if(offset != 0):
    sequence_found = sequence_found[offset:]
    # update starting character
    starting_char = format((int(starting_char, 16) + 1), 'x')
    if(len(starting_char) == 1):
        starting_char = "0" + starting_char

print(f"Sequence found : {YELLOW}{sequence_found}{RESET}\n")

substring_found = sequence_found
substring = ""
all_good_flag = True
j = 0
i = 0
while i+2 <= len(sequence_expected):
    
    substring = substring + sequence_expected[i:i+2]

    if substring not in substring_found:
        j = j + i
        if(len(substring) == 4):
            print(f"{YELLOW}[{RED}!{YELLOW}]{RESET} Missing bytes: either {YELLOW}[{RED}{substring[0:2]}{YELLOW}]{RESET} or {YELLOW}[{RED}{substring[2:4]}{YELLOW}]{RESET}, at position [{j//2}]")
        else:
            print(f"{YELLOW}[{RED}!{YELLOW}]{RESET} Missing bytes: {YELLOW}[{RED}{sequence_expected[i:i+2]}{YELLOW}]{RESET}, at position [{j//2}]")
        
        substring = ""
        sequence_expected = sequence_expected[i+2:]
        all_good_flag = False
        substring_found = substring_found[i:]
        
        i = -2
    i = i + 2


if (all_good_flag):
    print("Perfect match, no bad characters!")
