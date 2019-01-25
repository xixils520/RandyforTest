#coding:utf-8
#加注释本地修改的，马上提交
import time
import json
import urllib.request, urllib.error, urllib.parse
import redis
import requests
requests.packages.urllib3.disable_warnings()
# import pymysql
import pymysql
import pymysql.cursors
from warnings import filterwarnings
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

def createName():
    """
    :return:返回自动创建名字
    """
    couponName = '自动测' + str(int(time.time()))
    return couponName

def createTime():
    """
    :return: 返回发放开始时间，发放结束时间，可使用开始时间，可使用结束时间
    """
    grantStart = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()- 1* 60 * 60))
    useStart = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()- 2* 60 * 60))
    useEnd = grantEnd = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 24 * 60 * 60))
    return grantStart, grantEnd, useStart, useEnd

def createCouponTime():
    """
    南京的税换开始时间>可用开始时间
    :return: 返回发放开始时间，发放结束时间，可使用开始时间，可使用结束时间
    """
    grantStart = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()-24*60*60))
    useStart = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    useEnd = time.strftime('%Y-%m-%d', time.localtime(time.time() + 24 * 60 * 60))
    grantEnd = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 24 * 60 * 60))
    return grantStart, grantEnd, useStart, useEnd


def createRedGift(cityId,agencyId,server_url,url_username,url_password,redGift_value,redGift_quantity,redGift_ownLimit,redGift_useBaseLine,redGift_instruction):
    session = requests.Session()
    name = createName()
    grantStart, grantEnd, useStart, useEnd = createTime()
    # 登录
    login_url = '{0}/users/login'.format(server_url)
    login_data = {'userName': url_username, 'password': url_password}
    login_response = session.post(url=login_url, data=login_data, headers=headers)
    # 切换城市
    changzhou_url = '{0}/users/updateAgency'.format(server_url)
    changzhou_data = {'cityId': cityId, 'agencyId': agencyId}
    chanzhou_response = session.post(url=changzhou_url, data=changzhou_data, headers=headers)
    # 新增红包
    redgift_url = '{0}/json/management/promotional/coupon/redgift/add'.format(server_url)
    """
    ownLimit:用户拥有限制数量
    vipRank:vip无限制
    lifeTime:使用周期不限制
    """
    redgift_data = {'name': name, 'type': '普通红包', 'value': redGift_value, 'grantStart': grantStart,
                    'grantEnd': grantEnd, 'useStart': useStart, 'useEnd': useEnd, 'lifeTime': -1,
                    'quantity': redGift_quantity, 'ownLimit': redGift_ownLimit,
                    'useBaseLine': redGift_useBaseLine,
                    'vipRank': '-1', 'instruction': redGift_instruction}
    redgift_response = session.post(redgift_url, data=redgift_data, headers=headers)
    print(redgift_response.text)

def receiveRedGift(store_main_username,store_main_password,):
    """
    领取红包
    :return:
    """
    #登陆
    newSession=requests.Session()
    login_url='{0}/login'.format(store_url)
    login_reponse=newSession.post(url=login_url,data={'uid':store_main_username,'pwd':store_main_password,'auto':'true',
                                                        'plugin[sw]': 1920,'plugin[sh]': 1080,'plugin[iw]': 1916,'plugin[ih]': 264,
                                                        'plugin[ua]': headers},headers=headers)
    print(login_reponse.text)
    #领取
    giftUnUsed_url='{0}/api/user/assets/canUseCash'.format(store_url)
    giftUnUsed_response=newSession.post(url=giftUnUsed_url,data={"type":"money","offset":0,"limit":12})
    giftUnUsed_str=changeIntoStr(giftUnUsed_response.text)
    giftUnUsed_json=json.loads(giftUnUsed_str)
    for eveId in giftUnUsed_json['data']:
        id_=eveId['id']
        receive_url='{0}/api/home/first/redGift'.format(store_url)
        receive_response=newSession.post(url=receive_url,data={"redGiftId":id_})
        print(receive_response.text)

def newCoupon(cityId,agencyId,server_url,url_username,url_password,coupon_value,coupon_quantity,coupon_useBaseLine,coupon_instruction):
    """
    创建优惠码
    :return:
    """
    session = requests.Session()
    couponName=createName()
    grantStart,grantEnd,useStart,useEnd=createCouponTime()
    #登陆后台
    login_url='{0}/users/login'.format(server_url)
    login_data={'userName':url_username,'password':url_password}
    login_response=session.post(url=login_url,data=login_data,headers=headers)
    #选择城市
    changzhou_url='{0}/users/updateAgency'.format(server_url)
    changzhou_data={'cityId':cityId,'agencyId':agencyId}
    chanzhou_response=session.post(url=changzhou_url,data=changzhou_data,headers=headers)
    #创建单
    youhuiquan_url='{0}/json/management/coupon/addCoupon'.format(server_url)
    """
    type：2, 优惠码
    grantType:-1 无兑换条件
    lifeTime:-1 无领取时间限制
    """
    youhuiquan_data={'couponName':couponName,'type':2,'grantType':'-1','value':coupon_value,'grantStart':grantStart,
                     'grantEnd':grantEnd,'useStart':useStart,'useEnd':useEnd,
                     'lifeTime':'-1','quantity':coupon_quantity,'useBaseLine':coupon_useBaseLine,'instruction':coupon_instruction}
    youhuiquan_response=session.post(youhuiquan_url,data=youhuiquan_data,headers=headers)
    youhuiquan_strdata = changeIntoStr(youhuiquan_response.text)
    youhuiquan_json=json.loads(youhuiquan_strdata)
    #点击导出
    daochu_url='{0}/json/management/coupon/queryCoupon?id={1}'.format(server_url,str(youhuiquan_json['gift']['id']))
    daochu_response=session.get(url=daochu_url,headers=headers)
    daochu_data=changeIntoStr(daochu_response.text)
    testdata=json.loads(daochu_data)
    #拼接下载url地址
    test_url = '{7}/json/management/coupon/code/generate?couponCodeBaseSettingId={0}' \
        '&name={1}&useStart={2}&useEnd={3}&quantity={4}&value={5}&useBaseLine={6}'.format(  testdata['data']['id'],
                                                                                            urllib.parse.quote(testdata['data']['couponName'].encode('utf-8')),
                                                                                            testdata['data']['useStartTime'],
                                                                                            testdata['data']['useEndTime'],
                                                                                            testdata['data']['grantCount'],
                                                                                            testdata['data']['value'],
                                                                                            testdata['data']['useBaseLine'],
                                                                                            server_url)
    session.get(url=test_url,headers=headers)
    giftID, couponName =youhuiquan_json['gift']['id'],youhuiquan_data['couponName']
    cur = conn_test.cursor()
    conn_test.select_db(test_mainDb)
    count = cur.execute('select code from coupon_codes WHERE CouponCodeBaseSettingId = {0}'.format(giftID))
    info = cur.fetchmany(count)
    conn_test.commit()
    cur.close()
    print('是否绑定优惠券到店铺(输入数字选择):')
    isUse = input('1.绑定店铺,\n2.不绑定店铺,\n')
    if str(isUse)==str(1):
        store_main_username = input('输入店铺登陆账号:')
        store_main_password = input('输入店铺登陆密码(默认123456,可回车跳过):')
        if store_main_password == '':
            store_main_password = 123456
        for coupon in info:
            bindingCoupon(coupon[0],store_main_username,store_main_password)
    else:
        pass
def bindingCoupon(couponCode,store_main_username,store_main_password):
    """
    绑定优惠券
    :return:
    """
    #登陆
    newSession=requests.Session()
    login_url='{0}/login'.format(store_url)
    login_reponse=newSession.post(url=login_url,data={'uid':store_main_username,'pwd':store_main_password,'auto':'true',
                                                        'plugin[sw]': 1920,'plugin[sh]': 1080,'plugin[iw]': 1916,'plugin[ih]': 264,
                                                        'plugin[ua]': headers},headers=headers)
    print(login_reponse.text)
    #绑定
    banding_url='{0}/api/user/assets/code/new'.format(store_url)
    banding_response=newSession.post(url=banding_url,data={'code':couponCode})
    print(banding_response.text)

def UpdateDadou(storePhoneNum,ddCount):
    """
    更新账号达豆数量
    """
    cur = conn_test.cursor()
    conn_test.select_db(test_mainDb)
    cur.execute("update stores set dadou={0} where storePhoneNum = {1}".format(ddCount, storePhoneNum))
    conn_test.commit()
    cur.execute("select dadou from stores where storePhoneNum = {0}".format(storePhoneNum))
    print(cur.fetchone())
    print('\n该店铺达豆数量已修改\n')
    cur.close()

def clean_redis(storePhoneNum):
    """
    清空缓存购物车信息
    """
    cur = conn_test.cursor()
    conn_test.select_db(test_mainDb)
    cur.execute("select id from stores where storePhoneNum = {0}".format(storePhoneNum))
    _ID=cur.fetchone()
    cur.close()
    rd = redis.Redis(host=redis_db_ip, port=redis_port, db=0)
    try:
        key_ = 'cart:{0}'.format(_ID[0])
        if rd.exists(key_):
            rd.delete(key_)
    except:
        pass

