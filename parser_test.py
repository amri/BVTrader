import datetime
import time
from xml.etree import ElementTree
import requests
import unittest
import urllib3
import configparser

__author__ = 'Amri'

class BVTrader(object):

    API_POST_AUTHENTICATE = "https://live.bullionvault.com/secure/j_security_check"
    API_GET_SESSION = "https://live.bullionvault.com/secure/login.do"
    API_GET_VIEW_MARKET = "https://live.bullionvault.com/secure/api/v2/view_market_xml.do"

    def authenticate(self):
        parser2 = configparser.ConfigParser()
        parser2.read("configuration.ini")
        user = parser2.get("authentication","username")
        pasw = parser2.get("authentication","password")
        response = requests.get(self.API_GET_SESSION)
        response = requests.post(self.API_POST_AUTHENTICATE, cookies=response.cookies, data={'j_username': user, 'j_password': pasw})
        return response

    def get_raw_market_data(self):
        http = urllib3.PoolManager()
        request = http.request("GET", self.API_GET_VIEW_MARKET)
        xml_file = request.data
        return xml_file

    def get_market_data(self, security_class, security_id, currency):
        root = ElementTree.fromstring(self.get_raw_market_data())

        i = 0
        for market in root.iter("pitch"):
            sec_class = market.get("securityClassNarrative")
            sec_id = market.get("securityId")
            curr = market.get("considerationCurrency")
            if sec_class == security_class and sec_id == security_id and curr == currency:
                buy_price = list(list(market)[0])[0]
                sell_price = list(list(market)[1])[0]
                print("Buy: {0} at {1}".format(buy_price.get("quantity"), buy_price.get("limit")))
                print("Sell: {0} at {1}".format(sell_price.get("quantity"), sell_price.get("limit")))


class TestParser(unittest.TestCase):

    def setUp(self):
        self.trader = BVTrader()
        
    def test_read_xml(self):
        result = self.trader.add(1, 2)
        self.assertEqual(result, 3)
        
    def test_read_xml_from_url(self):
        content = self.trader.get_raw_market_data()
        self.assertTrue(len(content) > 1)

    def test_get_market_data(self):
        while True:
            print(datetime.datetime.now())
            self.trader.get_market_data("GOLD", "AUXLN", "EUR")
            time.sleep(59)

    def test_valid_login(self):
        response = self.trader.authenticate()
        self.assertIn("accountLinkContainer",response.content.decode())

if __name__ == "__main__":
    unittest.main()