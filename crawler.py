import urllib2
import re
import csv

from bs4 import BeautifulSoup

global_link = 'http://www.flohmarkt.at/nachhilfeboerse/index.php?start={}'
STARTS_WITH = 1520 # Advert number
ADVERTS_PER_PAGE = 20 # constante, look at the http://www.flohmarkt.at/nachhilfeboerse


def get_phone(list_of_lines):
    for line in list_of_lines:
        if 'Telefon:' in line:
            phohe = re.sub('Telefon:', '', line)
            
            return re.sub('\t', '', phohe) # \t takes one char in table 
    
    return 'N/A'

def get_city(list_of_lines):
    for line in list_of_lines:
        if 'Standort:' in line:
            return re.sub('Standort:', '', line)
    
    return 'N/A'

def get_email(list_of_lines):
    reg_exp_mail = '^(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])+$'

    for line in list_of_lines:
        for word in line.split(' '):
            if re.match(reg_exp_mail, word):
                return word
    
    return 'N/A'

def parse_detail(detail_link):
    result = {}
    response = urllib2.urlopen(detail_link)
    soup = BeautifulSoup(response.read())
    style = "margin:10px 0 0 0;background-color:#F5F8FB;padding:5px 5px 5px 15px;border:1px solid #CBDDED;font-size:13px;"
    divs = soup.find('div', {'style': style})
    lines = divs.get_text().split('\n')

    result['phone'] = get_phone(lines).encode('utf-8')
    result['city'] = get_city(lines).encode('utf-8') 
    result['email'] = get_email(lines).encode('utf-8')
    
    return result

def find_adverts(paginator):
    response = urllib2.urlopen(global_link.format(str(paginator)))
    soup = BeautifulSoup(response.read())
    
    return soup.find_all('div',{'class': 'pMitte'})

def save_data(data):
    with open('adverts.csv', 'wb') as f:
        fieldnames = ['link', 'subject', 'city', 'phone', 'email']
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        writer.writeheader()
        for row in data:
            writer.writerow(row)

def collect_detail(stack):
    result = []
    for anchor in stack:
        link = anchor.get('href')
        detail = parse_detail(link)

        detail['subject'] = anchor.get_text().encode('utf-8')
        detail['link'] = link.encode('utf-8')
        result.append(detail)
    
    return result

def find_links(content):
    advert_anchors = []
    
    for advert in content:
        anchors = advert.find_all('a')

        advert_anchors.append(anchors[0])

    return advert_anchors

def crowler():
    paginator = STARTS_WITH
    adverts = find_adverts(paginator)
    results = []
    
    while adverts:
        try:
            advert_anchors = find_links(adverts)
            
            results.extend(collect_detail(advert_anchors))
        except urllib2.URLError, urllib2.HTTPError:
            adverts = False
        else:   
            paginator += ADVERTS_PER_PAGE
            adverts = find_adverts(paginator)
    
    save_data(results)


if __name__ == '__main__':
    crowler()

