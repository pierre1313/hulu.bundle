import re, random

HULU_PLUGIN_PREFIX   = "/video/hulu" 
HULU_BASE_URL        = "http://www.hulu.com/"
HULU_SEARCH_URL      = HULU_BASE_URL + "search/"

CACHE_INTERVAL       = 3600 # HTTP cache interval in seconds
LONG_CACHE_INTERVAL  = 750000 # this is the cache time for show/movie details that don't really change
MAX_RESULTS          = "150"  # max results for lists

HULU_HTML_ITEMS     = "http://www.hulu.com/videos/slider?items_per_page=%s&page=%s&season&show_id=%s&sort=original_premiere_date&type=%s" # max_results % page %show_id % episode/clip
HULU_HTML_ITEMS_alt = "http://www.hulu.com/videos/slider?items_per_page=%s&page=%s&season&show_id=%s&sort=original_premiere_date&category=%s" # max_results % page %show_id % episode/clip

HULU_RECENT_RSS = "http://rss.hulu.com/HuluRecentlyAddedShows?format=xml"

huluListings = 'http://www.hulu.com/browse/search?keyword=&alphabet=All&family_friendly=0&closed_captioned=0&channel=%s&subchannel=&network=All&display=%s&decade=All&type=%s&view_as_thumbnail=true&block_num=%s'
huluShowInfo = 'http://www.hulu.com/shows/info/%s' #by show alpha id
huluVideoInfo = 'http://www.hulu.com/videos/info/%s' #by show id #

HULU_EMBEDDED = 'http://www.hulu.com/site-player/playerembedwrapper.swf?referrer=%s&eid=%s&st=0&et=0&it=&ml=0&siteHost=http://www.hulu.com'

HULU_ASSETS = 'http://r.hulu.com/videos?eid=%s&include=video_assets'
HULU_AGECHECK = 'http://www.hulu.com/users/age_check/%s'

YAHOO_NAMESPACE  = {'media':'http://search.yahoo.com/mrss/'}
# Default artwork and icon(s)
PLUGIN_ARTWORK      = 'art-default.jpg'
PLUGIN_ICON_DEFAULT = 'icon-default.png'
PLUGIN_ICON_PREFS   = 'icon-prefs.png'
  
TYI = '//img[@src="/images/icon-has-%s.gif"]/..'
TYICLIPS = '//table//li'

USER_AGENT = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2.12) Gecko/20101026 Firefox/3.6.12'

headers = {'User-Agent': USER_AGENT}
    
