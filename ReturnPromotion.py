#coding:utf-8
import time
import json
import urllib.request, urllib.error, urllib.parse
import redis
import requests
requests.packages.urllib3.disable_warnings()
import pymysql
import pymysql.cursors
from warnings import filterwarnings
import time
filterwarnings('ignore', category = pymysql.Warning)
test_db_ip = '192.168.1.101'
test_user = 'dddev'
test_passwd = '123456'
test_mainDb='ctcdb_new_test'
test_ckDb='ctcdb_ck_test'
conn_test = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306,charset="utf8")

redis_db_ip='192.168.1.101'
redis_port=6379
headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36',
                      'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8'}
store_url = 'http://192.168.1.251:30011'
global_url='http://192.168.1.251:39000'
def changeIntoStr(data,str_data=''):
    if isinstance(data, str):
        str_data = data.encode('utf-8')
    elif isinstance(data, str):
        str_data = data
    return str_data
server_url='http://192.168.1.251:31010'
#登录
Session=requests.Session()
login_url='http://192.168.1.251:31010/users/login'
login_data = {'userName': 13111111111, 'password': 123456}
login_response = Session.post(url=login_url, data=login_data, headers=headers)
#切换城市
nanjing_url = '{0}/users/updateAgency'.format(server_url)
nanjing_data = {'cityId': 320100, 'agencyId': 101}
nanjing_data_response = Session.post(url=nanjing_url, data=nanjing_data, headers=headers)
#上架单商品
addpr_url='{0}/api/goods/shelve/publish'.format(server_url)


task_num = input('\n1.上架单商品,\n\n2.上架套装\n')
if str(task_num) == str(1):
    input_price = input('请输入上架商品价格：')
    input_dadou=input('请输入达豆立减:')
    addprone_data = {
        "amount": "1",
        "areaPriceStr": "156:1#157:1#166:1#173:1#230:1#232:1#234:1#236:1#238:1#242:1#244:1#248:1#250:1#252:1#256:1#258:1#260:1#262:1#264:1#524:1#526:1#588:1#590:1#592:1#666:1#668:1#670:1#672:1#706:1#708:1#710:1#712:1#714:1#716:1#718:1#720:1#722:1#724:1#726:1#728:1#730:1#732:1#734:1#736:1#738:1#740:1#742:1#744:1#746:1#748:1#780:1#782:1#784:1#786:1#794:1#",
        "catalogId": "4090000",
        "comboType": "0",
        "combos[0][id]": "137469",
        "combos[0][isFree]": "0",
        "combos[0][originalPrice]": "0",
        "combos[0][packageNum]": "1",
        "combos[0][preWarehouseId]": "13",
        "combos[0][price]": "0",
        "combos[0][specification]": "10支*1盒",
        "combos[0][unit]": "件",
        "dadou": input_dadou,
        "endTime": "2018-03-17 23:59:59",
        "id": "137469",
        "isAllFirst": "0",
        "isDirectSell": "0",
        "isDiscount": "1",
        "isHotFirst": "0",
        "isOrderLimit": "unlimited",
        "isTypeFirst": "0",
        "limit": "100",
        "notSoldPriceArea": "[]",
        "onSale": "0",
        "price": input_price,
        "showProduceDate": "1",
        "specification": "规格",
        "startTime": "2018-03-14 10:18:05",
        "title": input_price + "元的商品",
        "type": "0",
        "unit": "件",
        "vip": "0",
        "warehouseId": "13",
        "yjPrice": "0"
    }
    addpr_data_response = Session.post(url=addpr_url, data=addprone_data, headers=headers)
    print(addpr_data_response.text)
    time.sleep(10)
elif str(task_num) == str(2):
    store_name = input('输入店铺登录账号:')
    price1=input('第一个商品价格：')
    price2=input('第二个商品价格：')
    input_dadou = input('请输入达豆立减:')
    price=price1+price2
    addprmany_data = {
        "amount": "1",
        "areaPriceStr": "156:#157:#166:#173:#230:#232:#234:#236:#238:#242:#244:#248:#250:#252:#256:#258:#260:#262:#264:#524:#526:#588:#590:#592:#666:#668:#670:#672:#706:#708:#710:#712:#714:#716:#718:#720:#722:#724:#726:#728:#730:#732:#734:#736:#738:#740:#742:#744:#746:#748:#780:#782:#784:#786:#794:#",
        "catalogId": "4090000",
        "comboType": "2",
        "combos[0][id]": "137558",
        "combos[0][isFree]": "0",
        "combos[0][originalPrice]": price1,
        "combos[0][packageNum]": "1",
        "combos[0][preWarehouseId]": "13",
        "combos[0][price]": "price1",
        "combos[0][specification]": "12*1箱",
        "combos[0][unit]": "件",
        "combos[1][id]": "137469",
        "combos[1][isFree]": "0",
        "combos[1][originalPrice]": price2,
        "combos[1][packageNum]": "1",
        "combos[1][preWarehouseId]": "13",
        "combos[1][price]": price2,
        "combos[1][specification]": "10支*1盒",
        "combos[1][unit]": "件",
        "dadou": input_dadou,
        "endTime": "2018-03-17 23:59:59",
        "id": "137558",
        "isAllFirst": "0",
        "isDirectSell": "0",
        "isDiscount": "1",
        "isHotFirst": "0",
        "isOrderLimit": "unlimited",
        "isTypeFirst": "0",
        "limit": "11",
        "notSoldPriceArea": "[]",
        "onSale": "0",
        "price": price,
        "showProduceDate": "1",
        "specification": "规格",
        "startTime": "2018-03-14 10:59:54",
        "title": "蒙牛11+美美7",
        "type": "0",
        "unit": "件",
        "vip": "0",
        "warehouseId": "13",
        "yjPrice": "0"
    }
    addpr_data_response = Session.post(url=addpr_url, data=addprmany_data, headers=headers)
    print(addpr_data_response.text)
    time.sleep(10)








