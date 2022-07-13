

import csv
import requests
import subprocess

from ftplib import FTP
from pathlib import Path
from pyasn import mrtx
#from hammer.models import IPRange


DOWNLOADS_DIR = Path(__file__).resolve().parent / "downloads"

def update_asn_db():
    """Based on pyasn_util_download and pyasn_util_convert by hadiasghari for pyasn"""
    ftp = FTP("archive.routeviews.org")
    ftp.login()
    months = sorted(ftp.nlst('route-views4/bgpdata'), reverse=True)
    search_path = '/%s/%s' % (months[0], '/RIBS')
    ftp.cwd(search_path)
    file_list = ftp.nlst()
    if not file_list:
        search_path = '/%s/%s' % (months[1], '/RIBS')
        ftp.cwd(search_path)
        file_list = ft.nlst()
        if not file_list:
            raise LookupError("Cannot find file to download, searched two directories")
    filename = max(file_list)
    localfile = DOWNLOADS_DIR / 'bgp.dat'
    with localfile.open('wb') as lfile:
        ftp.retrbinary('RETR %s' % filename, lfile.write)
    ftp.close()
    asn_file = DOWNLOADS_DIR / 'asn.dat'
    prefixes = mrtx.parse_mrt_file(str(localfile))
    mrtx.dump_prefixes_to_file(prefixes, str(asn_file), str(localfile))
    localfile.unlink()

def download_csv(url, file_name, force=False):
    r = requests.get(url)
    r.raise_for_status()
    file_path = DOWNLOADS_DIR / file_name
    if file_path.is_file() and not force:
        return  # TODO: throw error?
    with open(file_path, 'w') as f:
        f.write(r.text)

def download_global(force=False):
    download_csv("https://quarry.wmcloud.org/query/65222/result/latest/0/csv", "global_list.csv", force)

def download_enwiki(force=False):
    download_csv("https://quarry.wmcloud.org/query/65223/result/latest/0/csv", "enwiki_list.csv", force)

