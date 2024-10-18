python -m venv venv
pip install requirements.txt
python ./crack.py <FILE.PDF> (options)

Download: words.txt, rockyou.txt

Preconfigured hashcat commands:
`type`: easy, medium, hard, expert

EX
python ./crack.py ./my.pdf --type easy
python ./crack.py ./my.pdf --type hard

EX
python ./crack.py ./my.pdf --dictionary ./words.txt --rules ./best64.rule