import requests
import urllib
import re

'''response = requests.get(url)
response.encoding = "utf-8"
a = response.text
with open('index.html', 'bw') as output_file:
  output_file.write(bytes(a, encoding="utf-8"))'''

def download_file(url, name):
        res = urllib.request.urlopen(url)
        res = res.read().decode("utf-8")
        with open(name, 'bw') as output_file:
            output_file.write(bytes(res, encoding="utf-8"))
        print("File "+name+" download")
