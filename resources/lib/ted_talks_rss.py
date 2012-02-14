"""
Grab new talks from RSS feed. Yes we can just add an rss: source in XBMC,
but this allows us a little more power to tweak things how we want them,
so keep it for now.
"""

import urllib2
import time
try:
    # >=Eden
    from multiprocessing import Pool
    do_multi_threading = True
except ImportError:
    # < Eden
    do_multi_threading = False

import plugin
try:    
    from elementtree.ElementTree import fromstring
except ImportError:
    from xml.etree.ElementTree import fromstring

def getDocument(url):
    """
    Return document at given URL.
    """
    usock = urllib2.urlopen(url)
    try:
        return usock.read()
    finally:
        usock.close()

def getTalkDetails(item):
    """
    Return the details from an RSS <item> tag soup.
    """
    title = item.find('./{http://www.itunes.com/dtds/podcast-1.0.dtd}subtitle').text # <title> tag has unecessary padding strings
    author = item.find('./{http://www.itunes.com/dtds/podcast-1.0.dtd}author').text
    pic = item.find('./{http://search.yahoo.com/mrss/}thumbnail').get('url')
    duration = item.find('./{http://www.itunes.com/dtds/podcast-1.0.dtd}duration').text
    plot = item.find('./{http://www.itunes.com/dtds/podcast-1.0.dtd}summary').text
    link = item.find('./enclosure').get('url')
    talkID = item.find('./guid').text.split(':')[-1]
    
    # Get date as XBMC wants it
    pub_date = item.find('./pubDate').text[:-6] # strptime can't handle timezone info.
    try:
        date = time.strptime(pub_date, "%a, %d %b %Y %H:%M:%S")
    except ValueError, e:
        print '[%s] %s Could not parse date: %s' % (plugin.__plugin__, __name__, pub_date)
        print e
        date = time.localtime()
    date = time.strftime("%d.%m.%Y", date)
        
    return {'title':title, 'author':author, 'thumb':pic, 'plot':plot, 'duration':duration, 'date':date, 'link':link, 'id':talkID}


class NewTalksRss:
    """
    Fetches new talks from RSS stream.
    """
 
    def getNewTalks(self):
        """
        Returns talks as dicts {title:, author:, thumb:, date:, duration:, link:}.
        """
        
        sd_rss_url = "http://feeds.feedburner.com/tedtalks_video"
        hd_rss_url = "http://feeds.feedburner.com/TedtalksHD"
        rss_urls = [sd_rss_url, hd_rss_url] # Prefer HD, but get SD if that's all there is (my friends)
        
        document_fetchers = []
        if do_multi_threading:
            pool = Pool(processes=1) # Maybe it would be better to fetch them simultaneously?
            for url in rss_urls:
                result = pool.apply_async(getDocument, [url])
                document_fetchers.append(lambda x: result.get(30))
            pool.close()
        else:
            for url in rss_urls:
                document_fetchers.append(lambda x: getDocument(url))

        talksByTitle = {}
        for documentFetcher in document_fetchers:
            rss = documentFetcher(None) # Is this evil? We have to pass something into the lambda.
            for item in fromstring(rss).findall('channel/item'):
                talk = getTalkDetails(item)
                talksByTitle[talk['title']] = talk
        
        if do_multi_threading:
            pool.join()
        
        return talksByTitle.itervalues()