def store_Order(cityId,purchase_phoneNum):
    # 登录
    session=requests.Session()
    login_url = '{0}/login'.format(store_url)
    session.post(url=login_url,data={'uid': purchase_phoneNum, 'pwd': '123456','auto': 'true',
                'plugin[sw]': 1920, 'plugin[sh]': 1080, 'plugin[iw]': 1916,
                'plugin[ih]': 264,'plugin[ua]': headers}, headers=headers)
    default_=True
    new_dict=dict()
    while default_:
        store_choose= input('\n1.输入商品上架名称(精确名称)，\n\n2.输入商品上架编号,\n\n3.退出购物车去下单\n')
        if str(store_choose)==str(1):
            good_name = input('\n输入商品上架名称(精确名称)\n')
            cur = conn_test.cursor()
            conn_test.select_db(test_mainDb)
            cur.execute("select id,title,price,amount,`limit`,GoodId from on_sell_goods WHERE state= 100 and  CityId= '%d' and title ='%s' "%(cityId,good_name.decode('gbk')))
            good_= cur.fetchone()
            cur.close()
            if good_:
                print('上架编号:',str(good_[0]),'\t上架名称:',good_[1],'\t价格:',str(good_[2]),'\t起售数量:',str(good_[3]),'\t库存数量:',str(good_[4]),'\t库存编号:',str(good_[5]))
                good_id=str(good_[0])
                good_amount = input('\n输入商品数量:\n')
                try:
                    for i in range(int(good_amount)):
                        add_good_url = '{0}/api/cart/up'.format(store_url)
                        session.post(url=add_good_url,data={'command': json.dumps([{good_id: 'add'}])})
                    new_dict[good_id]=good_amount
                except Exception as e:
                    print(e)
            else:
                print('\n未查询到商品，重新操作\n')
        elif str(store_choose)==str(2):
            good_id= input('\n输入商品上架编号\n')
            good_amount = input('\n输入商品数量:\n')
            try:
                for i in range(int(good_amount)):
                    add_good_url = '{0}/api/cart/up'.format(store_url)
                    session.post(url=add_good_url,data={'command': json.dumps([{good_id: 'add'}])})
                new_dict[good_id] = good_amount
            except Exception as e:
                print(e)
        elif str(store_choose)==str(3):
            default_=False
        else:
            print('\n未做操作退出')
    try:
        if new_dict:
            order_place_url='{0}/api/order/place'.format(store_url)
            order_place_response=session.post(url=order_place_url,data={'orders':json.dumps(new_dict),'dadou':0, 'redGiftId':'','couponCode':'-1','message':'','payType':'1'},headers=headers)
            order_place_str=changeIntoStr(order_place_response.text)
            print(order_place_response.text)
            order_place_json=json.loads(order_place_str)
            print('\n订单号为:',order_place_json['data']['id'])
    except Exception as e:
        print(e)

def getZXXCode(LoginNum):
    rd = redis.Redis(host=redis_db_ip, port=redis_port, db=6)
    key_ = 'validateCode:user:{0}'.format(LoginNum)
    for i in range(3):
        if rd.exists(key_):
            js = json.loads(rd.get(key_))
            print()
            print('\n验证码:\t',js['code'])
            break
        time.sleep(1)

def checkStoreName(cityId,prehouse):
    """
    查询店铺
    """
    cur = conn_test.cursor()
    conn_test.select_db(test_mainDb)
    info=cur.execute("select id,storePhoneNum,storeName from stores where storeState= '1' and storePwd = 'e10adc3949ba59abbe56e057f20f883e' and CityId={0} order by id desc limit 100".format(cityId))
    storeInfo=cur.fetchmany(info)
    cur.close()

    cTime = 0
    dTime = 0
    if prehouse:
        prehouseId=[]
        cur1 = conn_test.cursor()
        if type(prehouse)==list:
            for pre in prehouse:
                conn_test.select_db(test_mainDb)
                info=cur1.execute("select StoreId from branch_warehouse_stores where CityId={0} and WarehouseId={1}".format(cityId,pre))
                preInfo=cur1.fetchmany(info)
                for pre in preInfo:
                    prehouseId.append(pre[0])
        else:
            conn_test.select_db(test_mainDb)
            info=cur1.execute("select StoreId from branch_warehouse_stores where CityId={0} and WarehouseId={1}".format(cityId,prehouse))
            preInfo=cur1.fetchmany(info)
            for pre in preInfo:
                prehouseId.append(pre[0])
        cur1.close()
        #判断
        prestore=[]
        mainstore=[]
        for store in storeInfo:
            if store[0] in prehouseId:
                prestore.append(store)
            else:
                mainstore.append(store)

        print('****************主仓店铺****************')
        for store in mainstore:
            print('店铺编号:',str(store[0]),'\t店铺登录账号:',str(store[1]),'\t店铺名:',store[2])
            cTime+=1
            if cTime>=4:
                break
        print('***************前置仓店铺***************')
        for store in prestore:
            print('店铺编号:',str(store[0]),'\t店铺登录账号:',str(store[1]),'\t店铺名:',store[2])
            dTime+=1
            if dTime>=4:
                break

    else:
        print('****************主仓店铺****************')
        for store in storeInfo:
            print('店铺编号:',str(store[0]),'\t店铺登录账号:',str(store[1]),'\t店铺名:',store[2])
            cTime+=1
            if cTime>=4:
                break
        print('**************无前置仓店铺***************')

def checkStoreType(cityId,store_name,prehouse):
    """
    查询店铺类型
    """
    cur = conn_test.cursor()
    conn_test.select_db(test_mainDb)
    cur.execute("select id from stores where CityId={0} and storePhoneNum={1} order by id desc limit 1".format(cityId,store_name))
    storeId=cur.fetchone()
    cur.close()
    if storeId:
        if prehouse:
            prehouseId = []
            cur1 = conn_test.cursor()
            if type(prehouse) == list:
                for pre in prehouse:
                    conn_test.select_db(test_mainDb)
                    info = cur1.execute(
                        "select StoreId from branch_warehouse_stores where CityId={0} and WarehouseId={1}".format(
                            cityId, pre))
                    preInfo = cur1.fetchmany(info)
                    for pre in preInfo:
                        prehouseId.append(pre[0])
            else:
                conn_test.select_db(test_mainDb)
                info = cur1.execute(
                    "select StoreId from branch_warehouse_stores where CityId={0} and WarehouseId={1}".format(cityId,
                                                                                                              prehouse))
                preInfo = cur1.fetchmany(info)
                for pre in preInfo:
                    prehouseId.append(pre[0])
            cur1.close()
            if storeId[0] in prehouseId:
                print()
                print('该店铺为前置仓店铺')
            else:
                print()
                print('该店铺为主仓店铺')
        else:
            print()
            print('该城市不存在前置仓店铺')
    else:
        print()
        print('不存在店铺账号')

def checkRuKuName(mainhouse):
    """查询入库验收员"""
    cur = conn_test.cursor()
    conn_test.select_db(test_ckDb)
    cur.execute("select workId from receivers where WarehouseId={0} limit 1".format(mainhouse))
    storeId=cur.fetchone()
    cur.close()
    if storeId:
        print('入库验收账号:')
        print('\t',storeId[0])
    else:
        print('无入库验收账号')

def checkGoodsExist(goodID):
    """
    检查是否存在商品
    """
    cur = conn_test.cursor()
    conn_test.select_db(test_mainDb)
    cur.execute("select id from goods where id = {0}".format(goodID))
    info = cur.fetchone()
    if not info:
        print('\n不存在该商品库存编号\n')
    cur.close()
    return info

def create_san_product(name,img_jpg):
    # 登录全局系统
    session=requests.Session()
    login = session.post(url=global_url+'/users/login',data={'userName':12345678910,'password':123456},headers = headers)
    # 添加商品
    data ={'brandId': '2436','country': '中国','name': name.decode('gbk'),'catalog': ['0', '4090100', '2'],'packType': '0','barCode': '123456','catalogId': '4090100',
    'specification': '12瓶/箱','unit': '1','tax': '17','length': '1','width': '1','height': '1','volume': '1.00','weight': '1','termOfValidity': '180','timeUnit': '2','transProportion': '1',
    'introduction': '<p>test</p>',}
    #添加商品
    session.post(url=global_url + '/goods/add', data=data, headers=headers)
    try:
        conn=pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
        cur = conn.cursor()
        conn.select_db(test_mainDb)
        cur.execute("select id from goods where `name` = '%s' order by id desc"%data['name'])
        info = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        info=None
    if info:
        good_id=info[0]
        # 提交新品图片处理
        session.post(url=global_url + '/goods/submitImg', data={'id': good_id},headers=headers)
        # 上传图片
        img_data = {'id': good_id,'imagePaths': -1,'images': '0'}
        try:
            session.post(global_url + '/goods/addFile', data=img_data, files=img_jpg,headers=headers)
        except BaseException as e:
            print(('Error:%s'%e))
        else:
            print(('商品(散)名称:%s\t库存编号:%d\n' % (name.decode('gbk'), good_id)))
        return good_id
    else:
        return

def create_zheng_product(name,full_id,img_jpg):
    # 登录全局系统
    session=requests.Session()
    login = session.post(url=global_url+'/users/login',data={'userName':12345678910,'password':123456},headers = headers)
    #查找散装商品信息
    find = session.post(url=global_url + '/api/goods/findRelatedGoods', data={'id':full_id},headers=headers)
    find = find.json()
    data = {'brandId': '2436','country': '中国','name':'(整)_'+name.decode('gbk'),"catalog": ['1090200', '2'],"catalogId": '1090200','barCode':'123456',"specification": '12瓶/箱',
     'unit':'1','tax':'17','length':'1','height':'1','width':'1','volume':'1.00','weight':'1',"packType":"1",
     'termOfValidity':'180','timeUnit':'2',"transProportion": 5,"sid":find['data']['id'],"sGoodName":find['data']['name'],"goodId":find['data']['id'],
     "sSpecification":find['data']['specification'],"sCustomCode":find['data']['customCode'],"sUnit":1,'introduction': '<p>test</p>',}
    #添加商品
    session.post(url=global_url + '/goods/add', data=data, headers=headers)
    try:
        conn=pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
        cur = conn.cursor()
        conn.select_db(test_mainDb)
        cur.execute("select id from goods where `name` = '%s' order by id desc"%data['name'])
        info = cur.fetchone()
        cur.close()
        conn.close()
    except Exception as e:
        info=None
    if info:
        good_id=info[0]
        # 提交新品图片处理
        session.post(url=global_url + '/goods/submitImg', data={'id': good_id},headers=headers)
        # 上传图片
        img_data = {'id': good_id,'imagePaths': -1,'images': '0'}
        try:
            session.post(global_url + '/goods/addFile', data=img_data, files=img_jpg,headers=headers)
        except BaseException as e:
            print(('Error:%s'%e))
        else:
            print(('商品(整)名称:%s\t库存编号:%d\n' % (name.decode('gbk'), good_id)))
        return good_id
    else:
        return


