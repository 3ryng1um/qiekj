import requests
import time
import json
from jsonpath_ng import parse
import traceback

# ip=47.110.172.244
shopID = "202011211129580000018669638151" # tyut店铺ID

CYAN = '\033[96m'
MAGENTA = '\033[95m'
WHITE = '\033[97m'
BOLD = '\033[1m'
RESET = '\033[0m'

def print_json(json_data):
    print("\n=== 接口返回的完整JSON ===")
    print(json.dumps(json_data, ensure_ascii=False, indent=2))

def login():
    global token
    phone = input("请输入手机号: ")
    headers = {
        "Version": "1.59.3",
        "channel": "android_app",
        "phoneBrand": "Redmi",
        "timestamp": t,
        "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        "Host": "userapi.qiekj.com",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip",
        "User-Agent": "okhttp/3.14.9"
    }
    try:
        res = requests.post(
            url="https://userapi.qiekj.com/common/sms/sendCode",
            data="phone=" + phone + "&template=reg",
            headers=headers
        )
    except Exception as e:
        print("【发送验证码】环节出错")
        print_json(res.json() if 'res' in locals() else {})
        raise

    code = input("\n请输入收到的验证码: ")
    try:
        res = requests.post(
            url="https://userapi.qiekj.com/user/reg",
            data="channel=android_app&phone=" + phone + "&verify=" + code,
            headers=headers
        )
        gettoken = json.loads(res.text)["data"]["token"]
        print("\n\ntoken = ", gettoken)
        token = gettoken
    except Exception as e:
        print("【登录/获取token】环节出错")
        print_json(res.json() if 'res' in locals() else {})
        raise

def get_latest_used():
    global result_goodsId
    headers = {
        'Authorization': token,
        'Version': '1.59.3',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'okhttp/3.14.9',
        'timestamp': t,
        'Host': 'userapi.qiekj.com',
        'channel': 'channel',
        'phoneBrand': 'Redmi'
    }
    data1 = {'categoryCode': '5', 'token': token}
    try:
        response_list = requests.post(
            url='https://userapi.qiekj.com/goods/latestUsed',
            headers=headers,
            data=data1
        )
        name = [match.value for match in parse('$..goodsName').find(response_list.json())]
        result_goodsId = [match.value for match in parse('$..goodsId').find(response_list.json())]
        for i, (n, g) in enumerate(zip(name, result_goodsId)):
            print(f"[{i}] goodsName: {n}, goodsId: {g}")
    except Exception as e:
        print("【get_latest_used】环节出错")
        print_json(response_list.json() if 'response_list' in locals() else {})
        raise

def get_all_goods(shopID):
    global result_goodsId
    headers = {
        'Authorization': token,
        'Version': '1.59.3',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'okhttp/3.14.9',
        'timestamp': t,
        'Host': 'userapi.qiekj.com',
        'channel': 'channel',
        'phoneBrand': 'Redmi'
    }
    data = {'goodsPage': '1', 'pageSize': '20', 'shopId': shopID, 'machineTypeId': '04', 'orgId': '0', 'token': token}
    try:
        response = requests.post(
            url='https://userapi.qiekj.com/appointNew/near/newMachines',
            headers=headers,
            data=data
        )
        result_name = [match.value for match in parse('$..goodsName').find(response.json())]
        result_goodsId = [match.value for match in parse('$..goodsId').find(response.json())]
        for i, (n, g) in enumerate(zip(result_name, result_goodsId)):
            print(f"[{i}] goodsName: {n}, goodsId: {g}")
    except Exception as e:
        print("【get_all_goods】环节出错")
        print_json(response.json() if 'response' in locals() else {})
        raise

def all_or_latest(choice):
    global result_goodsId
    if choice == '1':
        get_all_goods(shopID)
    elif choice == '2':
        get_latest_used()
    else:
        print("无效的选择，请输入1或2。")
        exit()
    cho = int(input("请输入你选择的商品编号: "))
    sku = goodsid2sku(result_goodsId[cho])
    imei = get_imei(result_goodsId[cho])
    return sku, imei

