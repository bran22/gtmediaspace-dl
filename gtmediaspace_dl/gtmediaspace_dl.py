import argparse
import logging
from bs4 import BeautifulSoup
import requests
import re
import youtube_dl
import sys


# parse arguments passed from command line
def parseArguments():
    # set up argument parser
    parser = argparse.ArgumentParser(description='Downloads video playlists hosted on mediaspace.gatech.edu using the youtube-dl Kaltura plugin')
    parser.add_argument('--embed-subs', action='store_true', help='Embed subtitles in the video (only for mp4, webm and mkv videos).  Requires ffmpeg.')
    parser.add_argument('playlistUrl', type=str, help='Playlist link.  Should be in the format https://mediaspace.gatech.edu/playlist/details/*')
    # get values from arguments
    args = parser.parse_args()
    url = args.playlistUrl
    embedSubs = args.embed_subs

    validUrlRegex = re.compile(r'^https://mediaspace.gatech.edu/playlist/details/\w{10}$')
    if (re.match(validUrlRegex, url) is not None):
        return url, embedSubs
    else:
        return '', embedSubs

# get page content
def getPageContent(url: str):
    page = requests.get(url)
    return BeautifulSoup(page.content, 'html.parser')

# get page title
def scrapePageTitle(soup: BeautifulSoup):
    pageTitle = soup.find('title').text
    # 
    if str.startswith(pageTitle, 'Playlist Details - '):
        pageTitle = pageTitle.strip('Playlist Details - ')
    return pageTitle

# find partner_id
def scrapePartnerId(soup: BeautifulSoup):
    partnerScript = soup.find('script', {'src': re.compile('https://cdnapisec.kaltura.com/p/*') })
    partnerIdPattern = re.compile(r'kaltura.com\/p\/([0-9]*)')
    partnerIdMatch = partnerIdPattern.search(partnerScript.get('src'))
    return partnerIdMatch.group(1)

# find list of playlist ids via the playlist script
def scrapePlaylistIdArray(soup: BeautifulSoup):
    playlistDiv = soup.find('div', id='playlist-details')
    playlistScript = playlistDiv.find_next_sibling('script')
    # looking for JSON like this: playlist: {"playlistContent":"*playlistID*,*playlistID* ...
    playlistIdPattern = re.compile(r'"playlistContent":"((\\"|[^"])*)"')
    playlistIdMatches = playlistIdPattern.search(playlistScript.string)
    return playlistIdMatches.group(1).split(',')  # convert comma-separated videoIds to array

# make array of YDL download links
def generateYdlLinks(partnerId: str, videoIds: list):
    downloadLinks = []
    for videoId in videoIds:
        downloadLinks.append(f'kaltura:{partnerId}:{videoId}')
    return downloadLinks

# download using youtube-dl
def ydlDownload(options, downloadLinks: list):
    with youtube_dl.YoutubeDL(options) as ydl:
        ydl.download(downloadLinks)

# main function
def main():

    # set up logging
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)

    # get url from command line
    url, embedSubs = parseArguments()
    if not url:
        logging.error('Invalid URL')
        quit()

    # scrape site contents
    logging.info(f'Fetching webpage: {url}')
    soup = getPageContent(url)
    pageTitle = scrapePageTitle(soup)
    logging.debug(f'Parsing webpage "{pageTitle}" for IDs')
    partnerId = scrapePartnerId(soup)
    playlistIds = scrapePlaylistIdArray(soup)
    logging.debug(f'playlist ID array: {playlistIds}')

    # generate download links
    logging.debug(f'Generating youtube-dl download links')
    downloadLinks = generateYdlLinks(partnerId, playlistIds)
    logging.info(f'Found {len(downloadLinks)} videos to download')

    # set youtube-dl settings
    ydlOptions = {
        'outtmpl': pageTitle + '/%(title)s.%(ext)s',
        'sleep_interval': 5,
    }

    if embedSubs:
        ydlOptions['writesubtitles'] = True
        ydlOptions['postprocessors'] = {
            'key': 'FFmpegEmbedSubtitle'
        },

    # download
    logging.info(f'Handing off to youtube-dl to perform download')
    ydlDownload(ydlOptions, downloadLinks)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logging.warning("CTRL-C detected, exiting...")
        sys.exit(0)