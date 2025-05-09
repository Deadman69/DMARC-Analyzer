import asyncio
from app.services.imap_handler import check_incoming_emails
from app.services.folder_watcher import process_reports_from_directory
from config.settings import debug_level

IMAP_CHECK_INTERVAL_SECONDS = 5  # 5 min

async def worker_loop():
    while True:
        if debug_level("INFO"):
            print("🔄 Checking IMAP and folder for DMARC reports...")
        
        try:
            check_incoming_emails()
        except Exception as e:
            if debug_level("ERROR"):
                print(f"❌ IMAP error: {e}")

        process_reports_from_directory()
        await asyncio.sleep(IMAP_CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(worker_loop())
