import requests
import hmac, hashlib
import re
import time

class Router:

    def __init__(self):
        self.ip = '10.100.102.1'

        self.username = 'home'
        self.password ='Home013'

        self.login_url = f'http://{self.ip}/ui/login'
        self.reboot_url = f'http://{self.ip}/ui/dboard/system/reboot?backto=system'
        self.reboot_action_url = f'http://{self.ip}/ui/dboard/system/reboot/action'

        self.get_ip_url = 'https://api.ipify.org/?format=text'
        

        self.re1='.input type=.hidden. name=.nonce. value=[\'\"]([^\'\"]+). ..'
        self.re2='.input type=.hidden. name=.code1. value=[\'\"]([^\'\"]+). ..'
        self.re3='.input type=.hidden. name=.code2. value=[\'\"]([^\'\"]+). ..'

        self.re4='.input type=.hidden. name=.action__key. value=[\'\"]([^\'\"]+). ..'

        self.session = None

    def get_session(self):
        if self.session is None:
            self.session = requests.session()
        return self.session


    def login(self):
        print('Navigating to login page')
        r = self.get_session().get(self.login_url)
        t = r.text

        f1 = re.findall(self.re1, t)
        f2 = re.findall(self.re2, t)
        f3 = re.findall(self.re3, t)

        nonce = f1[0]
        code1 = f2[0]
        code2 = f3[0]
        r = hmac.HMAC(nonce.encode('utf-8'), self.password.encode('utf-8'), digestmod=hashlib.sha256)
        r = r.hexdigest()

        print(f'Username {self.username}, Nonce {nonce}, Code1 {code1}, Code2 {code2}, Password {r}')

        d = {'userName':self.username, 'origUserPwdShow':'on', 'language': 'EN', 'login': 'Login', 'userPwd': r, 'nonce': nonce, 'code1': code1, 'code2': code2}
        r = self.get_session().post(self.login_url, data=d)
        print('Logged in')

    def reboot(self):
        print('Navigating to reboot page')
        r = self.get_session().get(self.reboot_url)
        t = r.text
        f4 = re.findall(self.re4, t)
        action_key = f4[0]
        print(f'Action key {action_key}, rebooting')

        r = self.get_session().post(self.reboot_action_url, data={'delay': '0', 'action__key':action_key, 'reboot': 'Reboot'})
        print('Sent!')
        
    def get_ip(self):
        return requests.get(self.get_ip_url, timeout=3).text
    
    def safe_get_ip(self):
        try:
            return self.get_ip()
        except:
            return None
    
    def wait_for_new_ip(self):
        start = time.time()        
        timeout = 10*60 # ten minutes
        retry_every = 10 # ten seconds
        end_time = start + timeout        
        while time.time() < end_time:
            time.sleep(10)
            new_ip = self.safe_get_ip()
            if new_ip is None:
                print('No ip yet')
                continue
            
            else:
                elapsed = time.time() - start
                print(f'New ip is {new_ip}, took {round(elapsed, 2)} seconds')
                return new_ip


    

    def all(self):
        start = time.time()
        ip1 = self.get_ip()
        print(f'Current IP is {ip1}, restarting')
        self.login()
        self.reboot()
        ip2 = self.wait_for_new_ip()
        elapsed = round(time.time() - start, 2)
        print(f'Took {elapsed} seconds to change ip from {ip1} to {ip2}')


def main():
    r = Router()
    r.all()

if __name__=='__main__':
    main()
