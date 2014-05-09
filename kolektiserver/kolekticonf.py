#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import mimetypes

from kolekti import kolekticonf

mimetypes.add_type("application/epub+zip", ".epub")
mimetypes.init()

kolekticonf.__conf__.update({
    'pubscripts':(u'_CONFDIR_/pubscripts.xml','/config/kolektiserver/publication/@scripts','path'),
    'modExt':(u'xht','/config/kolektiserver/modules/@file_extension','string'),
    'oooserver_host': (u'', '/config/kolektiserver/oooserver/@host', 'string'),
    'oooserver_port': (u'', '/config/kolektiserver/oooserver/@port', 'string'),

    'dirOP':(u'collections','/config/kolektiserver/directories/collections/@path','string'),
    'dirSA':(u'trames','/config/kolektiserver/directories/trames/@path','string'),
    'dirPUB':(u'publications','/config/kolektiserver/directories/publications/@path','string'),
    'dirSHEETS':(u'sheets','/config/kolektiserver/directories/sheets/@path','string'),
    'dirMOD':(u'modules','/config/kolektiserver/directories/modules/@path','string'),
    'dirMASTERS':(u'masters','/config/kolektiserver/directories/masters/@path','string'),
    'dirMEDIAS':(u'medias','/config/kolektiserver/directories/medias/@path','string'),
    'dirCSS':(u'design','/config/kolektiserver/directories/styles/@path','string'),
    'dirPRJ':(u'projects','/config/kolektiserver/directories/projects/@path','string'),

    })
__conf__=kolekticonf.__conf__

conf=kolekticonf.KConf(__conf__)
