#                                                                            #
#   OpenERP Module                                                           #
#   Copyright (C) 2013 Author <email@email.fr>                               #
#                                                                            #
#   This program is free software: you can redistribute it and/or modify     #
#   it under the terms of the GNU Affero General Public License as           #
#   published by the Free Software Foundation, either version 3 of the       #
#   License, or (at your option) any later version.                          #
#                                                                            #
#   This program is distributed in the hope that it will be useful,          #
#   but WITHOUT ANY WARRANTY; without even the implied warranty of           #
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the            #
#   GNU Affero General Public License for more details.                      #
#                                                                            #
#   You should have received a copy of the GNU Affero General Public License #
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.    #
#                                                                            #

{
    "name": "Report Pdf Preview",
    "version": "14.0.2.0.0",
    "depends": ["web"],
    "author": "odooqs,Community,Hadooc",
    "website": "http://www.odooqs.com",
    "category": "web",
    "data": [
        "views/assets.xml",
    ],
    "init_xml": [],
    "update_xml": [],
    "demo_xml": [],
    "qweb": [
        "static/src/xml/*.xml",
    ],
    "images": ["static/description/icon.jpg", "static/description/main_screenshot.png"],
    "license": "LGPL-3",
}
