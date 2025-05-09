import os
from app.dmarc.processor import process_dmarc_report
from config.settings import debug_level, FEEDER_DIR

def process_reports_from_directory():
    """
    Parcourt le dossier FEEDER_DIR pour détecter et traiter
    tous les fichiers DMARC .xml présents.
    """
    if not os.path.exists(FEEDER_DIR):
        print(f"📁 Folder {FEEDER_DIR} not found, creating it now...")
        os.makedirs(FEEDER_DIR)

    files = os.listdir(FEEDER_DIR)
    xml_files = [f for f in files if f.lower().endswith(".xml")]

    if not xml_files:
        if debug_level("INFO"):
            print(f"📂 No .xml file found in the DMARC Feeder folder : {FEEDER_DIR}")
        return

    for filename in xml_files:
        filepath = os.path.join(FEEDER_DIR, filename)
        try:
            if debug_level("INFO"):
                print(f"📥 Handling file : {filename}")
            process_dmarc_report(filepath)
        except Exception as e:
            if debug_level("ERROR"):
                print(f"❌ Error while handling file {filename} : {e}")
