import csv
import ipaddress
from ftplib import FTP
from pathlib import Path
from pyasn import mrtx, pyasn
import requests
from hammer.models import ASN, IPRange, validate_ip_range


DOWNLOADS_DIR = Path(__file__).resolve().parent / "downloads"


def update_asn_db():
    """Based on pyasn_util_download and pyasn_util_convert by hadiasghari for pyasn"""
    ftp = FTP("archive.routeviews.org")
    ftp.login()
    months = sorted(ftp.nlst("route-views4/bgpdata"), reverse=True)
    search_path = f"/{months[0]}/RIBS"
    ftp.cwd(search_path)
    file_list = ftp.nlst()
    if not file_list:
        search_path = f"/{months[1]}/RIBS"
        ftp.cwd(search_path)
        file_list = ftp.nlst()
        if not file_list:
            raise LookupError("Cannot find file to download, searched two directories")
    filename = max(file_list)
    localfile = DOWNLOADS_DIR / "bgp.dat"
    with localfile.open("wb") as lfile:
        ftp.retrbinary(f"RETR {filename}", lfile.write)
    ftp.close()
    asn_file = DOWNLOADS_DIR / "asn.dat"
    prefixes = mrtx.parse_mrt_file(str(localfile))
    mrtx.dump_prefixes_to_file(prefixes, str(asn_file), str(localfile))
    localfile.unlink()


def download_csv(url, file_name, force=False):
    req = requests.get(url)
    req.raise_for_status()
    file_path = DOWNLOADS_DIR / file_name
    if file_path.is_file() and not force:
        return  # TODO: throw error?
    with open(file_path, "w") as out:
        out.write(req.text)


def download_global(force=False):
    download_csv(
        "https://quarry.wmcloud.org/query/65222/result/latest/0/csv",
        "global_list.csv",
        force,
    )


def download_enwiki(force=False):
    download_csv(
        "https://quarry.wmcloud.org/query/65223/result/latest/0/csv",
        "enwiki_list.csv",
        force,
    )


def upsert_asn(number, desc):
    try:
        asn = ASN.objects.get(asn=number)
    except ASN.DoesNotExist:
        asn = ASN(asn=number, description=desc)
        asn.save()
    return asn


# TODO: range consolidation on insert
def add_range(address, check_reason, asndb):
    validate_ip_range(address)
    net = ipaddress.ip_network(address, strict=False)
    # TODO: range may exceede allocation
    as_number = str(asndb.lookup(net.network_address.compressed)[0])
    if as_number == "None":
        asn_model = None
    else:
        asn_model = upsert_asn(as_number, None)
    try:
        IPRange.objects.get(
            range_start=net.network_address.packed,
            range_end=net.broadcast_address.packed,
        )
        return  # Exists in database, move on to next
    except:
        range_model = IPRange(
            address=net.compressed,
            range_start=net.network_address.packed,
            range_end=net.broadcast_address.packed,
            asn=asn_model,
            check_reason=check_reason,
        )
        range_model.save()


def load_csv(source):
    if source == "enwiki":
        csvfile = DOWNLOADS_DIR / "enwiki_list.csv"
    elif source == "global":
        csvfile = DOWNLOADS_DIR / "global_list.csv"
    else:
        raise ValueError("Can't load a csv from a source that is not enwiki or global")
    asndb = pyasn(str(DOWNLOADS_DIR / "asn.dat"))
    with csvfile.open() as in_file:
        reader = csv.reader(in_file)
        next(reader)  # Discard headers
        for row in reader:
            if len(row) == 2:
                add_range(row[0], row[1], asndb)


def load_enwiki():
    load_csv("enwiki")


def load_global():
    load_csv("global")


def get_status():
    asnfile = DOWNLOADS_DIR / "asn.dat"
    enwiki_file = DOWNLOADS_DIR / "enwiki_list.csv"
    global_file = DOWNLOADS_DIR / "global_list.csv"
    return {
        "asn_file": asnfile.is_file(),
        "enwiki_file": enwiki_file.is_file(),
        "global_file": global_file.is_file(),
    }
