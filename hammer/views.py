
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from hammer.models import IPRange, ASN
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
    if not request.user.is_authenticated:
        raise PermissionDenied
    tools = {
        'asnupdate': load_data.update_asn_db,
        'enwikidown': load_data.download_enwiki,
        'enwikiload': load_data.load_enwiki,
        'globaldown': load_data.download_global,
        'globalload': load_data.load_global
    }
    assert tool in tools.keys()
    try:
        tools[tool]()
    except:
        opts = {
            'title':'Tools',
            'year':datetime.now().year,
            'error_msg':'Failed to run tool %s' % tool
        }
        opts.update(load_data.get_status())
        return render(
            request,
            'hammer/tools.html',
            opts
        )
    else:
        return HttpResponseRedirect(reverse('tools'))

def banip(request, ip_id):
    if not request.user.is_authenticated:
        raise PermissionDenied
    range = IPRange.objects.get(id=ip_id)
    range.scheduled = True
    range.save()
    return HttpResponseRedirect(reverse('listf', args=['pending']))

def banasn(request, asn):
    if not request.user.is_authenticated:
        raise PermissionDenied
    asn_obj = ASN.objects.get(asn=asn)
    asn_obj.asn_status = ASN.Status.BANNED
    asn_obj.save()
    IPRange.objects.filter(asn=asn_obj, blocked=False).update(scheduled=True, last_updated=datetime.now())
    return HttpResponseRedirect(reverse('listf', args=['pending']))

def list(request, filter=None):
    err_msg = None
    if not request.user.is_authenticated:
        return redirect('home')
    if filter == 'new':
        ip_list = IPRange.objects.filter(blocked=False, scheduled=False)
    elif filter == 'pending':
        ip_list = IPRange.objects.filter(scheduled=True)
    elif filter == 'blocked':
        ip_list = IPRange.objects.filter(blocked=True)
    else:
        ip_list = IPRange.objects.all()
        if filter != None:
            err_msg = "Unrecognized filter, please use the navbar, or report on GitHub if this issue is persistent"
    paginator = Paginator(ip_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'hammer/pager.html',
        {
            'page_obj': page_obj,
            'title': 'List',
            'year': datetime.now().year,
            'err_msg': err_msg
        }
    )