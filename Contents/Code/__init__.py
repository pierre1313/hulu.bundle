import re, random
from urlparse import urlparse
from PMS import *
from PMS.Objects import *
from PMS.Shortcuts import *

HULU_PLUGIN_PREFIX   = "/video/hulu" 
HULU_BASE_URL        = "http://www.hulu.com/"
HULU_SEARCH_URL      = HULU_BASE_URL + "search/"

CACHE_INTERVAL       = 3600 # HTTP cache interval in seconds
LONG_CACHE_INTERVAL  = 750000 # this is the cache time for show/movie details that don't really change
MAX_RESULTS          = "150"  # max results for lists

HULU_HTML_ITEMS     = "http://www.hulu.com/videos/slider?items_per_page=%s&page=%s&season&show_id=%s&sort=original_premiere_date&type=%s" # max_results % page %show_id % episode/clip
HULU_HTML_ITEMS_alt = "http://www.hulu.com/videos/slider?items_per_page=%s&page=%s&season&show_id=%s&sort=original_premiere_date&category=%s" # max_results % page %show_id % episode/clip

huluListings = 'http://www.hulu.com/browse/search?keyword=&alphabet=All&family_friendly=0&closed_captioned=0&channel=All&subchannel=&network=All&display=%s&decade=All&type=tv&view_as_thumbnail=true&block_num=%s'

YAHOO_NAMESPACE  = {'media':'http://search.yahoo.com/mrss/'} 
# Default artwork and icon(s)
PLUGIN_ARTWORK      = 'art-default.jpg'
PLUGIN_ICON_DEFAULT = 'icon-default.jpg'
  
TYI = '//img[@src="/images/icon-has-%s.gif"]/..'
TYICLIPS = '//table//li'
    
profilename = ''

####################################################################################################
def Start():
  Plugin.AddPrefixHandler(HULU_PLUGIN_PREFIX, MainMenu, "Hulu", PLUGIN_ICON_DEFAULT, PLUGIN_ARTWORK)
  Plugin.AddViewGroup("InfoList", viewMode="InfoList", mediaType="items")
  Plugin.AddViewGroup('List', viewMode='List', mediaType='items')
  MediaContainer.title1    = 'Hulu'
  MediaContainer.viewGroup = 'List'
  MediaContainer.art       = R(PLUGIN_ARTWORK)
  HTTP.SetCacheTime(CACHE_INTERVAL)
  loginResult = HuluLogin()
  Log("Login success: " + str(loginResult))
  if loginResult:
    Log("Profile name: " + HuluProfileName())

####################################################################################################  
def HuluLogin():
  username = Prefs.Get("email")
  password = Prefs.Get("password")
  resp = HTTP.Request("https://secure.hulu.com/account/authenticate?" + str(int(random.random()*1000000000)), headers={"Cookie":"sli=1; login=" + username + "; password=" + password + ";"})
  if resp == "Login.onComplete();":
    return True
  else:
    return False
    
####################################################################################################
def HuluProfileName():
  return XML.ElementFromURL("http://www.hulu.com/profile", isHTML=True, cacheTime=0).xpath('//a[contains(@href,"/profiles/")]')[0].get('href').split('/')[-1].split('?')[0]
  
####################################################################################################
def CreatePrefs():
  Prefs.Add(id='email', type='text', default='', label='Email address')
  #Prefs.Add(id='profilename', type='text', default='', label='Profile URL [in Hulu.com Profile]')
  Prefs.Add(id='password', type='text', default='', label='Password', option='hidden')
  #Prefs.Add(id='cacheLevel', type='enum', default='Low', label='Pre-caching Level', values='Low|High')
  
####################################################################################################
def UpdateCache():
  #cacheLevel = Prefs.Get("cacheLevel")
  #if cacheLevel = "Low":
  #  cacheLevel = 2
  #else:
  #  cacheLevel = 5
  #walkDir(MainMenu(), cacheLevel, 0) 
  walkDir(menutv(sender=""), 1, 1, recurse=True)
  walkDir(menumovies(sender=""), 1, 1, recurse=True)
  walkDir(menupopular(sender=""), 1, 1, recurse=True)
  walkDir(menurecent(sender=""), 1, 1, recurse=True)

def walkDir(dir, cacheLevel, currentLevel, recurse=False):
  #Log("cacheLevel:" + str(cacheLevel) + " currentLevel: " + str(currentLevel))
  for item in dir:
    try:
      if currentLevel <= cacheLevel and ObjectManager.ObjectHasBase(item, Function):   
        if recurse:
          pass
          #walkDir(item._Function__obj.key(ItemInfoRecord(), **item._Function__kwargs), cacheLevel, currentLevel+1, recurse=True)
        else:
          pass
          #x = item._Function__obj.key(ItemInfoRecord(), **item._Function__kwargs)
    except:
      pass
        
