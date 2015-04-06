from bs4 import BeautifulSoup
import os, fnmatch

def analyze_view(html):
    """
    Analyzes html and returns all the strings.
    """

    soup = BeautifulSoup(html)

    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()    # rip it out

    # get text
    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())

    # remove angular tags
    lines = [line for line in lines if line[:2] != '{{' and line[-2:] != '}}']

    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)

    return text.encode('utf-8')

if __name__ == "__main__":
    matches = []
    for root, dirnames, filenames in os.walk('/Users/j/dev/CheckUp-Frontend', topdown=True):
        for filename in fnmatch.filter(filenames, '*.html'):
            matches.append(os.path.join(root, filename))

    output = open('output.txt', 'w')

    for viewfile in matches:
        print viewfile
        f = open(viewfile, 'r')
        text = analyze_view(f)
        output.write(text)
