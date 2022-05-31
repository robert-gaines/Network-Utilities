#!/usr/bin/env python3

from urllib.parse import urljoin
from bs4 import BeautifulSoup
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Crawler():

    def __init__(self,targets):
        self.visited   = []
        self.to_visit  = targets

    def GetSequence(self,url):
        return requests.get(url,verify=False).text

    def GetLinks(self,url,html):
        SoupObject = BeautifulSoup(html,'html.parser')
        for link in SoupObject.find_all('a'):
            LinkPath = link.get('href')
            if(LinkPath and LinkPath.startswith('/')):
                CurrentPath = urljoin(url,LinkPath)
            yield CurrentPath

    def AddURL(self,url):
        if(url not in self.visited and url not in self.to_visit):
            self.to_visit.append(url)

    def Crawl(self,url):
        html = self.GetSequence(url)
        for entry in self.GetLinks(url,html):
            self.AddURL(entry)

    def run(self):
        while(self.to_visit):
            url = self.to_visit.pop(0)
            try:
                print("[~] Crawling: %s " % url)
                self.Crawl(url)
            except Exception as e:
                print("[!] Error: %s " % e)
            finally:
                self.visited.append(url)
        print(self.visited)

if(__name__ == '__main__'):
    targets = ["https://greenclouddefense.com/"]
    c = Crawler(targets)
    c.run()