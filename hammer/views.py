
from datetime import datetime
from django.http import HttpRequest
from django.shortcuts import render
from django.views.generic import ListView
from hammer.models import IPRange


def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'hammer/index.html',
        {
            'title':'Home',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'hammer/about.html',
        {
            'title':'About',
            'year':datetime.now().year,
        }
    )


class IPPager(ListView):
    paginate_by = 50
    model = IPRange


