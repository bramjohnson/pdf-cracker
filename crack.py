# https://medium.com/@ekiser_48014/python-penetration-testing-using-hashcat-and-python-to-crack-windows-passwords-34cb4f052bf3
# Tool that simplifies the Hashcat cracking process.

import argparse
import os
import subprocess
from pdf2hash import PdfParser
from pypdf import PdfReader

hash_modes = {
    '%PDF-1.1': 10400,
    '%PDF-1.2': 10400,
    '%PDF-1.3': 10400,
    '%PDF-1.4': 10500,
    '%PDF-1.5': 10500,
    '%PDF-1.6': 10500,
    # 'PDF 1.7 Level 3': 10600,
    '%PDF-1.7': 10700,
}

def check_pdf_file(file_path):
    # Check if the file has a PDF extension
    if not file_path.lower().endswith('.pdf'):
        raise ValueError("The provided file does not have a .pdf extension")
    
    # Check if the file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist")
    
def get_pdf_version(file_path):
    with open(file_path, 'rb') as file:
        return PdfReader(file).pdf_header

def get_pdf_info(file_path, password=None):
    # Open and read the PDF file using PyPDF2
   reader = PdfReader(file_path)
   
   if reader.is_encrypted:
        if password is None:
            raise ValueError("The PDF is password-protected, and no password was provided.")
            
        # Attempt to decrypt with the provided password
        if reader.decrypt(password) == 0:
            raise ValueError("The provided password is incorrect.")
        
        num_pages = len(reader.pages)
        title = reader.metadata.title if reader.metadata.title else "Unknown"
        author = reader.metadata.author if reader.metadata.author else "Unknown"

        return {
            "title": title,
            "author": author,
            "num_pages": num_pages
        }
        
def run_hashcat(command, hash_text):
    # Execute hashcat command using subprocess
    try:
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        password = None
        empty_count = 0
        for line in iter(process.stdout.readline, ''):
            line = line.decode().rstrip().strip()
            if hash_text in line:
                password = line.split(f"{hash_text}:")[1]
            if line.startswith('Status'):
                cracked_huh = line.endswith('Cracked')
                exhausted_huh = line.endswith('Exhausted')
                if cracked_huh:
                    print("Cracked the PDF!")
                if exhausted_huh:
                    print("All out of attempts...")
            if line.startswith('Time.Estimated'):
                print(line)
            if line.startswith('Progress'):
                print(line)
            if line.startswith('Candidates.'):
                print(line)
            if line.startswith('Stopped:'):
                print(line)
                break
            if line == '':
                empty_count += 1
            else:
                empty_count = 0 
            if empty_count > 10:
                print("♾ Subprocess running in an infinite loop, exiting...")
                return
        process.wait()
        return password
    except subprocess.CalledProcessError as e:
        print(f"Error executing hashcat command: {e}")

def get_hashcat_mode(file):
    check_pdf_file(file)
    pdf_version = get_pdf_version(file)
    
    hash_type = pdf_version.upper()
    # Check if entered hash type is valid
    if hash_type.upper() not in hash_modes:
        print(f"Invalid hash type {hash_type}. Supported hash types are: NTLM, SHA1, SHA256, and MD5.")
        exit()
        
    # Get the hash mode from the dictionary
    return hash_modes[hash_type.upper()]

def use_password(file, password):
    if password is None:
        print("👎 NO PASSWORD FOUND FOR CURRENT WORDS/RULES")
        return
    
    print(f"🎉🚨 FOUND PASSWORD {password} 🚨🎉")
    
    pdf_info = get_pdf_info(file, "iloveu!")

    # # Print out basic PDF information
    print(f"PDF Title: {pdf_info['title']}")
    print(f"PDF Author: {pdf_info['author']}")
    print(f"Number of Pages: {pdf_info['num_pages']}")
    
def get_hashcat_command(args, hash_mode, hash_text):
    if args.type:
        if args.type == "easy":
            return f"hashcat -m {hash_mode} -a 0 -r best64.rule -O --potfile-disable --status --remove {hash_text} words.txt"
        if args.type == "medium":
            return f"hashcat -m {hash_mode} -a 0 -r best64.rule -O --potfile-disable --status --remove {hash_text} rockyou.txt"
        if args.type == "hard":
            return f"hashcat -m {hash_mode} -a 0 -r onerule.rule -O --potfile-disable --status --remove {hash_text} words.txt"
        if args.type == "expert":
            return f"hashcat -m {hash_mode} -a 0 -r onerule.rule -O --potfile-disable --status --remove {hash_text} rockyou.txt words.txt"
    if args.dictionary and args.rules:
        return f"hashcat -m {hash_mode} -a 0 -r {args.rules} -O --potfile-disable --status --remove {hash_text} {args.dictionary}"
    if args.dictionary:
        return f"hashcat -m {hash_mode} -a 0 -r best64.rule -O --potfile-disable --status --remove {hash_text} {args.dictionary}"
    if args.rules:
        return f"hashcat -m {hash_mode} -a 0 -r {args.rules} -O --potfile-disable --status --remove {hash_text} words.txt"
    return f"hashcat -m {hash_mode} -a 0 -r onerule.rule -O --potfile-disable --status --remove {hash_text} rockyou.txt words.txt"
    

def parse_custom(args):
    hash_mode = get_hashcat_mode(args.file)
    hash_text = PdfParser(args.file).parse()
    
    hashcat_command = get_hashcat_command(args, hash_mode, hash_text)
    print(hashcat_command)
    
    password = run_hashcat(hashcat_command, hash_text)
    use_password(args.file, password)

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process a single PDF file.")
    
    parser.add_argument("file", type=str, help="Path to the PDF file")
    parser.add_argument("--dictionary", type=str, help="Path to the word list", required=False)
    parser.add_argument("--rules", type=str, help="Path to the rules file", required=False)
    parser.add_argument("--type", type=str, help="Complexity of rules and word lists", required=False)
    parser.set_defaults(func=parse_custom)
    
    # Parse the command-line arguments
    parser.parse_args()
    args = parser.parse_args()
    args.func(args)
    
if __name__ == "__main__":
    main()