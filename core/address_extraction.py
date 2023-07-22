import re

def extract_address(text):
    # Define the list of keywords to look for
    keywords = ['quartier', 'rue', 'cours', 'allée', 'avenue', 'boulevard', 'place', 'quais', 'arrêt', 'quai', 'impasse', 'voie', 'secteur']
    
    # Convert all keywords to lowercase
    keywords = [keyword.lower() for keyword in keywords]
    
    # Define the regular expression pattern to match the keywords
    pattern_keywords = r"\b(?:{})\b".format('|'.join(keywords))
    
    # Use the regular expression to find all matches in the text
    matches = re.finditer(pattern_keywords, text, re.IGNORECASE)
    
    addresses = []
    # Iterate over all matches
    for match in matches:
        # Get the start position of the match
        start = match.start()
        
        not_valid_address = True
        address = ''
        i = 0
        counter = 0
        max_iter = 10
        while not_valid_address and max_iter > 0:
            words = text[start:].split()[0:4+(i*3)]
            
            flag = False
            
            for word in words:
                counter += 1
                # Check if the word starts with a capital letter
                if word[0].isupper():
                    address = ' '.join(text[start:].split()[0:counter])
                    i += 1
                    flag = True
                if word[-1] in [',', ':', '.', '\n', "-", '*', ';', '?', '!'] or word[0] in [',', ':', '.', '\n', '-', '*', ';', '?', '!']:
                    not_valid_address = False
                    break
            
            
            if flag :
                not_valid_address = False
            max_iter -= 1
        if address :        
            addresses.append(re.split(f"[.,;:]", address)[0])
    return addresses
