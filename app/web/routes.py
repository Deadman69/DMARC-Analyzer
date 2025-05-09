import os
import gzip
from flask import request, Response, jsonify, url_for
from sqlalchemy import func
from app.database.session import SessionLocal
from app.database.models import Report, Record
from config.settings import FEEDER_DIR, IMAP_DOWNLOAD_DIR

def register_routes(app):
    @app.route("/health", methods=["GET"])
    def health_check():
        return jsonify({"status": "ok"})

    @app.route("/reports", methods=["GET"])
    def get_reports():
        session = SessionLocal()
        try:
            reports_with_counts = (
                session.query(
                    Report,
                    func.coalesce(func.sum(Record.count), 0).label("email_count")
                )
                .outerjoin(Report.records)
                .group_by(Report.id)
                .order_by(Report.date_end.desc())
                .limit(10)
                .all()
            )

            result = [{
                "id": r.id,
                "domain": r.domain,
                "date_begin": r.date_begin.isoformat(),
                "date_end": r.date_end.isoformat(),
                "policy": r.policy,
                "org_name": r.org_name,
                "email_count": email_count
            } for r, email_count in reports_with_counts]

            return jsonify(result)
        finally:
            session.close()

    @app.route("/report/<int:report_id>", methods=["GET"])
    def get_report_detail(report_id):
        session = SessionLocal()
        try:
            report = session.query(Report).filter(Report.id == report_id).first()
            if not report:
                return jsonify({"error": "Report not found"}), 404

            return jsonify({
                "id": report.id,
                "domain": report.domain,
                "date_begin": report.date_begin.isoformat(),
                "date_end": report.date_end.isoformat(),
                "policy": report.policy,
                "org_name": report.org_name,
                "email": report.email,
                "pct": report.pct,
                "adkim": report.adkim,
                "aspf": report.aspf
            })
        finally:
            session.close()


    @app.route("/report/<int:report_id>/xml", methods=["GET"])
    def get_report_xml(report_id):
        session = SessionLocal()
        try:
            report = session.query(Report).filter(Report.id == report_id).first()
            if not report:
                return jsonify({"error": "Report not found"}), 404

            search_dirs = [FEEDER_DIR, IMAP_DOWNLOAD_DIR]
            found_path = None

            # Search for the XML file in the specified directories
            for directory in search_dirs:
                for file in os.listdir(directory):
                    if file.endswith(".xml") or file.endswith(".xml.gz"):
                        if str(report_id) in file:
                            found_path = os.path.join(directory, file)
                            break
                if found_path:
                    break

            if not found_path:
                return jsonify({"error": "XML file not found for this report ID (" + str(report_id) + ")"}), 404

            if found_path.endswith(".gz"):
                with gzip.open(found_path, "rt", encoding="utf-8") as f:
                    content = f.read()
            else:
                with open(found_path, "r", encoding="utf-8") as f:
                    content = f.read()

            return Response(content, mimetype="application/xml")

        finally:
            session.close()


    @app.route("/emails", methods=["GET"])
    def get_emails():
        try:
            page     = max(int(request.args.get("page", 1)), 1)
            per_page = min(int(request.args.get("per_page", 50)), 200)
        except ValueError:
            return jsonify({"error": "Invalid pagination parameters"}), 400

        session = SessionLocal()
        try:
            q = session.query(Record)

            # 1) Dispositions (none, quarantine, reject)
            dispositions = request.args.getlist("disposition")
            if dispositions:
                q = q.filter(Record.disposition.in_(dispositions))

            # 2) SPF (pass, fail)
            spfs = request.args.getlist("spf")
            if spfs:
                q = q.filter(Record.spf_result.in_(spfs))

            # 3) DKIM (pass, fail)
            dkims = request.args.getlist("dkim")
            if dkims:
                q = q.filter(Record.dkim_result.in_(dkims))

            # Total before pagination
            total = q.count()

            # Offset + limit
            items = q.offset((page-1)*per_page).limit(per_page).all()

            # Serialization
            data = [{
                "report_id": r.report_id,
                "source_ip":  r.source_ip,
                "header_from":r.header_from,
                "disposition":r.disposition,
                "spf_result": r.spf_result,
                "dkim_result":r.dkim_result
            } for r in items]

            # Navigation links
            def make_url(p):
                args = request.args.to_dict(flat=False)
                args["page"] = [str(p)]
                args["per_page"] = [str(per_page)]
                return url_for("get_emails", _external=True, **args)

            meta = {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": (total + per_page - 1) // per_page,
                "prev": make_url(page-1) if page>1 else None,
                "next": make_url(page+1) if page*per_page<total else None
            }

            return jsonify({"meta": meta, "data": data})
        finally:
            session.close()