####################################################################################################
def MainMenu():
  dir = MediaContainer()
  dir.noCache=1
  dir.Append(Function(DirectoryItem(myhulu, title="My Hulu")))
  dir.Append(Function(DirectoryItem(menutv, title="TV")))
  #dir.Append(Function(DirectoryItem(menumovies, title="Movies")))
  dir.Append(Function(DirectoryItem(tv_channels, L("Movies")), entry_type="feature_film", xp=TYI % "movie"))
  dir.Append(Function(DirectoryItem(menupopular, title="Popular Videos")))
  dir.Append(Function(DirectoryItem(menurecent, title="Recently Added")))
  dir.Append(Function(DirectoryItem(feeds, title=L("Highest Rated Videos")), feedUrl="http://www.hulu.com/feed/highest_rated/videos"))
  dir.Append(Function(DirectoryItem(feeds, title=L("Soon-to-Expire Videos")), feedUrl="http://www.hulu.com/feed/expiring/videos"))
  #dir.AppendItem(DirectoryItem("hd||" + _L("HD Gallery"), _L("HD Gallery"), ""))
  dir.Append(Function(InputDirectoryItem(Search, title=L("Search Hulu"), prompt=L("Search Hulu"), thumb=R('search.png'))))
  dir.Append(PrefsItem(L("Preferences...")))
  return dir

def menutv(sender):
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(tv_shows, L("TV Shows")), url="http://www.hulu.com/browse/alphabetical/tv", entry_type="episode", xp=TYI % "episode"))
  dir.Append(Function(DirectoryItem(tv_channels, L("TV Channels")), entry_type="episode", xp=TYI % "episode"))    
  #dir.Append(Function(DirectoryItem(tv_channels, L("TV Clips")), entry_type="clips", xp=TYICLIPS))
  return dir
  
def menumovies(sender):
  dir = MediaContainer()
  dir.Append(Function(DirectoryItem(tv_channels, L("Movie Channels")), entry_type="feature_film", xp=TYI % "movie"))
  #dir.Append(Function(DirectoryItem(tv_channels, L("Movie Clips")), entry_type="film_clips", xp=TYICLIPS))
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
  dir.Append(Function(DirectoryItem(recent_shows, L("Recently Added Shows")))) 
  dir.Append(Function(DirectoryItem(feeds, L("Recently Added Movies")), feedUrl="http://rss.hulu.com/HuluRecentlyAddedMovies?format=xml")) 
  dir.Append(Function(DirectoryItem(feeds, L("Recently Added Videos")), feedUrl="http://rss.hulu.com/HuluRecentlyAddedVideos?format=xml"))
  return dir
  
def myhulu(sender):
  loginResult = HuluLogin()  
  Log("myhulu Login success: " + str(loginResult))
  if loginResult:
    username = HuluProfileName()
    dir = MediaContainer()
    dir.Append(Function(DirectoryItem(viewQueue, L("My Hulu Queue"))))
    #dir.Append(Function(DirectoryItem(feeds, L("My Hulu Queue")), feedUrl="http://www.hulu.com/feed/queue/" + username, sort="reverse"))
    #these links are dead on their site right now. nice work.
    dir.Append(Function(DirectoryItem(feeds, L("My Hulu Show Recommendations")), feedUrl="http://www.hulu.com/feed/show_recommendations/" + username, feedType="shows"))
    dir.Append(Function(DirectoryItem(feeds, L("My Hulu Video Recommendations")), feedUrl="http://www.hulu.com/feed/recommendations/" + username))
    dir.Append(Function(DirectoryItem(feeds, L("My Hulu Subscriptions")), feedUrl="http://www.hulu.com/feed/subscriptions/" + username, feedType="shows"))
  else:
    dir = MessageContainer("User info required", "Please enter your Hulu email address and password in Preferences.")
  return dir
  
####################################################################################################
def tv_shows(sender, url, entry_type, xp):
  dir = MediaContainer(title2=sender.itemTitle)
  i = 0
  while 1:
    h = HTTP.Request(huluListings % ("Shows%20with%20full%20episodes%20only", i), autoUpdate=True)
    if len(h) < 215:
      break
    rep = 'Element.update("show_list", "'
    if h.find(rep) == -1:
      rep = 'Element.replace("browse-lazy-load", '
    h = h.split('\n')[1].replace(rep,'').replace('");','').decode('unicode_escape')
    for s in XML.ElementFromString(h, isHTML=True).xpath('//a[@class="info_hover"]'):
      showUrl = s.get('href')
      title = s.xpath('img')[0].get('alt')
      thumb = "http://assets.hulu.com/shows/key_art_" + showUrl.split("?")[0].split("/")[-1].replace("-","_") + ".jpg"
      dir.Append(Function(DirectoryItem(tv_shows_listings, title=title, thumb=thumb), showUrl=showUrl, fromType="html", entry_type=entry_type))
    i+=1
    
  return dir

