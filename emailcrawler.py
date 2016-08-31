#! /usr/bin/python
#Written in conjunction with Kay Avila and Ewan Smith!

#import our modules
import urllib
import urllib2
import urlparse
import re
import sys
import ssl
import socket
import time
from bs4 import BeautifulSoup

url = 'http://www.aegon.co.uk'
#we need to track urls still to visit
#we also need to track urls we have visitied so we dont go there again

emails_seen = []
emails_unseen = []
urls = [url]
visitedurls = []
error_urls = []
start_time = time.time()
DEBUG = False # set to True or False

excluded_suffixes_match = re.compile(r'(xlsx?|docx?|pdf|jpg|gif|png)$')

# Loop through the urls we need to process
while urls:

    url = urls.pop()

    if DEBUG:
        print "Looping through for url - '%s'" % url

    try:
        htmltext = urllib2.urlopen(url, timeout=3).read()
        soup = BeautifulSoup(htmltext, "html.parser")
        tld = '/'.join(url.split('/')[:3])
    except urllib2.HTTPError as e:
        error_urls.append((url, 'HTTPError %s' % e.code))
        continue
    except urllib2.URLError:
        error_urls.append((url, 'URLError'))
        continue
    except ssl.SSLError:
        error_urls.append((url, 'SSLError'))
    except socket.timeout:
        error_urls.append((url, 'Socket timeout'))

    # Loop through all the 'a' tags and store email addresses and links we haven't seen
    for tag in soup.findAll('a', href=True):

        # Handle any email address links
        if tag['href'].startswith("mailto"):
           email = tag['href'].split(':')[1]
           email = email.lower()

           if email not in emails_seen:
               emails_seen.append(email)
               if DEBUG:
                    print " > Appending email - '%s'" % email

        # Handle anything that isn't an email address
        else:
            # If the TLD doesn't exist, add it, also remove any #anchor
            link = urlparse.urljoin(url, tag['href'])
            link = link.split('#')[0]

            link = link.lower()

            # If the link ends in 'pdf', ignore it
            if excluded_suffixes_match.search(link):
                if DEBUG:
                    print " > ** Excluded URL - '%s'" % link
                continue

            if tld in link and link not in visitedurls:
                urls.append(link)
                visitedurls.append(link)
                if DEBUG:
                    print " > Appending URL - '%s'" % link

print "==============================================================="
print "=				Stats"
print "=		Visited URL count:", len(visitedurls)
print "=		Found email count:", len(emails_seen)
print "="
print "=		URL Errors Encountered: ", len(error_urls)
print "="		
print("=                Time to run: %s seconds" % (time.time() - start_time))
print "==============================================================="

for email in emails_seen:
    print email

# Uncomment section below to see urls which error
#if error_urls:
#    print "\nURLs with errors:"
#    for u in error_urls:
#        url, error = u
#        print "%s - %s" % (url, error)
