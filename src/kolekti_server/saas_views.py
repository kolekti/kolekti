# -*- coding: utf-8 -*-

#     kOLEKTi : a structural documentation generator
#     Copyright (C) 2007-2013 Stéphane Bonhomme (stephane@exselt.com)
class SaasProjectsView(kolektiMixin, View):
    template_name = "saas/projects.html"
    def get(self, request, require_svn_auth=False, project_folder="", project_url=""):
        
        context = self.get_context_data({
                    "active_project" :self.user_settings.active_project.encode('utf-8'),
                    "active_srclang":self.kolekti_userproject.srclang,
                    "require_svn_auth":require_svn_auth,
                    "projectfolder":self.kolekti_userproject.project.directory,
                    "projecturl":self.kolekti_userproject.project.svn,
                    })
            
        return self.render_to_response(context)

    def post(self, request):
        project_folder = request.POST.get('projectfolder')
        project_url = request.POST.get('projecturl')
        username = request.POST.get('username',None)
        password = request.POST.get('password',None)
        from kolekti.synchro import SVNProjectManager
        sync = SVNProjectManager(settings.KOLEKTI_BASE,username,password)
        if project_url=="":
        # create local project
            #sync.export_project(project_folder)
            self.create_project(project_folder, os.path.join(settings.KOLEKTI_BASE,self.user.username)
            self.project_activate(project_folder)
            return self.get(request)
        else:
            try:
                sync.checkout_project(project_folder, project_url)
                return self.get(request)
            except ExcSyncNoSync:
                return self.get(request, require_svn_auth=True, project_folder=project_folder, project_url=project_url)





    
