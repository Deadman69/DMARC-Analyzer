from app.database.models import Report, Record, AuthResult

def insert_dmarc_report(session, report_info, records_data):
    """
    Inserts a complete DMARC report into the database.

    :param session: Active SQLAlchemy session
    :param report_info: Dictionary containing the report metadata
    :param records_data: List of dictionaries containing the associated records
    """
    # 1. Creation of the main report
    report = Report(
        report_id=report_info["report_id"],
        org_name=report_info["org_name"],
        email=report_info["email"],
        date_begin=report_info["date_begin"],
        date_end=report_info["date_end"],
        domain=report_info["domain"],
        adkim=report_info["adkim"],
        aspf=report_info["aspf"],
        policy=report_info["policy"],
        subdomain_policy=report_info["subdomain_policy"],
        pct=report_info["pct"]
    )
    session.add(report)
    session.flush()

    # 2. Insertion of linked records
    for record_data in records_data:
        record = Record(
            report_id=report.id,
            source_ip=record_data["source_ip"],
            count=record_data["count"],
            disposition=record_data["disposition"],
            dkim_result=record_data["dkim_result"],
            spf_result=record_data["spf_result"],
            header_from=record_data["header_from"]
        )
        session.add(record)
        session.flush()

        # 3. Insertion of authentication results for each record
        for auth in record_data.get("auth_results", []):
            auth_result = AuthResult(
                record_id=record.id,
                auth_type=auth["auth_type"],
                domain=auth["domain"],
                result=auth["result"]
            )
            session.add(auth_result)

    # 4. Commit outside to allow batching multiple insertions
    # (the commit is handled in the calling function to manage errors globally)

