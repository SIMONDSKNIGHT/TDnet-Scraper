import os
import re
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime, timedelta
from scraper.document_finder import DocumentFinder
from scraper.pdf_downloader import PDFDownloader
from config.settings import BASE_URL, HEADERS

ID_SOURCE = "resources/ids.txt"
def get_base_path():
    if getattr(sys, 'frozen', False):
        # If the application is running from a PyInstaller bundle
        return sys._MEIPASS
    else:
        # If running normally
        return os.path.dirname(os.path.abspath(__file__))

BASE_DIR = get_base_path()
ID_SOURCE = os.path.join(BASE_DIR, ID_SOURCE)  # Ensures proper path handling


def initialize_dates_and_folder(start_date, end_date, query, use_id_list, filter_query, download_path):
    pattern = re.compile(r"(\d{8})~(\d{8})-(.+)")
    new_folder_name_with_path = None

    # Format the filter query to be part of the folder name
    formatted_filter_query = filter_query.replace('+', 'AND').replace(',', 'OR')
    
    # Create a new folder name with the query, filter query, and ID list status
    new_folder_name = f"{start_date}~{end_date}-{query}-{'ID' if use_id_list else 'NoID'}-{formatted_filter_query}"
    new_folder_name_with_path = os.path.join(download_path, new_folder_name)

    # New logic: If the folder already exists, delete it and create a new one
    if os.path.exists(new_folder_name_with_path):
        for root, dirs, files in os.walk(new_folder_name_with_path, topdown=False):
            for file in files:
                os.remove(os.path.join(root, file))
            for directory in dirs:
                os.rmdir(os.path.join(root, directory))
        os.rmdir(new_folder_name_with_path)

    os.makedirs(new_folder_name_with_path)

    return start_date, end_date, new_folder_name_with_path

def download_pdfs(start_date, end_date, query, filter_query, use_id_list, reset_metadata, download_path):
    start_date, end_date, new_file_path = initialize_dates_and_folder(start_date, end_date, query, use_id_list, filter_query, download_path)

    search_criteria = {
        "t0": start_date,
        "t1": end_date,
        "q": query,
        "m": "0"
    }
    
    if not os.path.exists(download_path):
        os.makedirs(download_path)

    if reset_metadata:
        metadata_file = os.path.join(download_path, 'metadata.json')
        if os.path.exists(metadata_file):
            os.remove(metadata_file)
            messagebox.showinfo("Metadata Reset", "Metadata file has been reset.")

    id_list = None
    if use_id_list:
        with open(ID_SOURCE, "r") as f:
            id_list = f.read().splitlines()

    finder = DocumentFinder(BASE_URL, HEADERS, search_criteria, id_list, use_id_list)
    downloader = PDFDownloader(new_file_path, BASE_URL)

    documents = finder.find_documents()
    filtered_documents = finder.apply_filters(documents, filter_query or "")
    found = len(filtered_documents)

    for link, metadata in filtered_documents:
        downloader.download_pdf(link, metadata)

    metadata_file = os.path.join(new_file_path, 'metadata.json')
    downloader.save_metadata(metadata_file)
    
    messagebox.showinfo("Success", f"{found} PDFs downloaded successfully!")

def on_download_click():
    start_date = start_date_entry.get()
    end_date = end_date_entry.get()
    query = query_entry.get()
    filter_query = filter_entry.get()
    use_id_list = use_id_var.get()
    reset_metadata = reset_metadata_var.get()
    download_path = download_path_entry.get()

    if not start_date or not end_date or not query or not download_path:
        messagebox.showwarning("Input Error", "Please fill in all required fields.")
        return

    download_pdfs(start_date, end_date, query, filter_query, use_id_list, reset_metadata, download_path)

def get_default_dates():
    end_date = datetime.today()
    start_date = end_date - timedelta(days=30)
    return start_date.strftime('%Y%m%d'), end_date.strftime('%Y%m%d')

def choose_download_folder():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        download_path_entry.delete(0, tk.END)
        download_path_entry.insert(0, folder_selected)

# Get the user's default "Downloads" directory
default_download_path = os.path.join(os.path.expanduser("~"), "Downloads")

# Initialize default dates
default_start_date, default_end_date = get_default_dates()

app = tk.Tk()
app.title("PDF Downloader")

tk.Label(app, text="Start Date (YYYYMMDD)").grid(row=0, column=0, padx=10, pady=10)
start_date_entry = tk.Entry(app)
start_date_entry.insert(0, default_start_date)
start_date_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(app, text="End Date (YYYYMMDD)").grid(row=1, column=0, padx=10, pady=10)
end_date_entry = tk.Entry(app)
end_date_entry.insert(0, default_end_date)
end_date_entry.grid(row=1, column=1, padx=10, pady=10)

tk.Label(app, text="Primary Query").grid(row=2, column=0, padx=10, pady=10)
query_entry = tk.Entry(app)
query_entry.insert(0, "異動")  # Set default query to "異動"
query_entry.grid(row=2, column=1, padx=10, pady=10)

tk.Label(app, text="Filter Query (Optional)\nUse '+' as AND and ',' as OR ").grid(row=3, column=0, padx=10, pady=10)
filter_entry = tk.Entry(app)
filter_entry.insert(0, "役員, 取締, 執行, 人事異動")  # Set default filter query options
filter_entry.grid(row=3, column=1, padx=10, pady=10)

tk.Label(app, text="Download Folder").grid(row=4, column=0, padx=10, pady=10)
download_path_entry = tk.Entry(app)
download_path_entry.insert(0, default_download_path)  # Default to Downloads folder
download_path_entry.grid(row=4, column=1, padx=10, pady=10)

choose_folder_button = tk.Button(app, text="Browse...", command=choose_download_folder)
choose_folder_button.grid(row=4, column=2, padx=10, pady=10)

use_id_var = tk.BooleanVar(value=True)  
use_id_checkbox = tk.Checkbutton(app, text="Use ID List", variable=use_id_var)
use_id_checkbox.grid(row=5, column=0, columnspan=2, pady=10)

reset_metadata_var = tk.BooleanVar(value=True)
reset_metadata_checkbox = tk.Checkbutton(app, text="Reset Metadata", variable=reset_metadata_var)
reset_metadata_checkbox.grid(row=6, column=0, columnspan=2, pady=10)

download_button = tk.Button(app, text="Download PDFs", command=on_download_click)
download_button.grid(row=7, column=0, columnspan=2, pady=20)

app.mainloop()
