# -*- coding: utf-8 -*-
#
#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2011 Stéphane Bonhomme (stephane@exselt.com)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""
"""

__author__  = '''Guillaume Faucheur <guillaume@exselt.com>'''


from kolektiserver.views.PublishView import PublishView
from kolektiserver.views.WWWProjectView import WWWProjectView

class WWWTranslateView (PublishView, WWWProjectView):
    def startdoc(self):
        doc = '''<html xmlns="http://www.w3.org/1999/xhtml">
          <head>
            <title>upload form</title>
            <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
            <link href="/_lib/kolekti/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
            <link href="/_lib/app/css/forms/kolekti-uploadmasterform.css" media="all" rel="stylesheet" type="text/css" />
            <link href="/_lib/app/css/forms/kolekti-uploadtranslateform.css" media="all" rel="stylesheet" type="text/css" />
            <link href="/_lib/app/css/kolekti.css" media="all" rel="stylesheet" type="text/css" />
            <link href="/_lib/kolekti/scripts/jquery/css/ui-lightness/jquery-ui-1.8.14.custom.css" media="all" rel="stylesheet" type="text/css"/>
          </head>
          <body style="min-width:0;">
              <div class="publication_result">'''
        return doc

    def finalizedoc(self):
        doc = '''</div>
              </body>
            </html>'''
        return doc