def img_content():
    try:
        img = requests.get('https://ss0.bdstatic.com/-0U0bnSm1A5BphGlnYG/tam-ogel/b80a043c57da31ca37f99c22b53511e3_121_121.jpg',headers=headers, verify=False)
        img_jpg = {'image0': ('demo.jpg', img.content, 'image/jpeg')}
        return img_jpg
    except Exception as e:
        return

def SureOrder(cityId,agencyId,service_url,service_username,service_password):
    start=time.strftime('%Y-%m-%d', time.localtime(time.time()))
    end=time.strftime('%Y-%m-%d', time.localtime(time.time() + 24 * 60 * 60))
    #登陆客服
    newSession = requests.Session()
    service_login='{0}/service/api/manager/login'.format(service_url)
    service_response=newSession.post(url=service_login,data={'account':service_username,'password':service_password})
    #切换城市
    service_changecity_url='{0}/service/api/manager/updateAgency'.format(service_url)
    service_changecity_response=newSession.post(url=service_changecity_url,data={'cityId':cityId,'agencyId':agencyId})
    #查看当前订单
    check_url='{0}/service/api/order/list?offset=0&limit=1000&payType=1&order=store&start={1}%2000:00:00&end={2}%2000:00:00&message=0&timeTag=0'.format(service_url,start,end)
    check_url_response=newSession.get(url=check_url)
    check_json=json.loads(changeIntoStr(check_url_response.text))
    try:
        for cj in check_json['stores'][0]['orders']:
            if cj['state']==0:
                #确认订单
                order_url='{0}/service/api/order/send'.format(service_url)
                newSession.post(url=order_url,data={'orderId':int(cj['id'])})
                print('\n订单号:%s\t 审核通过\n'%cj['id'])
    except Exception as e:
        pass
def CancleOrder(cityId,agencyId,service_url,service_username,service_password,orderId):
    #登陆客服
    newSession = requests.Session()
    service_login='{0}/service/api/manager/login'.format(service_url)
    newSession.post(url=service_login,data={'account':service_username,'password':service_password})
    #切换城市
    service_changecity_url='{0}/service/api/manager/updateAgency'.format(service_url)
    newSession.post(url=service_changecity_url,data={'cityId':cityId,'agencyId':agencyId})
    #取消订单
    cancle_url='{0}/service/api/order/cancel'.format(service_url)
    cancle_response=newSession.post(url=cancle_url,data={'id':orderId,'info':'客户下错单'})
    cancle_json=json.loads(changeIntoStr(cancle_response.text))
    if cancle_json['tag']=='error':
        print('未找到对应货品订单')
    else:
        print('\n订单号:%s\t 取消订单成功\n' % str(orderId))

def ThOrder(cityId,agencyId,service_url,service_username,service_password,orderId,invent_url,invent_username,mainhouse):
    #登陆客服
    if str(cityId)=='320100':
        worker = {'name': '00', 'id': 34, 'workId': '8886', 'phone': 15575000995}
    elif str(cityId)=='320200':
        worker = {'name': '11', 'id': 42, 'workId': 'ps001', 'phone': 15575000999}
    else:
        worker = {'name': '李白', 'id': 14, 'workId': 'ps001', 'phone': 17621145336}
    newSession = requests.Session()
    service_login='{0}/service/api/manager/login'.format(service_url)
    newSession.post(url=service_login,data={'account':service_username,'password':service_password})
    #切换城市
    service_changecity_url='{0}/service/api/manager/updateAgency'.format(service_url)
    newSession.post(url=service_changecity_url,data={'cityId':cityId,'agencyId':agencyId})
    #点单明细
    conn_test_1 = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
    cur_1 = conn_test_1.cursor()
    conn_test_1.select_db(test_mainDb)
    cur_1.execute("select id FROM store_order_branches where StoreGoodsOrderId='{0}' and CityId='{1}'".format(orderId,cityId))
    data = cur_1.fetchone()
    cur_1.close()
    conn_test_1.close()
    if data:
        detail_url='{0}/service/api/backGoods/branchOrder/detail'.format(service_url)
        detail_res=newSession.post(url=detail_url,data={'orderId':orderId,'branchOrderId':data[0]})
        detail_json=json.loads(changeIntoStr(detail_res.text))
        new_detail=[]
        for de in detail_json['result']:
            new_detail.append(de)
        back_url = '{0}/service/api/backGoods/add'.format(service_url)
        if len(new_detail)==1:
            print('\n商品可退总数为:',str(int(new_detail[0]['amount'])-int(new_detail[0]['returnAmount'])))
            T_amount=input('\n输入退货数量(小于等于可退数量)\n')
            back_res=newSession.post(url=back_url,data={'detailId':new_detail[0]['detailId'],'branchOrderId':data[0],'goodId':new_detail[0]['GoodId'],
                                                        'backGoodId':new_detail[0]['GoodId'],'orderId':orderId,'produceDates[]':time.strftime('%Y-%m-%d',time.localtime(time.time())),
                                                        'amounts[]':int(T_amount),'onSellGoodsCombId':new_detail[0]['OnSellGoodsCombId'],'message':'','onSellGoodId':new_detail[0]['OnSellGoodId'],
                                                        'orderComboType':0,'backPackType':1,'backComboType':2})
            print('退货成功')
        else:
            for nd in new_detail:
                print('上架名称:',nd['sellName'],'\t库存名称:',nd['name'],'\t库存编号:',nd['OnSellGoodId'],'\t可退数量:',str(int(nd['amount'])-int(nd['returnAmount'])))
            T_order = input('\n输入要退的库存编号:\n')
            T_amount= input('\n输入退货数量(小于等于可退数量)\n')
            for nd in new_detail:
                if str(nd['OnSellGoodId'])==T_order:
                    back_res = newSession.post(url=back_url,
                                               data={'detailId': nd['detailId'], 'branchOrderId': data[0],
                                                     'goodId': nd['GoodId'],
                                                     'backGoodId': nd['GoodId'], 'orderId': orderId,
                                                     'produceDates[]': time.strftime('%Y-%m-%d',
                                                                                     time.localtime(time.time())),
                                                     'amounts[]': int(T_amount),
                                                     'onSellGoodsCombId': nd['OnSellGoodsCombId'], 'message': '',
                                                     'onSellGoodId': nd['OnSellGoodId'],
                                                     'orderComboType': 0, 'backPackType': 1, 'backComboType': 2})
                    print('退货成功')
                    break
        try:
            back_json=json.loads(changeIntoStr(back_res.text))
            if back_json['tag']=='success':
                ZP_order = input('\n是否要继续指派配送员取货:\n\n1.指派取货\t2.不指派取货\n')
                if str(ZP_order)==str(1):
                    print('\n默认指派主仓配送员:',worker['name'],'\t手机号为:',str(worker['phone']))
                    NewSession = requests.Session()
                    login_url = '{0}/users/login'.format(invent_url)
                    login_data = {'userName': invent_username, 'password': service_password}
                    NewSession.post(url=login_url, data=login_data)
                    zdh_url = '{0}/users/updateAgency'.format(invent_url)
                    zdh_data = {'cityId': cityId, 'agencyId': agencyId}
                    NewSession.post(url=zdh_url, data=zdh_data)
                    conn_test_A = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306,charset="utf8")
                    cur_A = conn_test_A.cursor()
                    conn_test_A.select_db(test_ckDb)
                    cur_A.execute("select id,rgl_number_id,rgl_store_goods_order_id,createdAt FROM return_goods_list where rgl_state='0' and rgl_warehouse_id='{0}'and rgl_store_goods_order_id='{1}' order by id desc".format(mainhouse, orderId))
                    zp = cur_A.fetchone()
                    cur_A.close()
                    conn_test_A.close()
                    if zp:
                        print('\n退货单号:', str(zp[1]), '\t订单编号:', str(zp[2]), '\t创建时间:', zp[3])
                        TH_url = '{0}/api/returnGoods/updateCourier'.format(invent_url)
                        TH_res = NewSession.post(url=TH_url, data={'id': zp[0], 'courierId': worker['id']})
                        TH_json = json.loads(changeIntoStr(TH_res.text))
                        if TH_json['tag'] == 'success':
                            print('\n指派配送员OK')
                else:
                    pass
        except Exception as e:
            pass


    else:
        print('未找到该订单')

