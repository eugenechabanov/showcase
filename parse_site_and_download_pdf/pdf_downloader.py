from functools import wraps

from playwright._impl._errors import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from page.page import SitePage
from utils import download_using_requests, save_factsheet, log_to_file


def retry_on_timeout(max_retries=2):
    def decorator(func):
        @wraps(func)
        def wrapper(self, site_page, source, *args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(self, site_page, source, *args, **kwargs)
                except PlaywrightTimeoutError as e:
                    attempts += 1
                    print(f"TimeoutError encountered for ISIN {source['isin']}, retrying {attempts}/{max_retries}...")
                    site_page.handle_timeout()
            log_to_file(f"Max retries reached for ISIN {source['isin']}.", also_print=True)
            return  # Continue to the next source if max retries are reached
        return wrapper
    return decorator


class SitePDFDownloader:
    """A class to manage the downloading of PDF documents from the <Under NDA> website.

    This class processes a list of ISINs, selecting the appropriate investor profile
    and downloading PDFs as needed. It minimizes unnecessary interactions by keeping track
    of the investor profile based on the ISIN's country code.

    Overall logic:
    The parser processes a given list of funds, takes their corresponding ISINs and searches for them on <Under NDA>
    via the search bar. It always selects the "Professional Investor" option and switches the country based on
    the ISIN’s country code (for example, "DK0124568" corresponds to Denmark).
    If the country from the ISIN is not available in <Under NDA>'s list,
    the parser tries a short list of other fallback codes.
    """
    FALLBACK_COUNTRY_CODES = ["GB", "LU", "DE", "CH"]
    BASE_URL = "https://<Under NDA>"

    def __init__(self, sources):
        self.sources = sources
        self.previous_country_code = None
        self.n = 1

    @retry_on_timeout(max_retries=2)
    def download_pdf(self, site_page, source):
        isin = source['isin']

        print(f"{self.n}/{len(self.sources)} - {isin} - {source['fund_name']}")

        country_code = isin[:2]  # Get the country code from the first 2 letters of ISIN

        if country_code != self.previous_country_code:
            site_page.choose_investor_profile(country_code)
            site_page.agree_to_terms()

        pdf_found = False
        for code in [country_code] + SitePDFDownloader.FALLBACK_COUNTRY_CODES:
            if not pdf_found:       # Change country profile and try to find PDF
                if code != country_code:
                    site_page.choose_investor_profile(code)
                    site_page.agree_to_terms()
                site_page.search_by_isin(isin)
                pdf_link = site_page.get_pdf_link()

                if pdf_link:
                    print(f"PDF link for ISIN {isin}: {pdf_link}")
                    filename = download_using_requests(pdf_link, isin)
                    save_factsheet(source['obj'], filename)
                    print(f"Saved to database: '{filename}'.\n")
                    pdf_found = True
                else:
                    print(f"No PDF link found for ISIN {isin} with Country Code {code}, trying next country.")

        if not pdf_found:
            log_message = f"No PDF found after trying all fallback countries for ISIN {isin}, skipping..."
            log_to_file(log_message, also_print=True)

        self.previous_country_code = country_code
        self.n += 1

    def run(self):
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()

            site_page = SitePage(page)

            site_page.open_site(SitePDFDownloader.BASE_URL)
            site_page.click_accept()

            for source in self.sources:
                self.download_pdf(site_page, source)

            browser.close()