####################################################################################################      
def tv_shows_listings(sender, showUrl, fromType="feed", entry_type="episode"):
  #episodes for show (go to the show homepage and grab the rss link to parse) 
  showHTML = str(HTTP.Request(showUrl))
  if entry_type == "episode" and showHTML.count('"category": "Episodes"'):
    jsonUrl = HULU_HTML_ITEMS_alt
    entry_type = "Episodes"
  else:
    jsonUrl = HULU_HTML_ITEMS
  rsslink = XML.ElementFromURL(showUrl, isHTML=True, autoUpdate=True).xpath("//a[@class='rss-link']")[0].get('href')
  if fromType == "feed":
    dir = populateFromFeed(rsslink, feedType="videos", title=sender.itemTitle)
  else:
    if entry_type == "episode":
      if rsslink.count("episodes") > 0:
        Log('episodes > 0') 
        entry_type = "episode"
      elif rsslink.count("videos") > 0 or rsslink.count("clip") > 0:
        entry_type = "clip"
    show_id = rsslink.split("/")[-2]
    dir = populateFromHTML(show_id, entry_type=entry_type, title=sender.itemTitle, jsonUrl=jsonUrl)
  dir.art = "http://assets.hulu.com/shows/key_art_" + showUrl.split("?")[0].split("/")[-1].replace("-","_") + ".jpg"
  return dir 
  
####################################################################################################
# genre dirs
def tv_channels(sender, entry_type, xp):
  dir = MediaContainer(title2=sender.itemTitle)
  if entry_type.count("film") == 0:
    url = "http://www.hulu.com/browse/alphabetical/" + entry_type + "s"
  else:
    url = "http://www.hulu.com/browse/alphabetical/" + entry_type
  for genre in XML.ElementFromURL(url, cacheTime=LONG_CACHE_INTERVAL, isHTML=True, autoUpdate=True).xpath("//ul[@id='ch_list_expanded']//div[@class='filter-item']/a"):
    if entry_type == "feature_film":
      dir.Append(Function(DirectoryItem(feature_film, title=genre.text_content()), url=genre.get("href"), entry_type=entry_type, xp=xp)) 
    elif entry_type == "film_clips":
      dir.Append(Function(DirectoryItem(tv_shows, title=genre.text_content()), url=genre.get("href"), entry_type="clip", xp=xp))    
    else:
      dir.Append(Function(DirectoryItem(tv_shows, title=genre.text_content()), url=genre.get("href"), entry_type=entry_type, xp=xp)) 
  return dir

####################################################################################################
# first, the high level genre dirs
def feature_film(sender, url, entry_type, xp):
  # Films in genre.
  dir = MediaContainer(title2=sender.itemTitle, viewGroup="InfoList")
  @parallelize
  def iter():
    for sh in XML.ElementFromURL(url, isHTML=True, autoUpdate=True).xpath(xp):
      @task
      def showMeta(show=sh):
        try:  
            show = show.xpath('..//a')[0]
            #title = showLi.xpath('a[contains(@class,"show-thumb")]')[0].text_content().strip() 
            url = show.get('href')
            Log(url)
            show_name = url.split("/")[-1]
            art = "http://assets.hulu.com/shows/key_art_" + show_name.split("?")[0].replace("-","_") + ".jpg"
            site = XML.ElementFromURL(url, cacheTime=LONG_CACHE_INTERVAL, isHTML=True)
            link = site.xpath("//span[@class='play-button-hover']/a")
            playurl = link[0].get('href')
            title = link[0].find('img').get('alt')
            desc = site.xpath("//div[@class='info'][4]")[0].text
            thumb = link[0].find('img').get('src')
            try:
              subtitle = "Released: " + site.xpath('//div[@class="relative"]/div[12]')[0].text
            except:
              subtitle = ""
            try:  
              duration = site.xpath('//div[@class="description"]')[0].text_content().split('|')[1].strip()
              duration_parts = duration.split(":")
              if len(duration_parts) == 2:
                hours = 0
                mins = int(duration_parts[0])
                secs = int(duration_parts[1])
              else:
                hours = int(duration_parts[0])
                mins = int(duration_parts[1])
                secs = int(duration_parts[2])
              duration = str(((hours*3600) + (mins * 60) + secs) * 1000)
            except:
              duration = ""
            dir.Append(WebVideoItem(playurl, title=title, summary=desc, subtitle=subtitle, duration=duration, thumb=thumb, art=art))
        except:
            pass
  dir.Sort("title")
  return dir

