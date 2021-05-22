import unittest

import AlertBotsMain.AlertBots as AlertBots
import sys
import datetime

#main = __import__("../main.py")

class TestChangeInSigningInfos(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.data1 = AlertBots.loadJSONFromFile('Tests/signing_infos_test1.json')
        self.data2 = AlertBots.loadJSONFromFile('Tests/signing_infos_test2.json')
        self.data3 = AlertBots.loadJSONFromFile('Tests/signing_infos_test3.json')
        self.data4 = AlertBots.loadJSONFromFile('Tests/signing_infos_test4.json')
        self.data5 = AlertBots.loadJSONFromFile('Tests/signing_infos_test5.json')
        self.data6 = AlertBots.loadJSONFromFile('Tests/signing_infos_test6.json')
        self.data7 = AlertBots.loadJSONFromFile('Tests/signing_infos_test7.json')
        self.data8 = AlertBots.loadJSONFromFile('Tests/signing_infos_test8.json')
        self.data9 = AlertBots.loadJSONFromFile('Tests/signing_infos_test9.json')

    def test_block_height(self):
        """
        New block should always have a larger block height
        """
        self.assertEqual(AlertBots.getChangeInSigningInfos({"height": "11350455"},{"height": "11350455"})[0]['error'],"New Block Height is not larger than old block height")
        self.assertEqual(AlertBots.getChangeInSigningInfos({"height": "200"},{"height": "20"})[0]['error'],"New Block Height is not larger than old block height")
    
    def test_sign_info_change1(self):
        """
        Change detected
        """
        change = AlertBots.getChangeInSigningInfos(self.data2,self.data3)

        self.assertEqual(len(change),1)
        self.assertEqual(change[0]['address'],"swthvalcons1q0a0pk2kjxd8xdjrf2mg6afuwdh4mrp9xst7dk")


    def test_sign_info_change2(self):
        """
        large timestamp to smaller timestamp
        """
        
        #data2
        #jailed_until": "1970-01-01T00:00:00Z",
        
        #data4
        #"jailed_until": "19700-01-01T00:00:00Z",
        
        change = AlertBots.getChangeInSigningInfos(self.data4,self.data2)
        self.assertEqual(len(change),0)

    def test_sign_info_change3(self):
        """
        No change, only block height increases
        """
        change = AlertBots.getChangeInSigningInfos(self.data2,self.data5)
        self.assertEqual(len(change),0)

    def test_sign_info_change4(self):
        """
        No change, only block height increases
        """
        change = AlertBots.getChangeInSigningInfos(self.data1,self.data6)
        self.assertEqual(len(change),0)


    def test_sign_info_change5(self):
        """
        Change detected
        """
        change = AlertBots.getChangeInSigningInfos(self.data1,self.data7)

        self.assertEqual(len(change),1)
        self.assertEqual(change[0]['address'],"swthvalcons1zecfdrf22f6syz8xj4vn8jsvsalxdhwl9tlflk")
        self.assertEqual(change[0]['jailed_until'],datetime.datetime(2021, 3, 10, 11, 44, 20))

    def test_sign_info_change5(self):
        """
        Change detected
        """
        change = AlertBots.getChangeInSigningInfos(self.data1,self.data7)

        self.assertEqual(len(change),1)
        self.assertEqual(change[0]['address'],"swthvalcons1zecfdrf22f6syz8xj4vn8jsvsalxdhwl9tlflk")
        self.assertEqual(change[0]['jailed_until'],datetime.datetime(2021, 3, 10, 11, 44, 20))


    def test_sign_info_change6(self):
        """
        Change detected for 2 validators
        """
        change = AlertBots.getChangeInSigningInfos(self.data1,self.data8)

        self.assertEqual(len(change),2)

        self.assertEqual(change[0]['address'],"swthvalcons1yv4v5q0wygl4aypnsr63fkyyuz87vhyh76qzp7")
        self.assertEqual(change[0]['jailed_until'],datetime.datetime(2021, 1, 1, 0, 0))

        self.assertEqual(change[1]['address'],"swthvalcons1t7pxus2dc87786x5998zgxgk80unaj4tjwh0lz")
        self.assertEqual(change[1]['jailed_until'],datetime.datetime(2020, 12, 22, 11, 20, 20))


    def test_sign_info_change7(self):
        """
        Change detected for 2 validators
        """
        change = AlertBots.getChangeInSigningInfos(self.data1,self.data9)
        self.assertEqual(len(change),0)

class TestAlertMessageSigningInfos(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.data1 = AlertBots.loadJSONFromFile('Tests/signing_infos_test1.json')
        self.data2 = AlertBots.loadJSONFromFile('Tests/signing_infos_test2.json')
        self.data3 = AlertBots.loadJSONFromFile('Tests/signing_infos_test3.json')
        self.data4 = AlertBots.loadJSONFromFile('Tests/signing_infos_test4.json')
        self.data5 = AlertBots.loadJSONFromFile('Tests/signing_infos_test5.json')
        self.data6 = AlertBots.loadJSONFromFile('Tests/signing_infos_test6.json')
        self.data7 = AlertBots.loadJSONFromFile('Tests/signing_infos_test7.json')
        self.data8 = AlertBots.loadJSONFromFile('Tests/signing_infos_test8.json')
        self.data9 = AlertBots.loadJSONFromFile('Tests/signing_infos_test9.json')

    def test_alert_0(self):
        message = AlertBots.alertMessageSigningInfos([{'error': 'New Block Height is not larger than old block height'}])
        self.assertEqual(message,'0')

    def test_alert_2(self):
        message = AlertBots.alertMessageSigningInfos([])
        self.assertEqual(message,'1')

    def test_alert_3(self):
        changes = [ {'address':'abc', 'jailed_until': datetime.datetime(2021, 3, 10, 11, 44, 20)} ]
        message = AlertBots.alertMessageSigningInfos(changes)
        print(message)
        self.assertEqual(len(message),1)

    def test_alert_4(self):
        changes = [{'address':'abc', 'jailed_until':datetime.datetime(2000, 3, 10, 11, 44, 20)},{'address':'abcd', 'jailed_until':datetime.datetime(2021, 4, 20, 0, 6, 9)}]
        message = AlertBots.alertMessageSigningInfos(changes)
        print(message)
        self.assertEqual(len(message),2)

    def test_alert_5(self):
        changes = AlertBots.getChangeInSigningInfos(self.data1,self.data8)
        message = AlertBots.alertMessageSigningInfos(changes)
        print(message)
        self.assertEqual(len(message),2)



if __name__ == '__main__':
    unittest.main()