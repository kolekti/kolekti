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

import time

from kolekti.mvc.controllers.IterController import IterController
from kolektiserver.publication.publication import TramePublisher

from kolekti.logger import dbgexc,debug
from kolekti.utils.i18n.i18n import tr

class PublishController(IterController):
    def __init__(self, httpRequest):
        IterController.__init__(self, httpRequest)
        self.nstrame = 'kolekti:trames'

    def genPOST(self):
        """ for publication : called from launcher
        http params :
            - pubdir        : publication directory
            - trame         : trame selected
            - profiles      : list of enabled profiles
            - scripts       : list of enabled scripts
            - do_master     : do we need to generate the master file ? [1|0]
            - filter_master : do we need to filter master file
            - master_name   : name of master file"""

        debug("post %s"%self.http.params)
        # tell the user we start
        yield self.view.start()
        debug("getting params")

        pubdata = self.model.getdata(self.http.params.get('KolektiData', None))
        if pubdata is None:
            return

        pubparams = {'pubdir': unicode(pubdata.xpath("string(/order/pubdir/@value)")),
                     'pubtitle': unicode(pubdata.xpath("string(/order/pubtitle[not(@value = '')]/@value|/order[not(pubtitle) or pubtitle/@value = '']/@id)")),
                     'trame': unicode(pubdata.xpath("string(/order/trame/@value)")),
                     'profiles': pubdata.xpath("/order/profiles/profile[@enabled='1']"),
                     'scripts': pubdata.xpath("/order/scripts/script[@enabled='1']"),
                     'do_master':self.http.params.get('genmaster','0'),
                     'filter_master':self.http.params.get('filtermaster','0'),
                     'master_name':self.http.params.get('mastername','')}

        # get the trame to be published
        try:
            trame=self.model.trame(pubparams['trame'])
        except:
            s = tr(u"[0026]Impossible de lire la trame")
            yield self.view.error(s.i18n(self.http.translation))
            yield self.view.finalize()
            return

        try:
            # instanciate a publisher object
            publisher = TramePublisher(self.view, self.model)

            # sets the trame and aggregate modules into a single xhtml structure
            trameerror = False
            for msg in publisher.settrame(trame, pubparams):
                trameerror = True
                yield msg

            if not trameerror:
                # if we shall actually publish, run the publication with all selected profiles
                for msg in publisher.publish():
                    yield msg

                # if we shall generate a master, for for generate the master
                if not pubparams['do_master'] == '0':
                    for msg in publisher.genmaster(pubparams['trame']):
                        yield msg

                # register publication parameters in a manifest document
                self.model.add_orders_history()
        except:
            dbgexc()
            # tell the user it is done
        yield self.view.finalize()
