from VTK_Code import *
import webbrowser
import requests
import xml.etree.ElementTree as ET

def wolfram():
    dbg = True
    vtkWolframAppID = '&appid=H2VK7E-WLKUW5PTX3'
    vtkWolframURL = "http://api.wolframalpha.com/v2/query?input="
    #while 1:
    print "Ask a question. Type control-c (ctrl and c at the same time, a.k.a ^c) to quit."
    try:
        line = sys.stdin.readline()
    except KeyboardInterrupt:
        return None
    #if not line:
    #    break
    if dbg: print line
    aQueryString = line.replace('  ',' ').strip().replace(' ','+')
    if dbg: print "Your query string is",aQueryString
    # get the answer from google and display it
    webbrowser.open_new('https://www.google.com/search?q='+aQueryString)
    # get the answer from wolfram alpha and display it
    webbrowser.open_new('http://www.wolframalpha.com/input/?i='+aQueryString)
    fullWolframQuery = vtkWolframURL+aQueryString+vtkWolframAppID
    if dbg: print fullWolframQuery
    return requests.get(fullWolframQuery)


if __name__ == "__main__":
    result = wolfram()
    root = ET.fromstring(result.content)
    with open("wolfram.xml", "w") as text_file:
        text_file.write("%s" % result.content)
    
