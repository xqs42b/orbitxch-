# coding=utf-8

import string 
import requests 
import random
import json
import time
import multiprocessing 

_marketCatalogueList = 'marketCatalogueList'
_competition = 'competition'
_marketId = 'marketId'
_event = 'event'
_id = 'id'
_eventType = 'eventType'
_name = 'name'
_sport = 'soccer'
_path_cookie = './cookies/orbitxch'

class Orbitxch:
    def __init__(self, username=None, password=None):
        self._username = username
        self._password = password
        self.token = self.get_token()

    def get_in_play_data(self):
        '''获取所有滚球markid, event_id'''
        url = 'https://www.orbitxch.com/customer/api/inplay/now'
        other_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Connection': 'keep-alive',
            'Referer': 'https://www.orbitxch.com/customer/inplay',
            'X-Rquested-With': 'MLttpRequest',            
        }
        headers = self.make_headers(other_headers)
        cookies = {
            'CSRF-TOKEN': self.token 
        }
        content = self.response(url, 'get', headers=headers, cookies=cookies)
        if content:
            inplay_data = json.loads(content)
            try:                
                marketCatalogueList = inplay_data[_marketCatalogueList]
                market_list = []
                events_params = ''
                for market in marketCatalogueList:
                    one_market = {}
                    if market[_eventType][_name].lower() == _sport:
                        one_market['market_id'] = market[_marketId]
                        one_market['event_id'] = market[_event][_id]
                        events_params += market[_event][_id] + ','
                        one_market['teams'] = market[_event][_name]
                        one_market['league'] = market[_competition][_name]
                        market_list.append(one_market)
                if events_params and market_list:
                    events_params = events_params[0:len(events_params)-1]
                    current_score_info_str = self.get_current_core(events_params)
                    if current_score_info_str:
                        current_score_info = json.loads(current_score_info_str) 
                        for mk_tmp in market_list:
                            for csi_tmp in current_score_info:
                                if mk_tmp['event_id'] == csi_tmp['eventId']:
                                    mk_tmp['home_name'] = csi_tmp['score']['home']['name']
                                    mk_tmp['away_name'] = csi_tmp['score']['away']['name']
                                    mk_tmp['home_score'] = csi_tmp['score']['home']['score']
                                    mk_tmp['away_score'] = csi_tmp['score']['away']['score']
                        return market_list
                    else:
                        return ''
                else:
                    return ''
            except Exception as err:
                print err
                return '' 
        else:
            return '' 

    def get_current_core(self, events_params):    
        '''获取当前比分'''
        url = 'https://www.orbitxch.com/customer/api/event-updates?eventIds=' + events_params
        other_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://www.orbitxch.com/customer/inplay',
            'X-Requested-With': 'XMLHttpRequest'
        }
        cookie_dict = {
            'CSRF-TOKEN': self.token
        }
        headers = self.make_headers(other_headers)
        score_info = self.response(url, 'get', headers=headers, cookies=cookie_dict)
        return score_info

    def get_data(self):
        '''获取所有的盘口数据'''
        in_play_data = self.get_in_play_data()
        if in_play_data:
            for ipd in in_play_data:
                event_id = ipd['event_id']
                market_id = ipd['market_id']
                koef_data = self.get_one_match_data(market_id, event_id)
                ipd['koef_data'] = koef_data
            return in_play_data
        else:
            return ''

    def get_one_match_data(self, market_id, event_id):
        '''获取该比赛所有对应盘口marketid,eventid'''
        url = 'https://www.orbitxch.com/customer/api/event/details/%s'%event_id
        other_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',            
            'Referer': 'https://www.orbitxch.com/customer/sport/market/%s'%market_id,
            'X-Requested-With': 'XMLHttpRequest'
        }
        cookie_dict = {
            'CSRF-TOKEN': self.token
        }
        headers = self.make_headers(other_headers)
        response = self.response(url, 'get', headers=headers, cookies=cookie_dict) 
        res_dict = json.loads(response)
        market_event = []
        market_all_info = []
        if res_dict:
            try:
                for k_tmp in res_dict['marketCatalogues']:
                    tmp1 = {}
                    tmp2 = {}
                    runners_name_list = []
                    tmp1['marketId'] = k_tmp['marketId']
                    tmp2['marketId'] = k_tmp['marketId']
                    tmp1['eventId'] = k_tmp['event']['id']
                    tmp2['eventId'] = k_tmp['event']['id']
                    market_event.append(tmp1)  
                    tmp2['marketName'] = k_tmp['marketName']
                    # print(k['marketName'])
                    for rn in k_tmp['runners']:
                        handicap_runner = {}
                        handicap_runner['runnerName'] = rn['runnerName']
                        handicap_runner['selectionId'] = rn['selectionId']
                        handicap_runner['handicap'] = rn['handicap']
                        runners_name_list.append(handicap_runner)
                        
                    tmp2['runners_name_list'] = runners_name_list
                    market_all_info.append(tmp2)
            except Exception as err:
                print err
                return ''
        else:
            return ''

        random_url_int = self.get_url_random_int()
        random_url_str = self.get_url_random_str()

        now_time1 = self.get_now_time()
        url1 = 'https://www.orbitxch.com/customer/ws/multiple-market-prices/%s/%s/xhr?t=%s'%(random_url_int, random_url_str, now_time1)
        other_headers1 = {
            'Accept': '*/*',
            'Content-Length': '0',
            'Referer': 'https://www.orbitxch.com/customer/sport/market/%s'%market_id,
        }
        headers1 = self.make_headers(other_headers1)
        self.response(url1, 'post', headers=headers1, cookies=cookie_dict)

        now_time2 = self.get_now_time()
        url2 = 'https://www.orbitxch.com/customer/ws/multiple-market-prices/%s/%s/xhr_send?t=%s'%(random_url_int, random_url_str, now_time2)
        market_event_info = json.dumps(market_event)
        market_event_info_list = []
        market_event_info_list.append(market_event_info)
        other_header2 = {
            'Accept': '*/*',            
            'Content-Length': str(len(market_event_info)),    
            'Content-type': 'text/plain',
            'Referer': 'https://www.orbitxch.com/customer/sport/market/%s'%market_id
        }
        headers2 = self.make_headers(other_header2)
        self.response(url2, 'post', headers=headers2, cookies=cookie_dict, json=market_event_info_list)

        now_time3 = self.get_now_time()
        url3 = 'https://www.orbitxch.com/customer/ws/multiple-market-prices/%s/%s/xhr?t=%s'%(random_url_int, random_url_str, now_time3)
        other_headers3 = {
            'Accept': '*/*',
            'Content-Length': '0',
            'Referer': 'https://www.orbitxch.com/customer/sport/market/%s'%market_id,
        }
        headers3 = self.make_headers(other_headers3)
        all_odds_info = self.response(url3, 'post', headers=headers3, cookies=cookie_dict)
        if all_odds_info:
            try:
                odds_info = all_odds_info[1:].split('\n')[0]
                odds_info = json.loads(odds_info)
                print(len(odds_info))

                for oi in odds_info:
                    odds = json.loads(oi)
                    for mai in market_all_info:
                        runners_list = []
                        if mai['marketId'] == odds['id']:
                            runners_info = odds['marketDefinition']['runners']
                            for run in runners_info: 
                                runners_dict = {}
                                runners_dict['id'] = run['id']
                                runners_dict['hc'] = run['hc']
                                runners_dict['status'] = run['status']
                                runners_list.append(runners_dict)
                            mai['runners_sort'] = runners_list
                            koef_list = []
                            rcs = odds['rc']
                            for rc in rcs:
                                koef_dict = {}
                                koef_dict['id'] = rc['id']
                                koef_dict['hc'] = rc['hc']
                                koef_dict['bdatb'] = rc['bdatb']
                                koef_dict['bdatl'] = rc['bdatl']
                                koef_list.append(koef_dict)
                            mai['koef_info'] = koef_list
                return market_all_info
            except Exception as err:
                print err
                return ''
        return ''

    def balance(self):
        '''获取账户余额'''
        url = 'https://www.orbitxch.com/customer/api/account/balance'
        other_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Referer': 'https://www.orbitxch.com/customer/',    
            'X-Requested-With': 'XMLHttpRequest'
        }
        headers = self.make_headers(other_headers)
        try:
            with open(_path_cookie , 'r') as f:
                cookies_str = f.read()
            if cookies_str:
                cookies = json.loads(cookies_str) 
            response = self.response(url, 'get', headers=headers, cookies=cookies)
            balance = json.loads(response)
            return balance
        except Exception as e:
            print e
            return ''

    def place_bet(self, market_id, selectionId, price, size, handicap='0', persistenceType='LAPSE', side='BACK'):
        '''
        进行投注
        price: 赔率
        selectionId:该盘口赔率标记
        side: 下注，或者受注 value(BACK 或者 LAY)
        size: 投注金额
        '''
        url = 'https://www.orbitxch.com/customer/api/placeBets'
        other_headers = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Content-Type': 'application/json;charset=UTF-8',
            'Referer': 'https://www.orbitxch.com/customer/sport/market/%s'%(str(market_id)),
            'X-CSRF-TOKEN': self.token,
            # 'X-CSRF-TOKEN': 'c2fa881c12f5b381e92f78f481086b2ab4',
            'X-Requested-With': 'XMLHttpRequest'
        }
        headers = self.make_headers(other_headers)
        form_data = {}
        current_bet = {
            'eachWayData': '{}',
            'handicap': handicap,
            'persistenceType': persistenceType,
            'price': price,
            'selectionId': selectionId,
            'side': side,
            'size': size             
        }
        one_match = []
        one_match.append(current_bet)
        form_data[market_id] = one_match
        try:
            with open(_path_cookie , 'r') as f:
                cookies_str = f.read()
            if cookies_str:
                cookies = json.loads(cookies_str)
            else:
                return ''
            response = self.response(url, 'post', headers=headers, json=form_data, cookies=cookies)
        except Exception as err:
            print 'place_bet', err
            return ''
        return response 

    def make_headers(self, other_headers):
        '''制作headers请求头信息'''
        headers = {}
        headers['Accept-Encoding'] = 'gzip, deflate, br'
        headers['Accept-Language'] = 'en-US,en;q=0.5'
        headers['Connection'] = 'keep-alive'
        headers['Host'] = 'www.orbitxch.com'
        headers['User-Agent'] = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
        headers['Origin'] = 'https://www.orbitxch.com'
        new_headers = dict(headers, **other_headers) 
        return new_headers

    def response(self, url, method, headers, cookies=None, formData=None, params=None, json=None):
        try:
            if method == 'post':
                response = requests.post(url, cookies=cookies, data=formData, json=json, headers=headers, timeout=10)
            else:
                response = requests.get(url, cookies=cookies, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.content
            else:
                print '请求状态码不是200!'
                return response.content 
        except Exception as error:
            print('is_success_request:', error)
            return '' 

    def get_token(self):
        '''获取csrf_token'''
        str_list = random.sample((string.digits + string.ascii_lowercase), 34)
        random_str = ''.join(str_list)
        return random_str

    def get_url_random_int(self):
        '''生成url里面随机的3位整数'''
        random_url_int_list = random.sample(string.digits, 3)
        random_url_int = ''.join(random_url_int_list)
        return random_url_int

    def get_url_random_str(self):
        '''生成url里面随机8位字符串'''
        random_url_str_list = random.sample((string.digits + string.ascii_lowercase), 8)
        random_url_str = ''.join(random_url_str_list)
        return random_url_str

    def get_now_time(self):
        '''获取11位时间戳字符串'''
        return str(int(time.time() * 1000))

    '''
    orbitxch登录
    '''

    def get_login_cookie(self):
        '''获取cookie'''
        with open(_path_cookie, 'rb') as f:
            cookies_str = f.read()
        try:
            if cookies_str:
                cookies = json.loads(cookies_str)
                if self.isLogin(cookies):
                    return cookies
                else:
                    return self.login_cookie()
            else:
                return self.login_cookie()
        except Exception as err:
            print 'get_cookie:', err
            return ''

    def login_cookie(self):
        '''用户登录获取cookie'''
        cookie_dict = {'CSRF-TOKEN': self.token}
        # 登录
        login_url = 'https://www.orbitxch.com/customer/api/login'
        other_headers = {
            'Accept': 'text/plain, */*; q=0.01',
            'Content-Length': '49',
            'Content-Type': 'application/json;charset=UTF-8',
            'Referer': 'https://www.orbitxch.com/customer/',
            'X-CSRF-TOKEN': self.token, 
            'X-Requested-With': 'XMLHttpRequest'
        }
        headers = self.make_headers(other_headers)
        print headers
        form_data = {
            'username': self._username,
            'password': self._password 
        }
        try:
            rp = requests.post(login_url, json=form_data, headers=headers, cookies=cookie_dict)
            login_cookie = dict(rp.cookies)
            if self.isLogin(login_cookie):
                with open(_path_cookie, 'wb') as f:
                    f.write(json.dumps(login_cookie))
                return login_cookie
            else:
                return ''
        except Exception as err:
            print 'login_cookie:', err
            return ''

    def isLogin(self, cookie_dict):
        '''判断用户是否登录'''
        if cookie_dict:
            cookie_dict['CSRF-TOKEN'] = self.token 
            url = 'https://www.orbitxch.com/customer/api/account/info'
            other_headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'Referer': 'https://www.orbitxch.com/customer/',
                'X-CSRF-TOKEN': self.token,
                'X-Requested-With': 'XMLHttpRequest'
            }
            headers = self.make_headers(other_headers)
            rp = requests.get(url, headers=headers, cookies=cookie_dict)
            html = rp.content
            user_info = json.loads(html)
            if 'username' in user_info:
                print 'username:',user_info['username']
                return True
            else:
                return False
        return False

if __name__ == '__main__':
　　username = ''
    password = ''
    ol = Orbitxch(username, password)
    # print ol.get_login_cookie()
    # print ol.get_token()
    # print ol.get_url_random_int()
    # print ol.get_url_random_str()
    # print ol.get_now_time()
    # print ol.get_in_play_data()
    # in_play_data = ol.get_data()
    # print in_play_data
    # print len(in_play_data)
    # print ol.balance()
    market_id = '1.146228500'
    selectionId = '1485568'
    price = 4.5 
    size = 10
    print ol.place_bet(market_id, selectionId, price, size)    
