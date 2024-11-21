class SiteLocators:
    ACCEPT_ALL_BUTTON = "#qc-cmp2-ui button[mode='primary']"
    COUNTRY_SELECTOR = ".country-selector"
    INVESTOR_COUNTRY_BUTTON = ".fund-market-type"
    PROFESSIONAL_INVESTOR_RADIO_BUTTON_LABEL = "label[for='professional']"
    COUNTRY_ITEM = ".countryItem[data-cc='{country_code}']"
    TOS_CHECKBOX = "label[for='fund-market-checkbox-mandatory'] span"
    CONFIRM_BUTTON = ".btn.fundmarket-btn.confirm"
    SEARCH_INPUT_CONTAINER = ".input-container"
    SEARCH_BUTTON = "button[type='submit']"
    PDF_REVEAL_BUTTON = "ul.list div[data-name='MR']:visible"
    DATA_EMPTY_LOCATOR = PDF_REVEAL_BUTTON
    NO_PDF_ELEMENT = "ul.list li.not-member"
    PDF_LINK = "ul.list div[data-name='MR'] li a.fancybox"
