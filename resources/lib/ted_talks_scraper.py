from .model import subtitles_scraper
from .model import talk_scraper

class TedTalks:

    def __init__(self, getHTML, logger):
        self.getHTML = getHTML
        self.logger = logger

    def getVideoDetails(self, url, video_quality, subs_language=None):
        talk_html = self.getHTML(url)
        try:
            video_url, title, speaker, plot, talk_json = talk_scraper.get(talk_html, self.logger, video_quality)
        except Exception as e:
            raise type(e)(e.message + "\nfor url '%s'" % (url))

        subs = None
        if subs_language:
            subs = subtitles_scraper.get_subtitles_for_talk(talk_json, subs_language, self.logger)

        return title, video_url, subs, {'Director':speaker, 'Genre':'TED', 'Plot':plot, 'PlotOutline':plot}
