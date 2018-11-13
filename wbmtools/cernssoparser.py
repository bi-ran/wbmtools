# -----------------------------------------------------------------------------
# Name:        cern sso website parser
# Purpose:     read content of a cern sso protected website in python
#
# Author:      Sam Harper
#
# Created:     01.08.2015
# Copyright:   (c) Sam Harper 2015
# Licence:     GPLv3
# -----------------------------------------------------------------------------
import os
import sys
import requests
import cern_sso

class SSOSession:
    """ manages a cern single sign on session

    authenticates the CERN single sign on (sso) system allowing sso protected
    pages to be accessed.
    """

    def __init__(self):
        self._check_valid_setup()
        self.session = requests.Session()
        self.cookies = None


    def _check_valid_setup(self):
        cert_location = os.environ.get('REQUESTS_CA_BUNDLE')
        if cert_location is None:
            print("please set the enviroment varible REQUESTS_CA_BUNDLE "
                  "to point to the location of the CERN CA certs")
            sys.exit()

        if os.path.isfile(cert_location) is False:
            print("cern ca certs location {} doesnt exist, please set "
                  "REQUESTS_CA_BUNDLE to the correct location".format(cert_location))
            sys.exit()


    def read_url(self, url):
        if not self.cookies:
            try:
                self.cookies = cern_sso.krb_sign_on(url)
            except requests.exceptions.HTTPError as ex:
                print("  error in obtaining kerberos cookies\n", ex)
                sys.exit()

        for _ in range(3):
            try:
                data = self.session.get(url, cookies=self.cookies)
                break
            except requests.exceptions.ConnectionError:
                print("  connection error, retrying...")
                pass

        return data.text