####################################################################################################
def recent_shows(sender):
  dir = MediaContainer(title2=sender.itemTitle)  
  feed = RSS.FeedFromURL("http://rss.hulu.com/HuluRecentlyAddedShows?format=xml")
  @parallelize  
  def iter():
    for entry in feed["items"]:
      @task  
      def showMeta(e=entry):
        url = e.feedburner_origlink.split("#")[0]
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
  dir = MediaContainer(title2=sender.itemTitle)  
  for row in XML.ElementFromURL("http://www.hulu.com/profile/queue?view=list&order=asc&sort=position", cacheTime=0, isHTML=True).xpath("//table[@class='vt']//tr[@class='r' or @class='r first']"):
    #Log(XML.StringFromElement(row))
    #Log(Log(XML.StringFromElement(row.xpath("//input[@type='checkbox']")[0])))
    if row.xpath("td[@class='c4']")[0].text != "Expired":
      show_num = row.xpath("td/input[@type='checkbox']")[0].get("value")
      info = JSON.ObjectFromURL(HULU_BASE_URL + "videos/info/" + show_num, cacheTime=LONG_CACHE_INTERVAL)
      #Log(info)
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
  return dir

####################################################################################################
def populateFromHTML(show_id, entry_type, title="", jsonUrl=HULU_HTML_ITEMS):
  dir = MediaContainer(viewGroup='InfoList', title2=title)
  #figure out what type of slider to use
  
  for page in range(0,int(MAX_RESULTS)/5):
    response = HTTP.Request(jsonUrl % (5, str(page+1), show_id, entry_type), errors='ignore', cacheTime=CACHE_INTERVAL, autoUpdate=True)
    if len(response) > 10:
      for e in XML.ElementFromString(response, isHTML=True).xpath("//li"):
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
  return dir

####################################################################################################
def populateFromFeed(url, feedType="videos", sort="normal", title=""):
  title2=title
  if feedType == "videos":
    vg = "InfoList"
  else:
    vg = "List"
  dir = MediaContainer(viewGroup=vg, title2=title)
  feed = XML.ElementFromURL(url, errors='ignore', cacheTime=CACHE_INTERVAL, isHTML=False, autoUpdate=True).xpath("//item")
  if sort == "reverse":
    feed.reverse()
  
  for e in feed:
    try:
      description = XML.ElementFromString(e.xpath("description")[0].text, True).xpath("//p")[0].text_content()
    except:
      description = ""
    try:    
      duration = XML.ElementFromString(e.xpath("description")[0].text, True).xpath("//p")[1].text_content()
      durfind = duration.find("Duration:")
      vid_duration = duration[durfind+9:duration.find("Rating",durfind)]
      duration = ""
      duration_parts = vid_duration.partition(":")
      if duration_parts[0] == "" or duration_parts[0] == " ": mins = 0
      else: mins = int(duration_parts[0])
      duration = str(((mins * 60) + int(duration_parts[2])) * 1000)
    except:
      duration = ""
      
    #might be useful for fanart setting...
    playurl = e.xpath("guid")[0].text
     
    # Tweak the title to remove common prefix.
    title = e.xpath("title")[0].text
    subtitle = e.xpath("pubDate")[0].text
    thumb = e.xpath("media:thumbnail", namespaces=YAHOO_NAMESPACE)[0].get("url")
    
    # Check for TV show.
    match = re.search('([a-zA-Z0-9\- ]+): (.*) \(s([0-9]+) \| e([0-9]+)\)', title)
    if match and url.find('feed/show') != -1:
      title = match.group(2)
    st = title.find("(s")  
    if st > 0:
      subtitle = "Season " + title[st+2:title.find("|")] + "  Episode " + title[title.find("|")+3:-1]
      title = title[:st]
      
    #Take off prefix.
    if title2 and title.find(title2) == 0:
      title = title[len(title2)+1:]
      if title.startswith("- "):
          title = title[2:]
    
    if feedType == "videos":
      dirItem = WebVideoItem(playurl, title=title.strip(), subtitle=subtitle, summary=description, duration=duration, thumb=thumb)
    else:
      url = playurl.split("#")[0]
      id = url.split("/")[-1]
      thumb = "http://assets.hulu.com/shows/key_art_" + id.replace("-","_") + ".jpg"
      art = "http://assets.hulu.com/shows/key_art_" + id.replace("-","_") + ".jpg"
      dirItem = Function(DirectoryItem(tv_shows_listings, title=title, subtitle=subtitle, art=art, thumb=thumb), showUrl=url, fromType="html")
    if match:
      dirItem.SetTelevisonMetadata(match.group(1), match.group(3), match.group(4))
    dir.Append(dirItem)
  return dir
  
# these calls will get seasons and total seasons
# menu: http://m.hulu.com/menu/8159?show_id=33&dp_id=huludesktop&page=1
# total seasons: http://m.hulu.com/menu/8159?show_id=33&dp_id=huludesktop&total=1
