from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError

from locators import SiteLocators


class SitePage:
    """A page object representing the <Under NDA> website for PDF downloads.

    This class encapsulates all interactions with the <Under NDA> webpage, allowing
    the user to select investor profiles, agree to terms of service, search for ISINs,
    and download corresponding PDF documents.
    On TimeoutError, retries page reload twice.

    Attributes:
        page (Page): The Playwright Page object used for browser interactions.
    """
    COUNTRY_CODES_LIST = [
        'CH', 'DE', 'GB', 'AT', 'BE', 'CY', 'CZ', 'DK', 'FI',
        'FR', 'GR', 'HK', 'HU', 'IS', 'IE', 'IT', 'LI', 'LU',
        'MT', 'NL', 'NO', 'PT', 'SG', 'ES', 'SE'
    ]

    def __init__(self, page: Page):
        self.page = page

    def open_site(self, base_url: str):
        self.page.goto(base_url, wait_until="load")

    def handle_timeout(self):
        self.page.reload(wait_until="load")

    def click_accept(self):
        accept_button = self.page.locator(SiteLocators.ACCEPT_ALL_BUTTON).first
        try:
            accept_button.wait_for(state="visible", timeout=5000)
            if accept_button.is_visible():
                accept_button.click()
                print("Clicked on Accept Cookies banner.")
        except PlaywrightTimeoutError:
            print("Accept Cookies banner is not displayed. Moving on.")

    def choose_investor_profile(self, country_code: str):
        if country_code not in SitePage.COUNTRY_CODES_LIST:
            country_code = 'GB'     # fallback country

        country_selector = SiteLocators.COUNTRY_ITEM.format(country_code=country_code)
        self.page.click(SiteLocators.INVESTOR_COUNTRY_BUTTON)

        self.page.wait_for_selector(country_selector)
        self.page.click(SiteLocators.COUNTRY_SELECTOR)
        self.page.click(country_selector)
        self.page.click(SiteLocators.PROFESSIONAL_INVESTOR_RADIO_BUTTON_LABEL)

    def agree_to_terms(self):
        self.page.click(SiteLocators.TOS_CHECKBOX)  # Click checkbox to agree to TOS
        self.page.click(SiteLocators.CONFIRM_BUTTON)  # Confirm button

    def search_by_isin(self, isin: str):
        self.page.wait_for_selector(SiteLocators.SEARCH_INPUT_CONTAINER)
        self.page.click(SiteLocators.SEARCH_INPUT_CONTAINER)  # Click on search bar input
        self.page.fill(f"{SiteLocators.SEARCH_INPUT_CONTAINER} input", isin)  # Input ISIN
        self.page.click(SiteLocators.SEARCH_BUTTON)  # Submit search request

    def wait_for_load_state_idle(self):
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                self.page.wait_for_load_state('networkidle')
                break
            except PlaywrightTimeoutError:
                if attempt < max_retries:
                    self.page.reload()
                else:
                    print("Failed to load page after", max_retries, "retries.")

    def get_pdf_link(self) -> str | None:
        self.wait_for_load_state_idle()
        pdf_element = self.page.query_selector(SiteLocators.PDF_REVEAL_BUTTON)
        if pdf_element:
            data_empty_value = self.page.get_attribute(SiteLocators.DATA_EMPTY_LOCATOR, "data-empty")
            if data_empty_value != "true":
                self.page.hover(SiteLocators.PDF_REVEAL_BUTTON)  # Reveals the PDF URL
                pdf_link = self.page.get_attribute(SiteLocators.PDF_LINK, "href")
                return pdf_link
