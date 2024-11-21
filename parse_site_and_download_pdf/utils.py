from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from urllib.parse import unquote

import requests
from django.core.files import File as FileObj
from factsheets.models import Factsheet


def download_using_requests(pdf_link, isin):
    response = requests.get(
        pdf_link,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        },
    )
    if response.status_code == 200:
        # Get the filename from the Content-Disposition header if available
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition:
            # Extract the filename from the header
            filename = content_disposition.split('filename=')[1].strip('"')
            # Decode the filename if it contains URL-encoded characters
            filename = unquote(filename)
        else:
            # Fallback to a generic filename if not available
            filename = f"{datetime.now().strftime('%Y-%m-%d')}_{isin}.pdf"

        with open(filename, 'wb') as file:
            file.write(response.content)
        print(f'Successfully downloaded: {filename}')
        return filename
    else:
        print(f'Failed to download PDF: {response.status_code}\n\n')


def save_factsheet(source, filename):
    def save_factsheet_query(source, filename):
        date = filename.replace('.pdf', '').split('_')[-1]
        with open(filename, 'rb') as f:
            factsheet = Factsheet.objects.get_or_create(
                name=filename,
                defaults=dict(
                    date=date,
                    source=source,
                )
            )[0]
            factsheet.file = FileObj(f)
            factsheet.save()

    with ThreadPoolExecutor() as executor:
        future = executor.submit(save_factsheet_query, source, filename)
        result = future.result()
    return result


def log_to_file(message, also_print=False):
    """Temporary function for logging errors to a file. Was later replaced with Django logger"""
    with open("logfile.txt", "a") as file:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        file.write(f"{timestamp} - {message}\n")
    if also_print:
        print(message + "\n\n")