def goodsid2sku(goodsid):
    headers = {
        'Authorization': token,
        'Version': '1.59.3',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'okhttp/3.14.9',
        'timestamp': t,
        'Host': 'userapi.qiekj.com',
        'channel': 'channel',
        'phoneBrand': 'Redmi'
    }
    data = {'goodsId': goodsid, 'token': token}
    try:
        response = requests.post(
            url='https://userapi.qiekj.com/goods/normal/skus',
            headers=headers,
            data=data
        )
        sku = [match.value for match in parse('$.data[0].skuId').find(response.json())]
        return sku[0]
    except Exception as e:
        print("【goodsid2sku】环节出错")
        print_json(response.json() if 'response' in locals() else {})
        raise

def get_imei(goodsid):
    headers = {
        'Authorization': token,
        'Version': '1.59.3',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'okhttp/3.14.9',
        'timestamp': t,
        'Host': 'userapi.qiekj.com',
        'channel': 'channel',
        'phoneBrand': 'Redmi'
    }
    data = {'goodsId': goodsid, 'token': token}
    try:
        response = requests.post(
            url='https://userapi.qiekj.com/goods/normal/details',
            headers=headers,
            data=data
        )
        imei = [match.value for match in parse('$.data.imei').find(response.json())]
        return imei[0]
    except Exception as e:
        print("【get_imei】环节出错")
        print_json(response.json() if 'response' in locals() else {})
        raise

def use_intergral():
    headers = {
        'Authorization': token,
        'Version': '1.59.3',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'okhttp/3.14.9',
        'timestamp': t,
        'Host': 'userapi.qiekj.com',
        'channel': 'channel',
        'phoneBrand': 'Redmi'
    }
    data = {'token': token}
    try:
        response = requests.post(
            url='https://userapi.qiekj.com/userIntegral/checkUserIsRisk',
            headers=headers,
            data=data
        )
    except Exception as e:
        print("【use_intergral】环节出错")
        print_json(response.json() if 'response' in locals() else {})
        raise

def unlock_water(sku):# 这个也能用，下面那个模拟得更全
    headers = {
        'Authorization': token,
        'Version': '1.59.3',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'okhttp/3.14.9',
        'timestamp': t,
        'Host': 'userapi.qiekj.com',
        'channel': 'channel',
        'phoneBrand': 'Redmi'
    }
    data = {
        'skuId': sku,
        'promotions': '[{"assetId":"0","oldPromotionId":"","orgId":"0","promotionId":"0","promotionType":"-6"},{"assetId":"0","oldPromotionId":"","orgId":"0","promotionId":"0","promotionType":"-7"},{"assetId":"0","oldPromotionId":"0","orgId":"0","promotionId":"0","promotionType":"8"}]',
        'token': token
    }
    try:
        response = requests.post(
            url='https://userapi.qiekj.com/goods/water/unlock',
            headers=headers,
            data=data
        )
        msgId = response.json()['data']['msgId']
        orderno = response.json()['data']['orderNo']
        return msgId, orderno
    except Exception as e:
        print("【unlock_water】环节出错")
        print_json(response.json() if 'response' in locals() else {})
        raise

def whole_unlock_water(imei, sku):
    headers = {
        'Authorization': token,
        'Version': '1.59.3',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'okhttp/3.14.9',
        'timestamp': t,
        'Host': 'userapi.qiekj.com',
        'channel': 'channel',
        'phoneBrand': 'Redmi'
    }
    try:
        data2 = {'method': '15', 'token': token}
        response2 = requests.post(
            url='https://userapi.qiekj.com/payChannelRoute/addUserAfterPayChannel',
            headers=headers,
            data=data2
        )
        data3 = {'categoryCode': '04', 'imei': imei, 'token': token}
        response3 = requests.post(
            url='https://userapi.qiekj.com/orderRisk/isCheckLocation',
            headers=headers,
            data=data3
        )
        msgId, orderno = unlock_water(sku)
        return msgId, orderno
    except Exception as e:
        print("【whole_unlock_water】环节出错")
        print_json(response2.json() if 'response2' in locals() else {})
        raise