profilename = ''

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(HULU_PLUGIN_PREFIX, MainMenu, "Hulu", PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  MediaContainer.title1    = 'Hulu'
  MediaContainer.viewGroup = 'List'
  MediaContainer.art       = R(PLUGIN_ARTWORK)
  
  DirectoryItem.thumb = R(PLUGIN_ICON_DEFAULT)
  
  HTTP.Headers['User-Agent'] = USER_AGENT
  HTTP.CacheTime = CACHE_INTERVAL

  loginResult = HuluLogin()
  Log("Login success: " + str(loginResult))
  
####################################################################################################  

import urllib2, httplib
class SmartRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_404(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_404(
            self, req, fp, code, msg, headers)
        Log(msg)
        return result

    def http_error_302(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_302(
            self, req, fp, code, msg, headers)
        result.status = code
        return result
        
    def http_error_301(self, req, fp, code, msg, headers):
        result = urllib2.HTTPRedirectHandler.http_error_301(
            self, req, fp, code, msg, headers)
        result.status = code
        return result
        
####################################################################################################  
def HuluLogin():
  username = Prefs["email"]
  password = Prefs["password"]
  if (username != None) and (password != None):
    resp = HTTP.Request("https://secure.hulu.com/account/authenticate?" + str(int(random.random()*1000000000)), headers={"Cookie":"sli=1; login=" + username + "; password=" + password + ";"},cacheTime=0).content
    if resp == "Login.onComplete();":
      Dict['HULU_username'] = HTML.ElementFromURL("https://www.hulu.com/profile",cacheTime=0,headers={"Cookie":HTTP.GetCookiesForURL('http://www.hulu.com/')}).xpath("//td[@class='content']/input[@id='username']")[0].get('value')
      HTTP.Headers['Cookie'] = HTTP.GetCookiesForURL('https://secure.hulu.com/')
      for item in HTTP.GetCookiesForURL('https://secure.hulu.com/').split(';'):
        if '_hulu_uname' in item :
          Dict['_hulu_uname'] = item[13:]
        if '_hulu_uid' in item :
          Dict['_hulu_uid'] = item[11:]
      return True
    else:
      return False
  else:
    return False
 
####################################################################################################
def UpdateCache():
  walkDir(myhulu(sender=""), 1, 1, recurse=True)
  walkDir(channels(sender=""), 1, 1, recurse=True)
  walkDir(feeds(sender=""), 1, 1, recurse=True)
  walkDir(menumovies(sender=""), 1, 1, recurse=True)
  walkDir(menupopular(sender=""), 1, 1, recurse=True)
  walkDir(menurecent(sender=""), 1, 1, recurse=True)

def walkDir(dir, cacheLevel, currentLevel, recurse=False):
  for item in dir:
    try:
      if currentLevel <= cacheLevel and ObjectManager.ObjectHasBase(item, Function):   
        if recurse:
          pass
        else:
          pass
    except:
      pass
        
####################################################################################################
def MainMenu():
  dir = MediaContainer(httpCookies=HTTP.GetCookiesForURL('http://www.hulu.com/profile'))
  dir.noCache=1
  dir.Append(Function(DirectoryItem(myhulu, title="My Hulu")))
  dir.Append(Function(DirectoryItem(channels, L("TV")), itemType="tv", display="Shows%20with%20full%20episodes%20only"))
  dir.Append(Function(DirectoryItem(channels, L("Movies")), itemType="movies", display="Full%20length%20movies%20only"))
  dir.Append(Function(DirectoryItem(menupopular, title="Popular Videos")))
  dir.Append(Function(DirectoryItem(menurecent, title="Recently Added")))
  dir.Append(Function(DirectoryItem(feeds, title=L("Highest Rated Videos")), feedUrl="http://www.hulu.com/feed/highest_rated/videos"))
  dir.Append(Function(DirectoryItem(feeds, title=L("Soon-to-Expire Videos")), feedUrl="http://www.hulu.com/feed/expiring/videos"))
  dir.Append(Function(InputDirectoryItem(Search, title=L("Search Hulu"), prompt=L("Search Hulu"), thumb=R('search.png'))))
  dir.Append(PrefsItem(L("Preferences..."), thumb=R(PLUGIN_ICON_PREFS)))
  return dir  
  
def menupopular(sender):
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(feeds, L("Popular Videos Today")), feedUrl="http://rss.hulu.com/HuluPopularVideosToday?format=xml"))
  dir.Append(Function(DirectoryItem(feeds, L("Popular Videos This Week")), feedUrl="http://rss.hulu.com/HuluPopularVideosThisWeek?format=xml"))
  dir.Append(Function(DirectoryItem(feeds, L("Popular Videos This Month")), feedUrl="http://rss.hulu.com/HuluPopularVideosThisMonth?format=xml"))
  dir.Append(Function(DirectoryItem(feeds, L("Popular Videos of All Time")), feedUrl="http://rss.hulu.com/HuluPopularVideosAllTime?format=xml"))
  return dir
  
def menurecent(sender):
  dir = MediaContainer()        
  dir.Append(Function(DirectoryItem(ParseShowsRSS, L("Recently Added Shows")),feed = HULU_RECENT_RSS)) 
  dir.Append(Function(DirectoryItem(feeds, L("Recently Added Movies")), feedUrl="http://rss.hulu.com/HuluRecentlyAddedMovies?format=xml")) 
  dir.Append(Function(DirectoryItem(feeds, L("Recently Added Videos")), feedUrl="http://rss.hulu.com/HuluRecentlyAddedVideos?format=xml"))
  return dir
  
def myhulu(sender):
  loginResult = HuluLogin()  
  Log("myhulu Login success: " + str(loginResult))
  if loginResult:
    dir = MediaContainer(httpCookies = HTTP.GetCookiesForURL('http://www.hulu.com/profile'))
    dir.Append(Function(DirectoryItem(feeds, L("My Hulu Queue")), feedUrl="http://www.hulu.com/feed/queue/" + Dict['HULU_username'], feedType="videos", sort="reverse"))
    dir.Append(Function(DirectoryItem(feeds, L("My Hulu Show Recommendations")), feedUrl="http://www.hulu.com/feed/show_recommendations/" + Dict['HULU_username'], feedType="shows"))
    dir.Append(Function(DirectoryItem(feeds, L("My Hulu Video Recommendations")), feedUrl="http://www.hulu.com/feed/recommendations/" + Dict['HULU_username']))
    dir.Append(Function(DirectoryItem(ParseShowsRSS, L("My Hulu Subscriptions")), feed="http://www.hulu.com/feed/subscriptions/" + Dict['HULU_username']+"?format=xml"))
  else:
    dir = MessageContainer("User info required", "Please enter your Hulu email address and password in Preferences.")
  return dir
  
####################################################################################################
def list_shows(sender, channel, itemType, display):
  if itemType == 'tv':  entry_type = 'episode'
  elif itemType == 'movies':  entry_type = 'feature_film'
  dir = MediaContainer(title2=sender.itemTitle,httpCookies = HTTP.GetCookiesForURL('http://www.hulu.com/profile'))
  
  i = 0
  while 1:
    h = HTTP.Request(huluListings % (channel, display, itemType, i)).content
    if len(h) < 215:
      break
    rep = 'Element.update("show_list", "'
    if h.find(rep) == -1:
      rep = 'Element.replace("browse-lazy-load", '
    h = h.split('\n')[1].replace(rep,'').replace('");','').decode('unicode_escape')
    for s in HTML.ElementFromString(h).xpath('//a[@class="info_hover"]'):
      showUrl = s.get('href')
      title = s.xpath('img')[0].get('alt')
      thumb = "http://assets.hulu.com/shows/key_art_" + showUrl.split("?")[0].split("/")[-1].replace("-","_") + ".jpg"
      if entry_type == 'episode':
        dir.Append(Function(DirectoryItem(tv_shows_listings, title=title, thumb=thumb), showUrl=showUrl, fromType="html", entry_type=entry_type))
      elif entry_type == 'feature_film':
        dir.Append(Function(DirectoryItem(feature_film_info, title=title, thumb=thumb), showUrl=showUrl, fromType="html", entry_type=entry_type))
    i+=1
  return dir

####################################################################################################      
def feature_film_info(sender, showUrl, fromType="feed", entry_type="feature_film"):
  dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList",httpCookies=HTTP.GetCookiesForURL('https://secure.hulu.com'))
  try:
    resp = HTTP.Request(showUrl).content
    playUrl = showUrl
    
    request = urllib2.Request(playUrl, None, headers)
    opener = urllib2.build_opener(SmartRedirectHandler)
    f = opener.open(request)
    if f.status == 301 or f.status == 302:
      playUrl = re.findall('<meta property="og:url" content="([^&]+)"',HTTP.Request(f.url).content)[0].split('"')[0]
  except Ex.HTTPError, error:
    playUrl = re.findall('<meta property="og:url" content="([^&]+)"',error.content)[0].split('"')[0]
    
  api_address = "http://www.hulu.com/api/oembed.json?url="+playUrl
  try:
    jsonObj = JSON.ObjectFromURL(api_address)
  except:
    jsonObj = JSON.ObjectFromURL(api_address.rsplit('/')[0])
  eid = jsonObj['embed_url'].split('embed/')[1].split('/')[0]
    
  details = XML.ElementFromURL(HULU_ASSETS %eid)
  
  desc = details.xpath('//video/description')[0].text
  subtitle =  details.xpath('//video/copyright')[0].text
  duration =  int(float(details.xpath('//video/duration')[0].text)*1000)
  thumb = details.xpath('//video/thumbnail-url')[0].text
  art = ""
  rating =  float(details.xpath('//video/user-star-rating')[0].text)
  plusonly =  details.xpath('//video/is-plus-web-only')[0].text
  if (plusonly == 'true'):
    plustext = "HuluPlus - "
  else:
    plustext = ""
  title =  plustext + details.xpath('//video/title')[0].text
 
  dir.Append(WebVideoItem(playUrl, title=title, summary=desc, subtitle=subtitle, duration=duration, thumb=thumb, art=art, rating=rating))
  
  if len(dir) == 0:
    return MessageContainer("Error","this section does not contain any video")
  else:
    return dir
    
####################################################################################################      
def tv_shows_listings(sender, showUrl, fromType="feed", entry_type="episode"):
  #episodes for show (go to the show homepage and grab the rss link to parse) 
  showHTML = str(HTTP.Request(showUrl).content)
  showXML = HTML.ElementFromString(showHTML)
  if entry_type == "episode" and showHTML.count('"category": "Episodes"'):
    jsonUrl = HULU_HTML_ITEMS_alt
    entry_type = "Episodes"
  else:
    jsonUrl = HULU_HTML_ITEMS
  rsslink = showXML.xpath("//a[@class='rss-link']")[0].get('href')
  if fromType == "feed":
    dir = populateFromFeed(rsslink, feedType="videos", title=sender.itemTitle)
  else:
    if entry_type == "episode":
      if rsslink.count("episodes") > 0:
        entry_type = "episode"
      elif rsslink.count("videos") > 0 or rsslink.count("clip") > 0:
        entry_type = "clip"
    show_id = rsslink.split("/")[-2]
    dir = populateFromHTML(show_id, entry_type=entry_type, title=sender.itemTitle, jsonUrl=jsonUrl)
  dir.art = "http://assets.hulu.com/shows/key_art_" + showUrl.split("?")[0].split("/")[-1].replace("-","_") + ".jpg"

  if len(dir) == 0:
    return MessageContainer("Error","this section does not contain any video")
  else:
    return dir  
####################################################################################################
# genre dirs
def channels(sender, itemType, display):
  dir = MediaContainer(title2=sender.itemTitle,httpCookies = HTTP.GetCookiesForURL('http://www.hulu.com/profile'))
  h = HTTP.Request(huluListings % ("All", display, itemType, 0), cacheTime=LONG_CACHE_INTERVAL).content
  rep = 'Element.replace("channel", "'
  h = h.split('\n')[2].replace(rep,'').replace('");','').decode('unicode_escape')
  for genre in HTML.ElementFromString(h).xpath('//div[@class="cbx-options"]//li'):
    dir.Append(Function(DirectoryItem(list_shows, title=genre.get("value")), channel=genre.get("value").replace(' ','%20'), itemType=itemType, display=display)) 
  return dir

####################################################################################################
def ParseShowsRSS(sender, feed = None):
  dir = MediaContainer(title2=sender.itemTitle,httpCookies = HTTP.GetCookiesForURL('http://www.hulu.com/profile'))  
  feed = RSS.FeedFromURL(feed)
  @parallelize  
  def iter():
    for entry in feed["items"]:
      @task  
      def showMeta(e=entry):
        url = e.guid.split("#")[0]
        showURL = url.split("/")[-1]
        thumb = "http://assets.hulu.com/shows/key_art_" + showURL.replace("-","_") + ".jpg"
        dir.Append(Function(DirectoryItem(tv_shows_listings, title=e.title, thumb=thumb), showUrl=url))
  return dir

####################################################################################################
def feeds(sender, feedUrl="", sort="normal", feedType="videos", xp=""):
    return populateFromFeed(feedUrl, title=sender.itemTitle, feedType=feedType, sort=sort)

####################################################################################################
def Search(sender, query):
  query = query.replace(" ","+") + "+site:hulu"
  return populateFromFeed("http://www.hulu.com/feed/search?query=" + query + "&sort_by=relevance")

####################################################################################################
def viewQueue(sender):
  dir = MediaContainer(title2=sender.itemTitle,httpCookies = HTTP.GetCookiesForURL('http://www.hulu.com/profile'))  
  for row in HTML.ElementFromURL("http://www.hulu.com/profile/queue?view=list&order=asc&sort=position&kind=list", cacheTime=0).xpath("//table[@class='vt']//tr[@class='r'  or @class='r hide-item first']"):
    if row.xpath("td[@class='c4']")[0].text != "Expired":
      show_num = row.xpath("td/input[@type='checkbox']")[0].get("value")
      info = JSON.ObjectFromURL(HULU_BASE_URL + "videos/info/" + show_num, cacheTime=LONG_CACHE_INTERVAL)

      thumb = info["thumbnail_url"]
      title = info["show_name"] + ": " + info["title"]
      desc = info["description"]
      if info["season_number"] <> 0:
        subtitle = "Season " + str(info["season_number"]) + "   Episode " + str(info["episode_number"])
      else:
        try:    
          subtitle = "Air Date: " + info["air_date"]
        except:
          subtitle = ""
      try:
        duration = str(info["duration"]*1000)
      except:
        duration = ""
      dir.Append(WebVideoItem("http://www.hulu.com/watch/" + show_num + "#in-playlist", title=title, summary=desc, duration=duration, subtitle=subtitle, thumb=thumb))

  if len(dir) == 0:
    return MessageContainer("Error","this section does not contain any video")
  else:
    return dir

####################################################################################################
def populateFromHTML(show_id, entry_type, title="", jsonUrl=HULU_HTML_ITEMS):
  dir = MediaContainer(viewGroup='InfoList', title2=title,httpCookies = HTTP.GetCookiesForURL('http://www.hulu.com/profile'))
  #figure out what type of slider to use
  try:
	  for page in range(0,int(MAX_RESULTS)/5):
		response = HTTP.Request(jsonUrl % (5, str(page+1), show_id, entry_type), errors='ignore', cacheTime=CACHE_INTERVAL).content
		if len(response) > 10:
		  for e in HTML.ElementFromString(response).xpath("//li"):
			id = e.xpath("a")[0].get("href")
			show_num = id.split("/")[-2]
			info = JSON.ObjectFromURL(HULU_BASE_URL + "videos/info/" + show_num, cacheTime=LONG_CACHE_INTERVAL)
			thumb = info["thumbnail_url"]
			title = info["title"]
			desc = info["description"]
			if info["season_number"] <> 0:
			  subtitle = "Season " + str(info["season_number"]) + "   Episode " + str(info["episode_number"])
			else:
			  try:    
				subtitle = "Air Date: " + info["air_date"]
			  except:
				subtitle = ""
			try:
			  duration = str(info["duration"]*1000)
			except:
			  duration = ""
			dir.Append(WebVideoItem(id, title=title, summary=desc, duration=duration, subtitle=subtitle, thumb=thumb))
  except:
    pass
    
  if len(dir) == 0:
    return MessageContainer("Error","This section does not contain any video")
  else:
    return dir

####################################################################################################
def populateFromFeed(url, feedType="videos", sort="normal", title=""):
  title2=title
  if feedType == "videos":
    vg = "InfoList"
  else:
    vg = "List"
  dir = MediaContainer(viewGroup=vg, title2=title,httpCookies = HTTP.GetCookiesForURL('http://www.hulu.com/profile'))
  feed = XML.ElementFromURL(url, errors='ignore', cacheTime=CACHE_INTERVAL).xpath("//item")
  if sort == "reverse":
    feed.reverse()

  @parallelize  
  def iter():
    for e in feed:
      @task  
      def Metadata(e=e):
        playUrl = e.xpath("guid")[0].text.split("#")[0]#.replace(':',"%3A")
        titleFromFeed = e.xpath("title")[0].text.split('-')
        if len(titleFromFeed) > 1:
          seasonEpisode = titleFromFeed[1].replace('e','E').replace('s',"Season ").replace('|',' ').replace('E',"Episode ")
          titleFromFeed = titleFromFeed[0] + '-' + titleFromFeed[2]
        
        if not(('watch' in playUrl)):
		  request = urllib2.Request(playUrl, None, headers)
		  opener = urllib2.build_opener(SmartRedirectHandler)
		  try:
			f = opener.open(request)
			if f.status == 301 or f.status == 302:
			  playUrl = f.url
			  playUrl = HTTP.Request(playUrl).xpath("//meta[@'property=og:url']")[0].get('content')
		  except:
			pass
		  
        api_address = "http://www.hulu.com/api/oembed.json?url="+playUrl
        try:
          jsonObj = JSON.ObjectFromURL(api_address)
        except: 
          jsonObj = JSON.ObjectFromURL(api_address.rsplit('/',1)[0])
		  
        eid = jsonObj['embed_url'].split('embed/')[1].split('/')[0]
		
        details = XML.ElementFromURL(HULU_ASSETS %eid)
	  
        desc = details.xpath('//video/description')[0].text
        airdate = Datetime.ParseDate(details.xpath('//video/original-premiere-date')[0].text).strftime('%a %b %d, %Y')
        if seasonEpisode :
          subtitle =  seasonEpisode.strip() + ' - ' + airdate
        else:
          subtitle = airdate
        duration =  int(float(details.xpath('//video/duration')[0].text)*1000)
        thumb = details.xpath('//video/thumbnail-url')[0].text
        art = ""
        rating =  float(details.xpath('//video/user-star-rating')[0].text)
        plusonly =  details.xpath('//video/is-plus-web-only')[0].text
        if (plusonly == 'true'):
          plustext = "HuluPlus - "
        else:
          plustext = ""
        title =  plustext + titleFromFeed#details.xpath('//video/title')[0].text
        
        if feedType == "videos":
          dirItem = WebVideoItem(playUrl, title=title.strip(), subtitle=subtitle, summary=desc, duration=duration, thumb=thumb,rating = rating)
        else:
          url = playUrl
          id = url.split("/")[-1]
          thumb = "http://assets.hulu.com/shows/key_art_" + id.replace("-","_") + ".jpg"
          art = "http://assets.hulu.com/shows/key_art_" + id.replace("-","_") + ".jpg"
          dirItem = Function(DirectoryItem(tv_shows_listings, title=title, subtitle=subtitle, art=art, thumb=thumb), showUrl=url, fromType="html")
        dir.Append(dirItem)
    
  if len(dir) == 0:
    return MessageContainer("Error","this section does not contain any video")
  else:
    return dir
  
  
# these calls will get seasons and total seasons
# menu: http://m.hulu.com/menu/8159?show_id=33&dp_id=huludesktop&page=1
# total seasons: http://m.hulu.com/menu/8159?show_id=33&dp_id=huludesktop&total=1
