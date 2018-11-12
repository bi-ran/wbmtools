# -----------------------------------------------------------------------------
# Name:        wbm parser
# Purpose:     simple class to parse WBM webpages
#
#
# Author:      Sam Harper
#
# Created:     12.09.2016
# Copyright:   (c) Sam Harper 2016
# Licence:     GPLv3
# -----------------------------------------------------------------------------

from wbmtools.cernssoparser import SSOSession
from wbmtools.htmlparser import HTMLTableParser

# throttle the speed if a Cern Authentication page is detected

class WBMParser(SSOSession):
    """wbm parser

    parse wbm pages, which consist of tables
    """

    def parse_url(self, url):
        parser = HTMLTableParser()
        parser.feed(self.read_url(url))
        try:
            for _ in range(10):
                from time import sleep
                sleep(3)
                parser.feed(self.read_url(url))
                if parser.titles[0] != "Cern Authentication" or len(tables) > 1:
                    break
        except:
            pass
        return parser


    def parse_url_tables(self, url):
        parser = HTMLTableParser()
        parser.feed(self.read_url(url))
        try:
            for _ in range(10):
                from time import sleep
                sleep(3)
                parser.feed(self.read_url(url))
                if parser.titles[0] != "Cern Authentication" or len(tables) > 1:
                    break
        except:
            pass
        return parser.tables


    def parse_url_tables_format(self, url):
        parser = HTMLTableParser()
        parser.feed(self.read_url(url))
        try:
            for _ in range(10):
                from time import sleep
                sleep(3)
                parser.feed(self.read_url(url))
                if parser.titles[0] != "Cern Authentication" or len(tables) > 1:
                    break
        except:
            pass
        return parser.tables, parser.tablesFormat
