import gzip
import xml.etree.ElementTree as ET
from datetime import datetime
from app.database.session import get_session
from app.database.models import Report
from app.dmarc.importer import insert_dmarc_report
from config.settings import debug_level

def convert_unix_timestamp(ts):
    return datetime.utcfromtimestamp(int(ts))

def decompress_gz_file(gz_path):
    xml_path = gz_path[:-3]  # remove .gz
    with gzip.open(gz_path, 'rb') as f_in, open(xml_path, 'wb') as f_out:
        f_out.write(f_in.read())
    return xml_path

def process_dmarc_report(xml_file):
    session = next(get_session())

    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()

        metadata = root.find('report_metadata')
        policy = root.find('policy_published')

        report_info = {
            "report_id": metadata.findtext('report_id', default=""),
            "org_name": metadata.findtext('org_name', default=""),
            "email": metadata.findtext('email', default=""),
            "date_begin": convert_unix_timestamp(metadata.find('date_range/begin').text),
            "date_end": convert_unix_timestamp(metadata.find('date_range/end').text),
            "domain": policy.findtext('domain', default=""),
            "adkim": policy.findtext('adkim', default="r"),
            "aspf": policy.findtext('aspf', default="r"),
            "policy": policy.findtext('p', default="none"),
            "subdomain_policy": policy.findtext('sp', default="none"),
            "pct": int(policy.findtext('pct', default="100")),
        }

        records = []
        for record in root.findall('record'):
            row = record.find('row')
            identifiers = record.find('identifiers')
            auth_results = record.find('auth_results')

            rec = {
                "source_ip": row.findtext('source_ip'),
                "count": int(row.findtext('count')),
                "disposition": row.find('policy_evaluated/disposition').text,
                "dkim_result": row.find('policy_evaluated/dkim').text,
                "spf_result": row.find('policy_evaluated/spf').text,
                "header_from": identifiers.findtext('header_from', default="")
            }

            auth_list = []
            if auth_results is not None:
                for dkim in auth_results.findall('dkim'):
                    auth_list.append({
                        "auth_type": "dkim",
                        "domain": dkim.findtext('domain'),
                        "result": dkim.findtext('result')
                    })
                for spf in auth_results.findall('spf'):
                    auth_list.append({
                        "auth_type": "spf",
                        "domain": spf.findtext('domain'),
                        "result": spf.findtext('result')
                    })

            rec["auth_results"] = auth_list
            records.append(rec)

        existing = session.query(Report).filter_by(report_id=report_info['report_id']).first()
        if existing:
            if debug_level("WARNING"):
                print(f"⚠️  Report already handled : {report_info['report_id']}")
            return

        insert_dmarc_report(session, report_info, records)
        session.commit()
        if debug_level("INFO"):
            print(f"✅ New report found : {report_info['report_id']} ({report_info['org_name']})")
    except Exception as e:
        if debug_level("ERROR"):
            print(f"❌ Error in the file {xml_file}: {e}")
    finally:
        session.close()

        if debug_level("DEBUG"):
            print("SQL Alchemy session closed.")