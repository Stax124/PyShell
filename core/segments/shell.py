import os

def main(segment):
    
    shell = os.environ.get('SHELL', "")
    
    if shell:
        return shell, False
    else:
        return "", True