def mainstorerun(cityId,agencyId,server_url,url_username,url_password,orderId):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}
    login_url = '{0}/users/login'.format(server_url)
    login_data = {'userName': url_username, 'password': url_password}
    session.post(url=login_url, data=login_data, headers=headers)
    # 切换城市
    zdh_url = '{0}/users/updateAgency'.format(server_url)
    zdh_data = {'cityId': cityId, 'agencyId': agencyId}
    session.post(url=zdh_url, data=zdh_data, headers=headers)
    # 增加供应商
    numID=0
    for i in range(5):
        boci_url = '{0}/api/expressRoute/create/surplus'.format(server_url)
        session.post(url=boci_url, data={"orderTime": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 5 * 60))})
        conn_test1 = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
        cur = conn_test1.cursor()
        conn_test1.select_db(test_ckDb)
        cur.execute("select ExpressRouteId  from express_route_details where StoreGoodsOrderId='{0}'".format(orderId))
        data = cur.fetchone()
        cur.close()
        conn_test1.close()
        if data:
            numID=data[0]
            break
        else:
            time.sleep(2)
    if numID:
        sureoder_url = '{0}/api/pickGoods/pickList/create?id={1}'.format(server_url, numID)
        JH = session.get(url=sureoder_url, headers=headers)
        print(JH.text)
        time.sleep(10)
        conn_test2 = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
        cur = conn_test2.cursor()
        conn_test2.select_db(test_ckDb)
        info = cur.execute(
            "select a.PickListId, a.id,a.orderQuantity,a.actualQuantity,b.numberId  from pick_list_details as a,pick_lists as b where a.PickListId=b.id and b.ExpressRouteId={0}".format(
                numID))
        data_all = cur.fetchmany(info)
        cur.close()
        conn_test2.close()
        if data_all:
            token_url = '{0}/api/getToken?numberId={1}&key=JHQR'.format(server_url, data_all[0][4])
            token_data = session.get(url=token_url, headers=headers)
            token_json = json.loads(token_data.text)
            token = token_json['token']

            jianhuo_url = '{0}/api/pickGoods/pickList/confirm'.format(server_url)
            dict_can = {}
            for j in range(len(data_all)):
                dict_can['details[%d][pickListId]' % j] = data_all[j][0]
                dict_can['details[%d][detailId]' % j] = data_all[j][1]
                dict_can['details[%d][orderQuantity]' % j] = data_all[j][2]
                dict_can['details[%d][actualQuantity]' % j] = data_all[j][2]

            dict_can['pickGoodsName'] = 'pickman'
            dict_can['token'] = token
            session.post(url=jianhuo_url, data=dict_can, headers=headers)
            time.sleep(10)
            if str(cityId) == str(320100):
                print('配送员:', 'ps001', '\t配送员手机号:  15575000999\n')
                ps = 'ps001'
                courierId = 42
                name='11'
            elif str(cityId) == str(320200):
                print('配送员:', 'ps001', '\t配送员手机号:  15575000995\n')
                ps = 'ps001'
                courierId = 34
                name='00'
            else:
                print('配送员:', 'ps001', '\t配送员手机号:  17621145336\n')
                courierId = 14
                ps = 'ps001'
                name='李白'

            reviewOrder_url='http://192.168.1.251:48000/api/stockOut/scan/reviewOrder?orderId={0}&courierId={1}&virtualCourierId={2}&courierName={3}'.format(orderId,courierId,ps,urllib.parse.quote(name.encode('utf-8')))
            session.get(url=reviewOrder_url)
            confirm_Url='http://192.168.1.251:48000/api/stockOut/delivery/reviewConfirm'
            confirm_res=session.post(url=confirm_Url,data={'orderId':orderId,'courierId':courierId})
            time.sleep(5)
            confirm_json=json.loads(changeIntoStr(confirm_res.text))
            if confirm_json['tag']=='success':
                print('\n出库成功')
        else:
            pass

def prestorerun(cityId,agencyId,server_url,url_username,url_password,orderId):
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}
    login_url = '{0}/users/login'.format(server_url)
    login_data = {'userName': url_username, 'password': url_password}
    session.post(url=login_url, data=login_data, headers=headers)
    # 切换城市
    zdh_url = '{0}/users/updateAgency'.format(server_url)
    zdh_data = {'cityId': cityId, 'agencyId': agencyId}
    session.post(url=zdh_url, data=zdh_data, headers=headers)
    # 增加供应商
    numID=0
    for i in range(5):
        boci_url = '{0}/api/expressRoute/create/surplus'.format(server_url)
        session.post(url=boci_url, data={"orderTime": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 5 * 60))})
        conn_test1 = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
        cur = conn_test1.cursor()
        conn_test1.select_db(test_ckDb)
        cur.execute("select ExpressRouteId  from express_route_details where StoreGoodsOrderId='{0}'".format(orderId))
        data = cur.fetchone()
        cur.close()
        conn_test1.close()
        if data:
            numID=data[0]
            break
        else:
            time.sleep(2)
    if numID:
        sureoder_url = '{0}/api/pickGoods/pickList/create?id={1}'.format(server_url, numID)
        JH=session.get(url=sureoder_url,headers=headers)
        print(JH.text)
        time.sleep(10)
        conn_test2 = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
        cur = conn_test2.cursor()
        conn_test2.select_db(test_ckDb)
        info=cur.execute("select a.PickListId, a.id,a.orderQuantity,a.actualQuantity,b.numberId  from pick_list_details as a,pick_lists as b where a.PickListId=b.id and b.ExpressRouteId={0}".format(numID))
        data_all=cur.fetchmany(info)
        cur.close()
        conn_test2.close()
        if data_all:
            token_url='{0}/api/getToken?numberId={1}&key=JHQR'.format(server_url,data_all[0][4])
            token_data=session.get(url=token_url,headers=headers)
            token_json=json.loads(token_data.text)
            token=token_json['token']

            jianhuo_url='{0}/api/pickGoods/pickList/confirm'.format(server_url)
            dict_can={}
            for j in range(len(data_all)):
                dict_can['details[%d][pickListId]'%j]=data_all[j][0]
                dict_can['details[%d][detailId]'%j]=data_all[j][1]
                dict_can['details[%d][orderQuantity]'%j]=data_all[j][2]
                dict_can['details[%d][actualQuantity]'%j]=data_all[j][2]

            dict_can['pickGoodsName']='pickman'
            dict_can['token']=token
            session.post(url=jianhuo_url,data=dict_can,headers=headers)
            time.sleep(5)
            if str(cityId)==str(320100):
                print('司机:','7777','\t司机手机号:  13900000000\n')
                ps='7777'
                courierId =8
                name='梅梅'
            elif str(cityId)==str(320200):
                print('司机:','sj001 ','\t司机手机号:  15000779522\n')
                ps = 'sj001'
                courierId =36
                name='ssss'
            else:
                print('司机:','sj002','\t司机手机号:  13200001111\n')
                courierId = 47
                ps = 'sj002'
                name='郭靖'
            reviewOrder_url='http://192.168.1.251:48000/api/stockOut/scan/reviewOrder?orderId={0}&courierId={1}&virtualCourierId={2}&courierName={3}'.format(orderId,courierId,ps,urllib.parse.quote(name.encode('utf-8')))
            session.get(url=reviewOrder_url)
            confirm_Url='http://192.168.1.251:48000/api/stockOut/delivery/reviewConfirm'
            confirm_res=session.post(url=confirm_Url,data={'orderId':orderId,'courierId':courierId})
            json.loads(changeIntoStr(confirm_res.text))
            sj_url='{0}/api/truckLoadList/courier/unload/list'.format(server_url)
            sj_response=session.post(url=sj_url,data={'CourierId':courierId})
            sj_json=json.loads(changeIntoStr(sj_response.text))

            ZC_id=0
            for sj_n in sj_json['data']:
                if sj_n['numberId'].split('-')[-1]==str(orderId):
                    ZC_id=sj_n['id']
            if ZC_id:
                ZC_url='{0}/api/truckLoadList/create'.format(server_url)
                session.post(url=ZC_url,data={'courierId':courierId,'orders[]':ZC_id})
                print(str(orderId), '\t前置仓订单波次已装车')

def checkUsedGood(cityID,providerID):
    print('\n可用商品库存编号以及价格如下\n')
    cur = conn_test.cursor()
    conn_test.select_db(test_mainDb)
    info=cur.execute("select cbp_good_id,cbp_price from cg_base_prices WHERE cbp_city_id='{0}' and cbp_state='1' and cbp_provider_id='{1}' order by id desc".format(cityID,providerID))
    datas = cur.fetchmany(info)
    sum_=0
    if datas:
        for data in datas:
            if data[0] and data[1]:
                print('库存编号为:',str(data[0]),'\t价格为:',str(data[1]))
            sum_+=1
            if sum_>=5:
                break
    cur.close()

def Ruku(cityId,agencyId,worker,orderId,invent_url,url_username,url_password):
    # 登录
    newsession=requests.Session()
    login_url = '{0}/users/login'.format(invent_url)
    login_data = {'userName': url_username, 'password': url_password}
    newsession.post(url=login_url, data=login_data)
    zdh_url = '{0}/users/updateAgency'.format(invent_url)
    zdh_data = {'cityId':cityId,'agencyId':agencyId}
    newsession.post(url=zdh_url, data=zdh_data)
    #入库
    conn_test11 = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
    cur11 = conn_test11.cursor()
    conn_test11.select_db(test_ckDb)
    cur11.execute("select identificationCode,id from check_up_orders WHERE numberId='{0}' order by id desc limit 1".format(orderId))
    info1 = cur11.fetchone()
    if info1:
        identificationCode=info1[0]
    else:
        identificationCode=''
    cur11.close()
    conn_test11.close()
    time.sleep(2)
    conn_test111 = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
    cur111 = conn_test111.cursor()
    conn_test111.select_db(test_ckDb)
    cur111.execute("select id,shouldReceive,GoodId,height,layerNumber from check_up_order_details WHERE identificationCode='{0}' and state='0' limit 1".format(identificationCode))
    info = cur111.fetchone()
    if info:
        _id=info[0]
        shouldReceive=info[1]
        GoodId=info[2]
        height=info[3]
        layerNumber=info[4]
    cur111.close()
    conn_test111.close()
    if info:
        scan_url='{0}/api/storageIn/scanReceipt/query?orderId={1}'.format(invent_url,orderId)
        newsession.get(url=scan_url)
        ruku_url='{0}/api/storageIn/checkup/add'.format(invent_url)
        ruku_data={"receiver":worker,
                   "identificationCode":identificationCode,
                   "checkUp":[{"id":_id,"count":shouldReceive,"shouldCount":shouldReceive,"tabelNumber":"1","type":"bulk","goodId":GoodId,"checkupType":"true",
                               "countByDate":[{"count":shouldReceive,"produceDate":time.strftime('%Y-%m-%d',time.localtime(time.time()))}],
                               "stockWay":"100*100","layerNumber":layerNumber,"height":height,"proportion":1}],
                   "remark":""
                   }
        newsession.post(url=ruku_url,data=json.dumps(ruku_data),headers={'Content-Type': 'application/json'})
        tokenRuku_url='{0}/api/getToken?numberId={1}&key=YS'.format(invent_url,orderId)
        tokenRuku_response=newsession.get(url=tokenRuku_url)
        tokenRuku_json=json.loads(tokenRuku_response.text)
        token=tokenRuku_json['token']
        #审核入库
        sureRuku_url='{0}/api/storageIn/checkup/confirm'.format(invent_url)
        sureRuku_data={'orderId':orderId,'identificationCode':identificationCode,'token':token}
        sureRuku_response=newsession.post(url=sureRuku_url,data=sureRuku_data)
        sureRuku_json=json.loads(changeIntoStr(sureRuku_response.text))
        print()
        print(sureRuku_json['message'])
    else:
        print('\n入库失败，再次入库')

