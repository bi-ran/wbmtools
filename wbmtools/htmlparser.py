# -----------------------------------------------------------------------------
# Name:        html_table_parser
# Purpose:     parsing an (x)html string to extract tables.
#              Written in python3
#
# Author:      Josua Schmid with hacks from Sam Harper
#
# Created:     05.03.2014
# Copyright:   (c) Josua Schmid 2014
# Licence:     GPLv3
# -----------------------------------------------------------------------------

from html.parser import HTMLParser

class HTMLTableParser(HTMLParser):
    """ This class serves as a html table parser. It is able to parse multiple
    tables which you feed in. You can access the result per .tables field.
    """

    def __init__(self):
        HTMLParser.__init__(self)
        self._in_cell = False
        self._current_table = []
        self._current_row = []
        self._current_cell = []
        self.tables = []


    def handle_starttag(self, tag, attrs):
        """ We need to remember the opening point for the content of interest.
        """
        if tag in ['th', 'td']:
            self._in_cell = True
        if tag == 'tr' and self._current_row:
            self.tables[-1].append(self._current_row)
            self._current_row = []
        if tag == 'table':
            self.tables.append([])

        if any('bgcolor' in attr for attr in attrs):
            self._current_cell.append(dict(attrs)['bgcolor'])


    def handle_data(self, data):
        """ This is where we save content to a cell """
        if self._in_cell:
            self._current_cell.append(data.strip())


    def handle_endtag(self, tag):
        """ Here we exit the tags. If the closing tag is </tr>, we know that we
        can save our currently parsed cells to the current table as a row and
        prepare for a new row.
        """
        if tag in ['th', 'td']:
            self._in_cell = False
            final_cell = " ".join(self._current_cell).strip()
            self._current_row.append(final_cell)
            self._current_cell = []
        if tag == 'tr':
            self.tables[-1].append(self._current_row)
            self._current_row = []
