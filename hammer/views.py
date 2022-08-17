
from datetime import datetime
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.http import HttpRequest, HttpResponseRedirect
from django.shortcuts import render, redirect, reverse
from django.views.generic import View, TemplateView
from hammer.models import IPRange, ASN
from hammer.utils import load_data


class SimplePage(TemplateView):
    """Provides baseline for rendering a page.

    Still need to provide template_name and a title in the extra_context."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['year'] = datetime.now().year
        return context


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
    """Executes specified tool (if possible)."""
    if not request.user.is_authenticated:
        raise PermissionDenied
    tool_dict = {
        'asnupdate': load_data.update_asn_db,
        'enwikidown': load_data.download_enwiki,
        'enwikiload': load_data.load_enwiki,
        'globaldown': load_data.download_global,
        'globalload': load_data.load_global
    }
    assert tool in tool_dict.keys()
    try:
        tool_dict[tool]()
    except:
        opts = {
            'title': 'Tools',
            'year': datetime.now().year,
            'error_msg': f"Failed to run tool {tool}"
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
    """Updates the status of the specified IP (by id) to pending."""
    if not request.user.is_authenticated:
        raise PermissionDenied
    address = IPRange.objects.get(id=ip_id)
    address.scheduled = True
    address.save()
    return HttpResponseRedirect(reverse('listf', args=['pending']))

def banasn(request, asn):
    """Updates the status of the ASN to banned, sets each IP with this ASN as pending."""
    if not request.user.is_authenticated:
        raise PermissionDenied
    asn_obj = ASN.objects.get(asn=asn)
    asn_obj.asn_status = ASN.Status.BANNED
    asn_obj.save()
    IPRange.objects.filter(asn=asn_obj, blocked=False)\
        .update(scheduled=True, last_updated=datetime.now())
    return HttpResponseRedirect(reverse('listf', args=['pending']))

def pager(request, filter_by=None):
    """Pages through IP list with optional filter."""
    err_msg = None
    if not request.user.is_authenticated:
        return redirect('home')
    if filter_by == 'new':
        ip_list = IPRange.objects.filter(blocked=False, scheduled=False)
    elif filter_by == 'pending':
        ip_list = IPRange.objects.filter(scheduled=True)
    elif filter_by == 'blocked':
        ip_list = IPRange.objects.filter(blocked=True)
    else:
        ip_list = IPRange.objects.all()
        if filter_by is not None:
            err_msg = "Unrecognized filter, please use the navbar, or report on GitHub "\
                    + "if this issue is persistent"
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

def list_asn(request, asn):
    """Lists all IPs attached to a specified ASN."""
    err_msg = None
    if not request.user.is_authenticated:
        return redirect('home')
    try:
        asn_obj = ASN.objects.get(asn=asn)
        ip_list = IPRange.objects.filter(asn=asn_obj)
    except ASN.DoesNotExist:
        err_msg = f"An ASN with number \"{asn}\" does not exist in the database!"
        ip_list = IPRange.objects.filter(address="empty")  # deliberately fetch an empty set
    paginator = Paginator(ip_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'hammer/pager.html',
        {
            'page_obj': page_obj,
            'title': 'Listing by ASN',
            'year': datetime.now().year,
            'err_msg': err_msg
        }
    )

def asn_detail(asn):
    """Supplies a detailed view of the ASN."""
    pass

def address_detail(address):
    """Supplies a detailed view of the IP address."""
    pass