def CaiGou(cityId,agencyId,server_url,warehouseId,url_username,url_password,goodId,quantity,cbp_provider_id):
    # 登录
    if str(cityId)==str(320100):
        contact={'selectContract_id':43,'copartnerId':7}
    elif str(cityId)==str(320200):
        contact = {'selectContract_id':134, 'copartnerId':10}
    else:
        contact = {'selectContract_id':135, 'copartnerId':41}
    session=requests.Session()
    headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.75 Safari/537.36'}
    login_url = '{0}/users/login'.format(server_url)
    login_data = {'userName': url_username, 'password': url_password}
    login_response = session.post(url=login_url, data=login_data, headers=headers)
    # 切换城市
    zdh_url = '{0}/users/updateAgency'.format(server_url)
    zdh_data = {'cityId':cityId,'agencyId':agencyId}
    session.post(url=zdh_url, data=zdh_data, headers=headers)
    # 新增申购单
    cur = conn_test.cursor()
    conn_test.select_db(test_mainDb)
    cur.execute("select cbp_price from cg_base_prices WHERE cbp_city_id='{0}' and cbp_good_id='{1}'and cbp_state='1' and cbp_provider_id='{2}'".format(cityId,goodId,cbp_provider_id))
    info1 = cur.fetchone()
    if info1:
        price=info1[0]
    cur.close()
    if info1:
        addOrder_url='{0}/json/stockin/add'.format(server_url)

        addOrder_data={'selectContract': contact['selectContract_id'], 'taxRate': '17', 'taxSum-show': float(int(quantity)*price), 'taxSum': int(int(quantity)*price), 'warehouseId': warehouseId,
                       'purchaseOrigin': '1', 'selectType': '1', 'suggestNum': '0', 'copartnerId': contact['copartnerId'], 'dailySold': '0', 'goodId': goodId,
                       'stockInType': 'normal', 'unitPrice': price, 'quantity': quantity}
        session.post(url=addOrder_url,data=addOrder_data,headers=headers)
        time.sleep(2)
        conn_test_N = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
        cur_N = conn_test_N.cursor()
        conn_test_N.select_db(test_mainDb)
        cur_N.execute("select id from stock_in_orders WHERE state='0' and ProviderId='{0}'and sumWithTax='{1}' order by id desc limit 1 ".format(cbp_provider_id,int(int(quantity)*price)))
        info = cur_N.fetchone()
        # print info
        if info:
            orderId=info[0]
            print('\n采购单号为',str(orderId))
        cur_N.close()
        conn_test_N.close()
        if info:
            orderCommit_url='{0}/json/stockin/commit'.format(server_url)
            session.post(url=orderCommit_url,data={'id':orderId})
            shenHe_url='{0}/json/stockin/ag'.format(server_url)
            session.post(url=shenHe_url,data={'id':orderId,'message':''})
            sureOrder_url='{0}/json/stockin/purchase'.format(server_url)
            session.post(url=sureOrder_url,data={'id':orderId,'warehouseTime':time.strftime('%Y-%m-%d %H:%M',time.localtime(time.time()))})
            print('\n采购成功')
        else:
            print('\n重新采购')
    else:
        print('\n商品未报价')

def ZZX(server_url,phone,task_type):
    session = requests.Session()
    rd = redis.Redis(host=redis_db_ip, port=redis_port, db=6)
    key_ = 'validateCode:user:{0}'.format(phone)
    if rd.exists(key_):
        js = json.loads(rd.get(key_))
        print('\n手机登录验证码:\t',js['code'])
        print()
    else:
        code_url='{0}/v1/user/sendCode'.format(server_url)
        session.post(url=code_url,data={"phone":phone})
        time.sleep(3)
        js = json.loads(rd.get(key_))
        print('\n手机登录验证码:\t', js['code'])
        print()
    code=js['code']
    zxx_login='{0}/v1/user/login'.format(server_url)
    zxx_res=session.post(url=zxx_login,data={"phone":phone,"validateCode":code})
    zxx_json=json.loads(zxx_res.text)
    zxx_token=zxx_json['data']['token']
    list_url='{0}/v2/order/delivery/listOrders?flag=0&lat=0.0&lon=0.0&state=2'.format(server_url)
    list_res=session.get(url=list_url,headers={'Authorization':zxx_token})
    list_json=json.loads(changeIntoStr(list_res.text))
    for orderId in list_json['data']:
        print('运单编号:',orderId['invoiceNumberId'],'\t订单号:',str(orderId['mainOrderId']))
    if task_type==str(1):
        #送达
        send_type = input('\n1.所有订单全部送达\t2.一个订单送达\t3.退出\n')
        sendComplete_url='{0}/v1/order/delivery/sendComplete'.format(server_url)
        if str(send_type)==str(1):
            for sd in list_json['data']:
                session.post(url=sendComplete_url,data={"numberId":sd['numberId'],"receiptCode":"8","receiveType":"cash"},headers={'Authorization':zxx_token})
                print('运单编号:',sd['invoiceNumberId'],'已送达')
                time.sleep(5)
        elif str(send_type)==str(2):
            send_orderId=input('\n输入要送达的订单号:\n')
            for sd in list_json['data']:
                if str(sd['mainOrderId'])==send_orderId:
                    session.post(url=sendComplete_url,data={"numberId": sd['numberId'], "receiptCode": "8","receiveType": "cash"}, headers={'Authorization': zxx_token})
                    print('运单编号:', sd['invoiceNumberId'], '已送达')
                    break
        else:
            pass

    elif task_type==str(2):
        #拒收
        refuse_orderId = input('\n输入拒收的订单号:\n')
        refuse_url='{0}/v2/order/delivery/refuse'.format(server_url)
        for sd in list_json['data']:
            if str(sd['mainOrderId']) == refuse_orderId:
                session.post(url=refuse_url,data={"numberId":sd['numberId'],"reason":"商品保质期不符合店家要求","receiptCode":"8"},headers={'Authorization':zxx_token})
                print('\n运单编号:', sd['invoiceNumberId'], '已拒收')

    elif task_type==str(3):
        #部分送达
        rejectPreview_orderId = input('\n输入部分送达的订单号:\n')
        for sd in list_json['data']:
            if str(sd['mainOrderId']) == rejectPreview_orderId:
                goodDetail_url='{0}/v2/order/delivery/goodDetail'.format(server_url)
                goodDetail_res=session.post(url=goodDetail_url,data={"deliveryOrderId":sd['id']},headers={'Authorization':zxx_token})
                goodDetail_json=json.loads(changeIntoStr(goodDetail_res.text))
                deliveryOrderId=goodDetail_json['data']['deliveryOrderId']
                for detail in goodDetail_json['data']['details']:
                    print('\n编号ID:',str(detail['id']),'\t商品上架名:',detail['name'],'\t数量为:',str(detail['quantity']))
                if len(goodDetail_json['data']['details'])==1:
                    refusePre_amount=input('\n输入商品拒收数量:\n')
                    detail_ID=goodDetail_json['data']['details'][0]['id']
                else:
                    detail_ID = input('\n输入拒收商品编号ID:\n')
                    refusePre_amount = input('\n输入商品拒收数量:\n')
                rejectPreview_url='{0}/v2/order/delivery/rejectPreview'.format(server_url)
                session.post(url=rejectPreview_url,data=json.dumps({"deliveryOrderId":deliveryOrderId,"details":json.dumps({str(detail_ID):int(refusePre_amount)})}),headers={'Authorization':zxx_token,"Content-Type":"application/json; charset=UTF-8"})
                partArrive_url='{0}/v2/order/delivery/partArrive'.format(server_url)
                partArrive_res=session.post(url=partArrive_url,data=json.dumps({"deliveryOrderId":deliveryOrderId,"details":json.dumps({str(detail_ID):int(refusePre_amount)}),"reason":"商品保质期不符合店家要求","receiptCode":"8","receiveType":"cash"}),headers={'Authorization':zxx_token,"Content-Type":"application/json; charset=UTF-8"})
                print(partArrive_res.text)
    elif task_type==str(4):
        #退货取货
        Tlist_url='{0}/v2/order/delivery/listOrders?flag=1&lat=0.0&lon=0.0&state=1'.format(server_url)
        Tlist_res=session.get(url=Tlist_url,headers={'Authorization':zxx_token})
        Tlist_json=json.loads(changeIntoStr(Tlist_res.text))
        for Tlist in Tlist_json['data']:
            Tdetail_url='{0}/v2/order/backGoods/listDetail?backOrderId={1}'.format(server_url,Tlist['backOrderId'])
            Tdetail_res=session.get(url=Tdetail_url,headers={'Authorization':zxx_token})
            Tdetail_json=json.loads(changeIntoStr(Tdetail_res.text))
            for m in range(len(Tdetail_json['data']['details'])):
                Td=Tdetail_json['data']['details'].pop()
                goodId=Td['goodId']
                _id=Td['id']
                Amount=Td['orgAmount']
                backGood_url='{0}/v2/order/backGoods/backGoods'.format(server_url)
                backGood_res=session.post(url=backGood_url,data=json.dumps({"detail":[{"goodId":goodId,"id":_id,"quantity":Amount,"realSum":0}],"backOrderId":Tlist['backOrderId']}),headers={'Authorization':zxx_token,"Content-Type":"application/json; charset=UTF-8"})
                backGood_json=json.loads(changeIntoStr(backGood_res.text))
                if backGood_json['tag']=='success':
                    print('\n退货取货完成:',str(_id),'\t取货数量:',str(Amount))
                    time.sleep(5)
                else:
                    time.sleep(5.5)
    else:
        print('\n请输入正确猪行侠业务类型')

