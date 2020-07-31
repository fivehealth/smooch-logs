__all__ = ['SmoochWebSession', 'SMOOCH_BASE_URL']

import logging
from tempfile import TemporaryDirectory
import os
import platform

import requests
from requests.exceptions import HTTPError

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located

logger = logging.getLogger(__name__)

if platform.system() in ['Darwin']:
    from webdriver_manager.chrome import ChromeDriverManager
    CHROME_DRIVER_LOCATION = ChromeDriverManager().install()

else:
    CHROME_DRIVER_LOCATION = 'chromedriver'
#end if

SMOOCH_BASE_URL = os.environ.get('SMOOCH_BASE_URL', 'https://app.smooch.io')


class SmoochWebSession():
    WAIT_TIMEOUT = 10

    def __init__(self, chrome_binary_location=None, username=None, password=None, session_id=None, logout=True):
        self.username = username or os.environ['SMOOCH_USERNAME']
        self.password = password or os.environ['SMOOCH_PASSWORD']

        self.chrome_binary_location = chrome_binary_location
        self.session_id = session_id
        self.logout = logout
    #end def

    def __enter__(self):
        self._session = None

        if self.session_id:
            session = requests.Session()
            session.headers.update({
                'X-Requested-With': 'XMLHttpRequest',
                'Referer': SMOOCH_BASE_URL,
            })

            logger.debug(f'Session ID is <{self.session_id}>.')
            cookie_jar = requests.cookies.RequestsCookieJar()
            cookie_jar.set('sessionId', self.session_id)
            session.cookies = cookie_jar

            self._session = session
        #end if

        if not self._session_is_valid():
            self._login()

        return self._session
    #end def

    def _login(self):
        with TemporaryDirectory() as temp_dir:
            logger.debug(f'Using <{temp_dir}> as temporary directory for chrome.')

            chrome_options = webdriver.ChromeOptions()

            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument('--enable-logging')
            chrome_options.add_argument('--single-process')

            with webdriver.Chrome(executable_path=CHROME_DRIVER_LOCATION, options=chrome_options) as driver:
                driver.get(SMOOCH_BASE_URL)

                elem = driver.find_element_by_name('email')
                elem.clear()
                elem.send_keys(self.username)

                elem = driver.find_element_by_name('password')
                elem.clear()
                elem.send_keys(self.password)
                elem.send_keys(Keys.RETURN)

                elem = WebDriverWait(driver, self.WAIT_TIMEOUT).until(presence_of_element_located((By.XPATH, f'//a/small[contains(text(),"{self.username}")]')))
                elem = WebDriverWait(driver, self.WAIT_TIMEOUT).until(presence_of_element_located((By.XPATH, '//*[text()="Create new app"]')))
                logger.info(f'Login for <{self.username}> successful.')
                # logger.debug(f'Cookies are: {driver.get_cookies()}')

                session = requests.Session()
                session.headers.update({
                    'X-Requested-With': 'XMLHttpRequest',
                    'Referer': SMOOCH_BASE_URL,
                })

                session_id = driver.get_cookie('sessionId')['value']
                logger.debug(f'Session ID is <{session_id}>.')
                cookie_jar = requests.cookies.RequestsCookieJar()
                cookie_jar.set('sessionId', session_id)
                session.cookies = cookie_jar

                self._session = session

                driver.close()
            #end with
        #end with

        return self._session
    #end def

    def __exit__(self, *exc):
        if not self._session or not self.logout:
            return

        try:
            r = self._session.post(f'{SMOOCH_BASE_URL}/webapi/logout', data='{}')
            r.raise_for_status()

        except HTTPError:
            logger.warning('HTTPError while logging out.')

        else:
            logger.info(f'Smooch session logout successful.')
        #end try

        self._session = None
    #end def

    def _session_is_valid(self):
        if self._session:
            try:
                r = self._session.get(f'{SMOOCH_BASE_URL}/webapi/users/me')
                r.raise_for_status()

            except HTTPError:
                logger.debug(f'Current session is invalidated. Will login again.')
                self._session = None

            else:
                logger.debug(f'Current session is still valid.')
                return True
            #end try
        #end if
    #end def
#end class
