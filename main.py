import argparse
import os
# main.py
from scraper.document_finder import DocumentFinder
from scraper.pdf_downloader import PDFDownloader
from config.settings import BASE_URL, DOWNLOAD_PATH, HEADERS

def main(start_date, end_date, query, dates):
    search_criteria = {
        "t0": start_date,
        "t1": end_date,
        "q": query,
        "m": "0"
    }
    """if the downloads folder doesn't exist, make it"""
    
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
    if not os.path.exists(os.path.join(DOWNLOAD_PATH, dates)):
        os.makedirs(os.path.join(DOWNLOAD_PATH, dates))



    finder = DocumentFinder(BASE_URL,HEADERS, search_criteria)
    downloader = PDFDownloader(os.path.join(DOWNLOAD_PATH, dates),BASE_URL)


    documents = finder.find_documents()
    for link, metadata in documents:
        downloader.download_pdf(link, metadata)

    # Save metadata to a file
    metadata_file = os.path.join(DOWNLOAD_PATH, 'metadata.json')
    downloader.save_metadata(metadata_file)
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download PDF documents from a website.")
    #todays date in YYMMDD format
    parser.add_argument("start_date", help="Start date for the search in YYYYMMDD format")
    parser.add_argument("end_date", help="End date for the search in YYYYMMDD format")
    parser.add_argument("query", help="Search query")
    
    args = parser.parse_args()
    #string start to end date separated by tilde
    dates = args.start_date + "~" + args.end_date
    main(args.start_date, args.end_date, args.query, dates)