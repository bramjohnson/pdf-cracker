import argparse
import os
import subprocess
from pdf2hash import PdfParser
from pypdf import PdfReader

# Set up argument parser
parser = argparse.ArgumentParser(description="Process a single PDF file.")

parser.add_argument("file", type=str, help="Path to the PDF file")
parser.add_argument("--password", type=str, help="Password", required=False)

# Parse the command-line arguments
parser.parse_args()
args = parser.parse_args()

reader = PdfReader(args.file)
   
if reader.is_encrypted:
    if args.password is None:
        raise ValueError("The PDF is password-protected, and no password was provided.")
        
    # Attempt to decrypt with the provided password
    if reader.decrypt(args.password) == 0:
        raise ValueError("The provided password is incorrect.")
    
num_pages = len(reader.pages)
title = reader.metadata.title if reader.metadata.title else "Unknown"
author = reader.metadata.author if reader.metadata.author else "Unknown"

print({
    "title": title,
    "author": author,
    "num_pages": num_pages
})