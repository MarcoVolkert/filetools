#http://docs.python-guide.org/en/latest/scenarios/scrape/
#http://stackabuse.com/download-files-with-python/

from lxml import html
import requests
import os
    
def getHrefs(mainpage, subpage,css='',contains=''):
    page = requests.get(mainpage+subpage)
    tree = html.fromstring(page.content)
    aList = tree.xpath('//a'+css)
    hrefs = [ x.get("href") for x in aList]
    if not contains=='': hrefs = [x for x in hrefs if contains in x]
    #print(hrefs)
    return hrefs       
    
def downloadPics(mainpage,name):
    maindest = 'F:\\Bilder\\bearbeitung\\webpic\\'
    mainname = mainpage.replace('http://','').replace('.com','')
    namedest=maindest+mainname+'\\'+name
    if not os.path.isdir(namedest): os.makedirs(namedest)
    
    galleries = getHrefs(mainpage,'/model/'+name+'/',contains='gallery')
    for i,gallery in enumerate(galleries):
        pics=getHrefs(mainpage,gallery,css='[@class="fancybox"]')
        dest=namedest+'\\'+str(i)
        print(dest)
        if not os.path.isdir(dest): os.makedirs(dest)
        for pic in pics:
            downloadFile(pic,dest)
        
def downloadFile(picUrl, dest):        
    page = requests.get(picUrl)
    filename=dest+'\\'+picUrl.split('/')[-1]
    #print(filename)
    with open(filename, 'wb') as f:  
        f.write(page.content)
        
def downloadMulti():
    #names=['katy-rios','kiara-lord','sara-kay','vinna-reed','alice-march']
    #mainpage='http://alsscangirlz.com'
    #for name in names:
    #    downloadPics(mainpage,name)
    #names=['milla','jessica','foxy-di','silvie','angelica']
    #mainpage='http://matrixteens.com'
    #for name in names:
    #    downloadPics(mainpage,name)
    #names=['luba','selma','foxy-di','larisa-a','irishka','nikola','vera']
    #mainpage='http://xmodelpics.com'
    #for name in names:
    #    downloadPics(mainpage,name)    
    names=['daniel-sea']
    mainpage='http://www.ametart.com'
    for name in names:
        downloadPics(mainpage,name)       