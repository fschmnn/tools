import hashlib
import re
import unicodedata

def simplehash(token,n=64):
    """Create an hash id with n digits
    
    This function removes all special characters and converts accents 
    to the closest ascii. The result is less a unique ID, but rather a 
    way to match similar strings with negligible differences. The 
    maximum length of the string is 64
    """
    
    # make sure all characters are lower case
    string = str(token).lower()
    # replace accents with the closest ascii
    string = ''.join(c for c in unicodedata.normalize('NFD', string) if unicodedata.category(c) != 'Mn')
    # remove non [^0-9a-zA-Z] characters
    string = re.sub('[^0-9a-zA-Z]+','',string)
    
    return hashlib.sha256(string.encode('ascii')).hexdigest()[:n]


