# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2014 Stéphane Bonhomme (stephane@exselt.com)

class ExcSync(Exception):
    pass

class ExcSyncNoSync(ExcSync):
    pass

class ExcSyncLocal(ExcSync):
    pass

class ExcSyncRequestAuth(ExcSync):
    pass

class ExcSyncRequestSSL(ExcSync):
    pass