def TH_RU(cityId,agencyId,invent_url,url_username,url_password,warehouseId,orderId):
    # 登录
    NewSession=requests.Session()
    login_url = '{0}/users/login'.format(invent_url)
    login_data = {'userName': url_username, 'password': url_password}
    NewSession.post(url=login_url, data=login_data)
    zdh_url = '{0}/users/updateAgency'.format(invent_url)
    zdh_data = {'cityId':cityId,'agencyId':agencyId}
    NewSession.post(url=zdh_url, data=zdh_data)
    conn_test_A = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
    cur_A = conn_test_A.cursor()
    conn_test_A.select_db(test_ckDb)
    cur_A.execute("select id,rgl_number_id,rgl_store_goods_order_id,createdAt FROM return_goods_list where rgl_state='20' and rgl_warehouse_id='{0}'and rgl_store_goods_order_id='{1}' order by id desc".format(warehouseId,orderId))
    zp = cur_A.fetchone()
    cur_A.close()
    if zp:
        print('\n退货单号:',str(zp[1]),'\t订单编号:',str(zp[2]),'\t创建时间:',zp[3])
        cur_B = conn_test_A.cursor()
        conn_test_A.select_db(test_ckDb)
        cur_B.execute("select id FROM return_goods_list_details where  rgld_return_goods_list_id='{0}' order by id desc".format(zp[0]))
        zp_B = cur_B.fetchone()
        cur_B.close()
        conn_test_A.close()
        if zp_B:
            return_url='{0}/api/returnGoods/list'.format(invent_url)
            NewSession.post(url=return_url,data={'numberId':str(zp[1])})
            confirm_url='{0}/api/returnGoods/confirm'.format(invent_url)
            confirm_res=NewSession.post(url=confirm_url,data={'id':zp[0],'details[0][id]':zp_B[0],'details[0][produceDate]':time.strftime('%Y-%m-%d',time.localtime(time.time()))})
            confirm_json=json.loads(changeIntoStr(confirm_res.text))
            if confirm_json['tag']=='success':
                print('\n已入库')
    else:
        print('未找到该城市对应的订单编号退货单')

def SJ(cityId,agencyId,invent_url,url_username,url_password,warehouseId,orderId):
    # 登录
    if str(cityId)==str(320100):
        area ={'JH':'A01-01-01-01'}
    elif str(cityId)==str(320200):
        area ={'JH':'A01-01-01-01'}
    else:
        area={'JH': 'AA11-11-11-11'}
    print('\n默认上架拣货位:',area['JH'])
    SJ_area = input('\n输入要上架的位置(按Enter跳过即使用拣货位):')
    if SJ_area!='':
        area['JH']=SJ_area
    NewSession=requests.Session()
    login_url = '{0}/users/login'.format(invent_url)
    login_data = {'userName': url_username, 'password': url_password}
    NewSession.post(url=login_url, data=login_data)
    zdh_url = '{0}/users/updateAgency'.format(invent_url)
    zdh_data = {'cityId':cityId,'agencyId':agencyId}
    NewSession.post(url=zdh_url, data=zdh_data)
    conn_test_A = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
    cur_A = conn_test_A.cursor()
    conn_test_A.select_db(test_ckDb)
    cur_A.execute("select identificationCode  FROM check_up_orders where state='999' and WarehouseId='{0}'and StockInOrderId='{1}' order by id desc limit 1".format(warehouseId,orderId))
    zp = cur_A.fetchone()
    cur_A.close()
    conn_test_A.close()
    if zp:
        getToken_url='%s/api/getToken?numberId=%s&key=SJ'%(invent_url,zp[0])
        getToken_res=NewSession.get(url=getToken_url)
        getToken_json=json.loads(getToken_res.text)
        token=getToken_json['token']
        onRack_url='{0}/api/onRack/createOnRack'.format(invent_url)
        NewSession.post(url=onRack_url,data={'identificationCode':zp[0],'token':token})

        conn_test_B = pymysql.connect(host=test_db_ip, user=test_user, passwd=test_passwd, port=3306, charset="utf8")
        cur_B = conn_test_B.cursor()
        conn_test_B.select_db(test_ckDb)
        cur_B.execute("select id,numberId FROM on_racks where state='0' and WarehouseId='{0}'and checkUpOrderId='{1}' order by id desc limit 1".format(warehouseId, zp[0]))
        zp_B = cur_B.fetchone()
        cur_B.execute("select id FROM on_rack_details where OnRackId='{0}' order by id desc limit 1".format(zp_B[0]))
        zp_BB=cur_B.fetchone()
        cur_B.close()
        conn_test_B.close()
        viewOnRack_url='{0}/api/onRack/viewOnRackDetail'.format(invent_url)
        viewOnRack_res=NewSession.post(url=viewOnRack_url,data={'onRackId':zp_B[0],'id':zp_BB[0]})
        viewOnRack_json=json.loads(changeIntoStr(viewOnRack_res.text))
        getOToken_url='%s/api/getToken?numberId=%s&key=SJ'%(invent_url,zp_B[1])
        getOToken_res=NewSession.get(url=getOToken_url)
        getOToken_json=json.loads(changeIntoStr(getOToken_res.text))
        OToken=getOToken_json['token']
        verification_url='{0}/api/onRack/verification'.format(invent_url)
        verification_res=NewSession.post(url=verification_url,data={'param[0][onRackDetailId]':viewOnRack_json['data'][0]['id'],
                                                                    'param[0][GoodId]':viewOnRack_json['data'][0]['GoodId'],
                                                                    'param[0][quantity]':viewOnRack_json['data'][0]['quantity'],
                                                                    'param[0][produceDate]':viewOnRack_json['data'][0]['produceDate'],
                                                                    'param[0][targetPosition]':area['JH'],
                                                                    'param[0][LPN]':'','param[0][onRackId]':zp_B[0],
                                                                    'param[0][index]':0})
        verification_json=json.loads(changeIntoStr(verification_res.text))
        if verification_json['tag']=='success':
            onRackUpdate_url='{0}/api/onRack/update'.format(invent_url)
            onRackUpdate_res=NewSession.post(url=onRackUpdate_url,data={'param[0][onRackDetailId]':viewOnRack_json['data'][0]['id'],
                                                                        'param[0][GoodId]':viewOnRack_json['data'][0]['GoodId'],
                                                                        'param[0][quantity]':viewOnRack_json['data'][0]['quantity'],
                                                                        'param[0][produceDate]':viewOnRack_json['data'][0]['produceDate'],
                                                                        'param[0][targetPosition]':area['JH'],
                                                                        'param[0][LPN]':'','param[0][onRackId]':zp_B[0],
                                                                        'param[0][index]':0,
                                                                        'param[0][id]':verification_json['param'][0]['id'],
                                                                        'param[0][type]':verification_json['param'][0]['type'],
                                                                        'onRackOperator':'倔强的小强',
                                                                        'token':OToken})
            onRackUpdate_json=json.loads(changeIntoStr(onRackUpdate_res.text))
            if onRackUpdate_json['tag']=='success':
                print('\n上架成功')
        else:
            print('\n系统无相应库位号')

