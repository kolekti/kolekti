from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse
from django.views.generic import View,TemplateView, ListView
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.decorators import method_decorator


from kserver.views import LoginRequiredMixin

# kolekti imports
from kolekti.common import kolektiBase


def in_translator_group(user):
    if user:
        return user.groups.filter(name='translator').count() == 1
    return False


        
class TranslatorsMixin(kolektiBase):
    @method_decorator(user_passes_test(in_translator_group, login_url='/'))
    def dispatch(self, *args, **kwargs):
        return super(TranslatorsMixin,  self).dispatch(*args, **kwargs)



class TranslatorsHomeView(TranslatorsMixin, TemplateView):
    template_name = "translators_home.html"
    def get(self, request):
        context = {}
        return self.render_to_response(context)