def query_balance():
    headers = {
        'Authorization': token,
        'Version': '1.59.3',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'okhttp/3.14.9',
        'timestamp': t,
        'Host': 'userapi.qiekj.com',
        'channel': 'channel',
        'phoneBrand': 'Redmi'
    }
    data = {'token': token}
    try:
        response = requests.post(
            url='https://userapi.qiekj.com/user/balance',
            headers=headers,
            data=data
        )
        coin = [match.value for match in parse('$..tokenCoin').find(response.json())]
        integral = [match.value for match in parse('$..integral').find(response.json())]
        integralamount = [match.value for match in parse('$..integralAmount').find(response.json())]
        print(f"{CYAN}tokenCoin: {coin[0]/100:.2f}, integral: {integral[0]}, integralAmount: {integralamount[0]}{RESET}")
    except Exception as e:
        print("【query_balance】环节出错")
        print_json(response.json() if 'response' in locals() else {})
        raise

def afterpay(sku):
    headers = {
        'Authorization': token,
        'Version': '1.59.3',
        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
        'User-Agent': 'okhttp/3.14.9',
        'timestamp': t,
        'Host': 'userapi.qiekj.com',
        'channel': 'channel',
        'phoneBrand': 'Redmi'
    }
    data7 = {'skuId': sku, 'token': token}
    try:
        while True:
            response7 = requests.post(
                url='https://userapi.qiekj.com/goods/water/sync',
                headers=headers,
                data=data7
            )
            print_json(response7.json())
            if response7.json().get('data', {}).get('workStatus') != 2:
                break
            time.sleep(1)
        orderno = response7.json().get('data', {}).get('identify')

        data8 = {'orderNo': orderno, 'token': token}
        response8 = requests.post(
            url='https://userapi.qiekj.com/order/afterPay/creating',
            headers=headers,
            data=data8
        )
        print("res8:")
        print_json(response8.json())
        data9 = {'orderId': response8.json()['data']['orderId'], 'token': token}
        response9 = requests.post(
            url='https://userapi.qiekj.com/order/detail',
            headers=headers,
            data=data9
        )
        print_json(response9.json()) # 这是完整的花费信息

        data = response9.json().get('data', {})
        # tradeOrderItem 中的 originPrice
        trade_item = data.get('tradeOrderItem', [])
        origin_price = trade_item[0].get('originPrice') if len(trade_item) > 0 else None
        if origin_price is not None:
            print(f"{CYAN}订单原价: {origin_price}, \n{RESET}")
        promo_list = data.get('promotionList', [])
        prolen=len(promo_list)
        for p in promo_list:
            ptype = p.get('promotionType')
            if ptype==4: # 小票
                discount1 = p.get('discountAmount')
                if discount1 is not None:
                    print(f"{CYAN}花费小票: {discount1}, \n{RESET}")
            elif ptype==8: # 积分
                discount2 = p.get('discountAmount')
                if discount2 is not None:
                    print(f"{CYAN}积分抵扣: {discount2}, \n{RESET}")
            else:
                print(f"promotiontype:{ptype},discount:{p.get('discountAmount')}\n")

    except Exception as e:
        print("【afterpay】环节出错")
        print_json(response7.json() if 'response7' in locals() else {})
        # raise

# ====================== 主程序 ======================
try:
    t = str(int(time.time() * 1000))

    # 自行填写token或使用login函数获得新token（新token不会覆盖以前的，可以不用每次都重接收）
    token=''
    login()
    query_balance() # tokenCoin是小票, integral是积分（网上有刷积分的脚本，不怕封号可以用） integralAmount是积分可抵的价格

    print("1 - 所有商品")
    print("2 - 最近使用的商品")
    choice = input("请输入 1 或 2: ")
    sku, imei = all_or_latest(choice)
    query_balance()
    use_intergral() # 用积分抵只需要支付0.01元的订单，积分不能抵全部价格
    msgId, orderno = whole_unlock_water(imei, sku) # 这就解开了,可以接水了

    afterpay(sku)

except Exception as e:
    print(f"\n{BOLD}{MAGENTA}程序运行出错！{RESET}")
    print(f"错误位置: {traceback.extract_tb(e.__traceback__)[-1]}")
    print(f"错误类型: {type(e).__name__}")
    print(f"错误信息: {e}")