def main():
    cityChange = {'nanJin': {'cityId': 320100, 'agencyId': 101,'mainhouse':13,'prehouse':22}, 'changZhou': {'cityId': 320400, 'agencyId': 3,'mainhouse':1,'prehouse':False},
                  'wuXi': {'cityId': 320200, 'agencyId': 17,'mainhouse':4,'prehouse':[15,16,17]}, 'lianYunGang': {'cityId': 320700, 'agencyId': 171,'mainhouse':80,'prehouse':81}}
    print()
    while True:
        print()
        print('*'*30)
        print('请选择以下业务(输入数字选择):')
        order_num=input('\n\n1.新建红包,\t2.新建优惠券,\t3.更改达豆,\t4.商城下单,\n\n5.猪行侠验证码,\t6.全局新建整散商品,\t7.客服系统审核,\t8.查询系统,'
                            '\n\n9.仓库运输系统走单,\t10.主仓入库,\t11.采购,\t12.猪行侠业务,\n\n13.退货入库,\t14.库位上架,\t0.退出,\n')
        if str(order_num)==str(1):
            print('请选择城市(输入数字选择):')
            city_num=input('\n1.南京,\n\n2.常州,\n\n3.无锡,\n\n4.连云港,\n')
            if str(city_num)==str(1):
                cityId=cityChange['nanJin']['cityId']
                agencyId=cityChange['nanJin']['agencyId']
                server_url = 'http://192.168.1.251:31010'
                url_username = '13111111111'
                url_password = '123456'
            elif str(city_num)==str(2):
                cityId=cityChange['changZhou']['cityId']
                agencyId=cityChange['changZhou']['agencyId']
                server_url = 'http://192.168.1.251:31000'
                url_username = '13111111111'
                url_password = '123456'
            elif str(city_num)==str(3):
                cityId=cityChange['wuXi']['cityId']
                agencyId=cityChange['wuXi']['agencyId']
                server_url = 'http://192.168.1.251:31010'
                url_username = '12345678910'
                url_password = '123456'
            elif str(city_num)==str(4):
                cityId=cityChange['lianYunGang']['cityId']
                agencyId=cityChange['lianYunGang']['agencyId']
                server_url = 'http://192.168.1.251:31010'
                url_username = '12345678910'
                url_password = '123456'
            else:
                continue
            redGift_value = input('红包金额:')
            redGift_quantity = input('红包发放数量:')
            redGift_ownLimit = input('用户可领取数量:')
            redGift_useBaseLine = input('红包使用条件金额(满多少可用?):')
            redGift_instruction = '满{0}减{1}'.format(redGift_useBaseLine,redGift_value)
            print('描述为:'+redGift_instruction)
            createRedGift(cityId,agencyId,server_url,url_username,url_password,redGift_value,redGift_quantity,redGift_ownLimit,redGift_useBaseLine,redGift_instruction)
            print('请选择是否店铺领取(输入数字选择):')
            bangding_num=input('\n1.领取,\n2.不领取,\n')
            if str(bangding_num)==str(1):
                store_main_username=input('输入店铺登陆账号:')
                store_main_password=input('输入店铺登陆密码(默认123456,可回车跳过):')
                if store_main_password=='':
                    store_main_password=123456
                receiveRedGift(store_main_username,store_main_password)
            elif str(bangding_num)==str(2):
                pass

        elif str(order_num)==str(2):
            print('请选择城市(输入数字选择):')
            city_num=input('\n1.南京,\n\n2.常州,\n\n3.无锡,\n\n4.连云港,\n')
            if str(city_num)==str(1):
                cityId=cityChange['nanJin']['cityId']
                agencyId=cityChange['nanJin']['agencyId']
                server_url = 'http://192.168.1.251:31010'
                url_username = '13111111111'
                url_password = '123456'
            elif str(city_num)==str(2):
                cityId=cityChange['changZhou']['cityId']
                agencyId=cityChange['changZhou']['agencyId']
                server_url = 'http://192.168.1.251:31000'
                url_username = '13111111111'
                url_password = '123456'
            elif str(city_num)==str(3):
                cityId=cityChange['wuXi']['cityId']
                agencyId=cityChange['wuXi']['agencyId']
                server_url = 'http://192.168.1.251:31010'
                url_username = '12345678910'
                url_password = '123456'
            elif str(city_num)==str(4):
                cityId=cityChange['lianYunGang']['cityId']
                agencyId=cityChange['lianYunGang']['agencyId']
                server_url = 'http://192.168.1.251:31010'
                url_username = '12345678910'
                url_password = '123456'
            else:
                continue
            coupon_value = input('优惠券金额:')
            coupon_quantity = input('优惠券发放数量:')
            coupon_useBaseLine = input('优惠券使用条件金额(满多少可用?):')
            coupon_instruction = '满{0}减{1}'.format(coupon_useBaseLine,coupon_value)
            print('描述为:' + coupon_instruction)
            newCoupon(cityId,agencyId,server_url,url_username,url_password,coupon_value,coupon_quantity,coupon_useBaseLine,coupon_instruction)
        elif str(order_num)==str(3):
            dd_phoneNum = input('输入店铺登陆账号:')
            dd_count = input('输入达豆数量:')
            UpdateDadou(dd_phoneNum,dd_count)
        elif str(order_num)==str(4):
            print('请选择城市(输入数字选择):')
            city_num=input('\n1.南京,\n\n2.常州,\n\n3.无锡,\n\n4.连云港,\n')
            if str(city_num)==str(1):
                cityId=cityChange['nanJin']['cityId']
                prehouse = cityChange['nanJin']['prehouse']
            elif str(city_num)==str(2):
                cityId=cityChange['changZhou']['cityId']
                prehouse = cityChange['changZhou']['prehouse']
            elif str(city_num)==str(3):
                cityId=cityChange['wuXi']['cityId']
                prehouse = cityChange['wuXi']['prehouse']
            elif str(city_num)==str(4):
                cityId=cityChange['lianYunGang']['cityId']
                prehouse = cityChange['lianYunGang']['prehouse']
            else:
                continue
            checkStoreName(cityId, prehouse)
            purchase_phoneNum = input('\n输入商城店铺登陆账号:\n')
            clean_redis(purchase_phoneNum)
            store_Order(cityId,purchase_phoneNum)

        elif str(order_num)==str(5):
            zxx_loginNum = input('输入猪行侠登陆账号:')
            getZXXCode(zxx_loginNum)
        elif str(order_num)==str(6):
            img_jpg=img_content()
            if not img_jpg:
                print('\t上传图片动作失败,无法新建整散商品')
                continue
            task_ID = input('\n1.新建散装,\n\n2.新建整装,\n')
            nav_Name = input('\n输入新建商品名标签(默认跳过):\n')
            if str(task_ID)==str(1):
                count_ID = input('\n输入新建散装商品数量:\n')
                for count in range(int(count_ID)):
                    name=nav_Name+str(int(time.time()))
                    create_san_product(name,img_jpg)
            elif str(task_ID)==str(2):
                type_ID=input('\n1.自动新建散装并绑定整装,\n\n2.手动输入散装库存编号,\n')
                if str(type_ID)==str(1):
                    count_ID = input('\n输入新建整装商品数量:\n')
                    for count in range(int(count_ID)):
                        name = nav_Name+str(int(time.time()))
                        full_Id = create_san_product(name,img_jpg)
                        if full_Id:
                            create_zheng_product(name,full_Id,img_jpg)
                        else:
                            continue
                elif str(type_ID)==str(2):
                    name = nav_Name+str(int(time.time()))
                    full_Id = input('\n输入关联的散装库存编号:\n')
                    if checkGoodsExist(full_Id):
                        create_zheng_product(name,full_Id,img_jpg)
                else:
                    continue
            else:
                continue
        elif str(order_num)==str(7):
            print('请选择城市(输入数字选择):')
            city_num=input('\n1.南京,\n\n2.无锡,\n\n3.连云港,\n')
            if str(city_num)==str(1):
                cityId=cityChange['nanJin']['cityId']
                agencyId=cityChange['nanJin']['agencyId']
                mainhouse = cityChange['nanJin']['mainhouse']
                server_url = 'http://192.168.1.251:3586'
                invent_url = 'http://192.168.1.251:48000'
                url_username = '12345678910'
                invent_username='12345678910'
                url_password = '123456'
            elif str(city_num)==str(2):
                cityId=cityChange['wuXi']['cityId']
                agencyId=cityChange['wuXi']['agencyId']
                mainhouse = cityChange['wuXi']['mainhouse']
                server_url = 'http://192.168.1.251:3586'
                invent_url = 'http://192.168.1.251:48000'
                url_username = '12345678910'
                invent_username = '13111111111'
                url_password = '123456'
            elif str(city_num)==str(3):
                cityId=cityChange['lianYunGang']['cityId']
                agencyId=cityChange['lianYunGang']['agencyId']
                mainhouse = cityChange['lianYunGang']['mainhouse']
                server_url = 'http://192.168.1.251:3586'
                invent_url = 'http://192.168.1.251:48000'
                url_username = '12345678910'
                invent_username = '12345678910'
                url_password = '123456'
            else:
                continue
            task_num = input('\n1.审核订单\t2.取消订单\t3.订单退货\n')
            if str(task_num)==str(1):
                SureOrder(cityId, agencyId, server_url, url_username, url_password)
            elif str(task_num)==str(2):
                order_Id = input('\n输入要取消的订单号\n')
                CancleOrder(cityId, agencyId, server_url, url_username, url_password, order_Id)
            elif str(task_num)==str(3):
                order_Id = input('\n输入要退货的订单号\n')
                ThOrder(cityId, agencyId, server_url, url_username, url_password, order_Id,invent_url,invent_username,mainhouse)
            else:
                continue
        elif str(order_num)==str(8):
            print('请选择城市(输入数字选择):')
            city_num=input('\n1.南京,\n\n2.常州,\n\n3.无锡,\n\n4.连云港,\n')
            if str(city_num)==str(1):
                cityId=cityChange['nanJin']['cityId']
                mainhouse=cityChange['nanJin']['mainhouse']
                prehouse=cityChange['nanJin']['prehouse']
            elif str(city_num)==str(2):
                cityId=cityChange['changZhou']['cityId']
                mainhouse = cityChange['changZhou']['mainhouse']
                prehouse = cityChange['changZhou']['prehouse']
            elif str(city_num)==str(3):
                cityId=cityChange['wuXi']['cityId']
                mainhouse = cityChange['wuXi']['mainhouse']
                prehouse = cityChange['wuXi']['prehouse']
            elif str(city_num)==str(4):
                cityId=cityChange['lianYunGang']['cityId']
                mainhouse = cityChange['lianYunGang']['mainhouse']
                prehouse = cityChange['lianYunGang']['prehouse']
            else:
                continue
            task_num = input('\n1.查询店铺账号,\n\n2.查询店铺是主仓或是前置仓,\n\n3.查询入库验收账号,\n\n4.退出,\n')
            if str(task_num)==str(1):
                checkStoreName(cityId,prehouse)
            elif str(task_num)==str(2):
                store_name = input('输入店铺登录账号:')
                checkStoreType(cityId, store_name, prehouse)
            elif str(task_num)==str(3):
                checkRuKuName(mainhouse)
            else:
                continue
        elif str(order_num)==str(9):
            print('请选择城市(输入数字选择):')
            city_num=input('\n1.南京,\n\n2.无锡,\n\n3.连云港,\n')
            if str(city_num)==str(1):
                cityId=cityChange['nanJin']['cityId']
                agencyId=cityChange['nanJin']['agencyId']
                mainhouse=cityChange['nanJin']['mainhouse']
                prehouse=cityChange['nanJin']['prehouse']
                server_url = 'http://192.168.1.251:48000'
                url_username = '12345678910'
                url_password = '123456'
            elif str(city_num)==str(2):
                cityId=cityChange['wuXi']['cityId']
                agencyId=cityChange['wuXi']['agencyId']
                mainhouse = cityChange['wuXi']['mainhouse']
                prehouse = cityChange['wuXi']['prehouse']
                server_url = 'http://192.168.1.251:48000'
                url_username = '13111111111'
                url_password = '123456'
            elif str(city_num)==str(3):
                cityId=cityChange['lianYunGang']['cityId']
                agencyId=cityChange['lianYunGang']['agencyId']
                mainhouse = cityChange['lianYunGang']['mainhouse']
                prehouse = cityChange['lianYunGang']['prehouse']
                server_url = 'http://192.168.1.251:48000'
                url_username = '12345678910'
                url_password = '123456'
            else:
                continue
            order_Id = input('\n输入订单号\n')
            print('请选择订单类型')
            order_ty = input('\n1.订单为主仓店铺订单,\n\n2.订单为前置仓店铺订单,\n')
            if str(order_ty)==str(1):
                mainstorerun(cityId,agencyId,server_url,url_username,url_password,order_Id)
            elif str(order_ty)==str(2):
                prestorerun(cityId,agencyId,server_url,url_username,url_password,order_Id)
            else:
                continue
        elif str(order_num)==str(10):
            print('请选择城市(输入数字选择):')
            city_num=input('\n1.南京,\n\n2.无锡,\n\n3.连云港,\n')
            if str(city_num)==str(1):
                cityId=cityChange['nanJin']['cityId']
                agencyId=cityChange['nanJin']['agencyId']
                mainhouse=cityChange['nanJin']['mainhouse']
                prehouse=cityChange['nanJin']['prehouse']
                server_url = 'http://192.168.1.251:48000'
                url_username = '12345678910'
                url_password = '123456'
                worker={"id":28,"workId":"njs001","name":"哈哈哈"}
            elif str(city_num)==str(2):
                cityId=cityChange['wuXi']['cityId']
                agencyId=cityChange['wuXi']['agencyId']
                mainhouse = cityChange['wuXi']['mainhouse']
                prehouse = cityChange['wuXi']['prehouse']
                server_url = 'http://192.168.1.251:48000'
                url_username = '13111111111'
                url_password = '123456'
                worker={"id":2,"workId":"wxs001","name":"无锡验收员"}
            elif str(city_num)==str(3):
                cityId=cityChange['lianYunGang']['cityId']
                agencyId=cityChange['lianYunGang']['agencyId']
                mainhouse = cityChange['lianYunGang']['mainhouse']
                prehouse = cityChange['lianYunGang']['prehouse']
                server_url = 'http://192.168.1.251:48000'
                url_username = '12345678910'
                url_password = '123456'
                worker={"id":32,"workId":"ZDH001","name":"连云港市"}
            else:
                continue
            order_Id = input('\n输入采购单号\n')
            Ruku(cityId, agencyId, worker, order_Id, server_url, url_username, url_password)
        elif str(order_num)==str(11):
            print('请选择城市(输入数字选择):')
            city_num=input('\n1.南京,\n\n2.无锡,\n\n3.连云港,\n')
            if str(city_num)==str(1):
                cityId=cityChange['nanJin']['cityId']
                agencyId=cityChange['nanJin']['agencyId']
                mainhouse=cityChange['nanJin']['mainhouse']
                prehouse=cityChange['nanJin']['prehouse']
                server_url = 'http://192.168.1.248:31100'
                url_username = '12345678910'
                url_password = '123456'
                worker={'name':'供应商test1','providerId':'100693'}
            elif str(city_num)==str(2):
                cityId=cityChange['wuXi']['cityId']
                agencyId=cityChange['wuXi']['agencyId']
                mainhouse = cityChange['wuXi']['mainhouse']
                prehouse = cityChange['wuXi']['prehouse']
                server_url = 'http://192.168.1.248:31100'
                url_username = '12345678910'
                url_password = '123456'
                worker={'name':'顶替','providerId':'100696'}
            elif str(city_num)==str(3):
                cityId=cityChange['lianYunGang']['cityId']
                agencyId=cityChange['lianYunGang']['agencyId']
                mainhouse = cityChange['lianYunGang']['mainhouse']
                prehouse = cityChange['lianYunGang']['prehouse']
                server_url = 'http://192.168.1.248:31100'
                url_username = '12345678910'
                url_password = '123456'
                worker={'name':'A01','providerId':'100716'}
            else:
                continue
            print('\n*****使用默认固定供应商:', worker['name'])
            checkUsedGood(cityId, worker['providerId'])
            ck_Id = input('\n输入商品库存编号\n')
            quantity = input('\n输入商品采购数量\n')
            print('\n请选择采购仓库')
            order_ty = input('\n1.主仓采购,\t2.前置仓采购,\n')
            if str(order_ty)==str(1):
                CaiGou(cityId, agencyId, server_url, mainhouse, url_username, url_password, ck_Id, quantity,worker['providerId'])
            elif str(order_ty)==str(2):
                if str(cityId)==str(320200):
                    print('无锡主要三个前置仓,请选择')
                    wuxi_pre = input('\n1.无锡前置仓1,\t2.无锡前置仓2,\t3.无锡前置仓3\n')
                    if str(wuxi_pre)==str(1):
                        prehouse=15
                    elif str(wuxi_pre)==str(2):
                        prehouse=16
                    elif str(wuxi_pre)==str(3):
                        prehouse=17
                    else:
                        continue
                CaiGou(cityId, agencyId, server_url, prehouse, url_username, url_password, ck_Id, quantity,worker['providerId'])
            else:
                continue
        elif str(order_num)==str(12):
            print('请选择城市(输入数字选择):')
            city_num=input('\n1.南京,\n\n2.无锡,\n\n3.连云港,\n')
            if str(city_num)==str(1):
                cityId=cityChange['nanJin']['cityId']
                server_url = 'http://192.168.1.251:50000'
                worker = {'name':'ps001', 'phone':'15575000999'}
            elif str(city_num)==str(2):
                cityId=cityChange['wuXi']['cityId']
                server_url = 'http://192.168.1.251:50000'
                worker = {'name':'ps001', 'phone':'15575000995'}
            elif str(city_num)==str(3):
                cityId=cityChange['lianYunGang']['cityId']
                server_url = 'http://192.168.1.251:50000'
                worker = {'name':'ps001', 'phone':'17621145336'}
            else:
                continue
            print('\n默认主仓猪行侠手机号:',worker['phone'])
            print('\n前置仓猪行侠手机号需自己输入')
            ps_phone=input('\n输入前置仓猪行侠手机号(主仓猪行侠Enter跳过)\n')
            if ps_phone !='':
                phone=ps_phone
            else:
                phone=worker['phone']
            task_type=input('\n1.送达\n\n2.拒收\n\n3.部分送达\n\n4.退货取货中\n')
            ZZX(server_url, phone, task_type)
        elif str(order_num)==str(13):
            print('\n仓库运输系统_退货入库业务')
            print('\n请选择城市(输入数字选择):')
            city_num=input('\n1.南京,\n\n2.无锡,\n\n3.连云港,\n')
            if str(city_num)==str(1):
                cityId=cityChange['nanJin']['cityId']
                agencyId=cityChange['nanJin']['agencyId']
                mainhouse = cityChange['nanJin']['mainhouse']
                invent_url = 'http://192.168.1.251:48000'
                invent_username='12345678910'
                url_password = '123456'
            elif str(city_num)==str(2):
                cityId=cityChange['wuXi']['cityId']
                agencyId=cityChange['wuXi']['agencyId']
                mainhouse = cityChange['wuXi']['mainhouse']
                invent_url = 'http://192.168.1.251:48000'
                invent_username = '13111111111'
                url_password = '123456'
            elif str(city_num)==str(3):
                cityId=cityChange['lianYunGang']['cityId']
                agencyId=cityChange['lianYunGang']['agencyId']
                mainhouse = cityChange['lianYunGang']['mainhouse']
                invent_url = 'http://192.168.1.251:48000'
                invent_username = '12345678910'
                url_password = '123456'
            else:
                continue
            order_Id = input('\n输入退货入库订单编号\n')
            TH_RU(cityId, agencyId, invent_url, invent_username, url_password, mainhouse, order_Id)
        elif str(order_num)==str(14):
            print('\n请选择城市(输入数字选择):')
            city_num=input('\n1.南京,\n\n2.无锡,\n\n3.连云港,\n')
            if str(city_num)==str(1):
                cityId=cityChange['nanJin']['cityId']
                agencyId=cityChange['nanJin']['agencyId']
                mainhouse = cityChange['nanJin']['mainhouse']
                invent_url = 'http://192.168.1.251:48000'
                invent_username='12345678910'
                url_password = '123456'
            elif str(city_num)==str(2):
                cityId=cityChange['wuXi']['cityId']
                agencyId=cityChange['wuXi']['agencyId']
                mainhouse = cityChange['wuXi']['mainhouse']
                invent_url = 'http://192.168.1.251:48000'
                invent_username = '13111111111'
                url_password = '123456'
            elif str(city_num)==str(3):
                cityId=cityChange['lianYunGang']['cityId']
                agencyId=cityChange['lianYunGang']['agencyId']
                mainhouse = cityChange['lianYunGang']['mainhouse']
                invent_url = 'http://192.168.1.251:48000'
                invent_username = '12345678910'
                url_password = '123456'
            else:
                continue
            order_Id = input('\n输入采购入库单号\n')
            SJ(cityId, agencyId, invent_url, invent_username, url_password, mainhouse, order_Id)
        elif str(order_num)==str(0):
            break
main()