
from datetime import datetime
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.views.generic import ListView
from hammer.models import IPRange
from hammer.utils import load_data


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'hammer/index.html',
        {
            'title': 'Home',
            'year': datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'hammer/about.html',
        {
            'title': 'About',
            'year': datetime.now().year,
        }
    )

def tools(request):
    """Renders a tools page for authenticated users only."""
    assert isinstance(request, HttpRequest)
    if not request.user.is_authenticated:
        return redirect('home')
    opts = {
        'title': 'Tools',
        'year': datetime.now().year,
    }
    opts.update(load_data.get_status())
    return render(
        request,
        'hammer/tools.html',
        opts
    )

def execute(request, tool):
    assert request.user.is_authenticated
    tools = {
        'asnupdate': load_data.update_asn_db,
        'enwikidown': load_data.download_enwiki,
        'enwikiload': load_data.load_enwiki,
        'globaldown': load_data.download_global,
        'globalload': load_data.load_global
    }
    assert tool in tools.keys()
    #try:
    tools[tool]()
    #except:
    #    opts = {
    #        'title':'Tools',
    #        'year':datetime.now().year,
    #        'error_msg':'Failed to run tool %s' % tool
    #    }
    #    opts.update(load_data.get_status())
    #    return render(
    #        request,
    #        'hammer/tools.html',
    #        opts
    #    )
    #else:
    return HttpResponseRedirect(reverse('tools'))

class IPPager(ListView):
    paginate_by = 50
    model = IPRange


