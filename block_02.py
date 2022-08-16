# -*- coding: utf-8 -*-
import os
import subprocess
import re
import pickle

#console창 깨짐 방지
os.system('chcp 65001')
os.system('dir/w')

class block_internet:
    def __init__(self):
        #interface 정보 백업용 경로 생성
        self.backup_path = 'c:/net_info/'
        if not os.path.exists(self.backup_path):
            os.mkdir(self.backup_path)
        # Todo self.net_interface_dict는 향후 파일형태로 저장/관리 필요
        # 초기 interface정보 dict {interface번호: {ip: 1.1.1.1, mask: 255.255.255.0}, interface번호:{}...}
        self.net_interface_dict = {}
        self.loopback_interface_num = 1  # loopback interface num(보통 1번임)


        # 정보수집 및 복원용 명령어
        # interface 정보 덤프
        self.net_info_dump_cmd = f"netsh -c interface dump > {self.backup_path}net_info_backup.txt"
        # interface 정보 원복
        self.net_info_backup_cmd = f"netsh -f {self.backup_path}net_info_backup.txt"
        # interface 정보 확인
        self.net_interface_list_cmd = "netsh interface ipv4 show interface"
        # 라우팅 테이블 기반 loopback interface num 확인용
        self.route_table_status_cmd = "route print -4"

        self.ip_num = 1

    def set_cmd(self):
        # disable / enable 명령어

        # 1. inteface 비활성화
        self.adapter_disable_cmd = []
        self.adapter_enable_cmd = []
        for name, info in self.net_interface_dict.items():
            #disable_cmd
            tmp_cmd = f'netsh interface set interface {name} disable'
            self.adapter_disable_cmd.append(tmp_cmd)
            # enable_cmd
            tmp_cmd = f'netsh interface set interface {name} enable'
            self.adapter_enable_cmd.append(tmp_cmd)

        # 2. dns 변경
        self.dns_disable_cmd = []
        self.dns_enable_cmd = []
        for name, info in self.net_interface_dict.items():
            # disable_cmd
            tmp_cmd = f'netsh -c int ip set dns name={name} source=static addr=192.168.0.{self.ip_num} register=PRIMARY'
            self.dns_disable_cmd.append(tmp_cmd)

            # enable_cmd
            if 'dns1' in info.keys():
                if info['dns1'] != '0.0.0.0':
                    tmp_cmd = f'netsh -c int ip set dns name={name} source=static addr={info["dns1"]} register=PRIMARY'
                    self.dns_enable_cmd.append(tmp_cmd)
                if 'dns2' in info.keys():
                    tmp_cmd = f'netsh -c int ip add dns name={name} addr={info["dns2"]} index=2'
                    self.dns_enable_cmd.append(tmp_cmd)
            else:
                tmp_cmd = f'netsh -c int ip set dns name={name} source=dhcp'
                self.dns_enable_cmd.append(tmp_cmd)

        # 5. IP 변경
        self.ip_addr_disable_cmd = []
        self.ip_addr_enable_cmd = []
        for name, info in self.net_interface_dict.items():
            #disable_cmd
            if info["dhcp_enabled"] == 'No' and 'ipv4_address' not in info.keys():
                continue #ip가 수동 설정인데 ip정보가 안보이는 경우 변경 안함
            tmp_cmd = f'netsh interface ipv4 set address name={name} static 192.168.{self.ip_num}.1 255.255.255.0 192.168.{self.ip_num}.254'
            self.ip_addr_disable_cmd.append(tmp_cmd)
            self.ip_num += 1
            #enable_cmd
            if info['dhcp_enabled'] == 'No' and 'ipv4_address' in info.keys(): #기존IP설정이 수동일 경우
                # print(f"ip_addr_enable_cmd(info): {info}")
                tmp_cmd = f"netsh interface ipv4 set address name={name} static {info['ipv4_address']} {info['ipv4_mask']} {info['gw_address']}"
            else: #기존IP설정이 자동일 경우
                tmp_cmd = f"netsh interface ipv4 set address name={name} source=dhcp"
            self.ip_addr_enable_cmd.append(tmp_cmd)

        # 8. 라우팅 테이블
        self.route_table_disable_cmd = [
            f"netsh interface ipv4 set interface {self.loopback_interface_num} metric=1",
            f"route add 0.0.0.0 mask 128.0.0.0 10.10.10.10 metric 3 if {self.loopback_interface_num} -p",
            f"route add 128.0.0.0 mask 128.0.0.0 10.10.10.10 metric 3 if {self.loopback_interface_num} -p"
        ]
        self.route_table_enable_cmd = [
            f"netsh interface ipv4 set interface {self.loopback_interface_num} metric=auto",
            f"route delete 0.0.0.0 mask 128.0.0.0",
            f"route delete 128.0.0.0 mask 128.0.0.0"
        ]
    def save_def_net_info(self):
        # save data
        with open(f'{self.backup_path}def_net_info.txt', 'wb') as fw:
            pickle.dump(self.net_interface_dict, fw)

        # load data
        # with open('user.pickle', 'rb') as fr:
        #     user_loaded = pickle.load(fr)


    # network 설정정보 덤프
    def net_info_dump(self):
        print(f"[net_info_dump]")
        status_value = self.run_cmd(self.net_info_dump_cmd, True)

    # network 설정정보 원복
    def net_info_backup(self):
        print(f"[net_info_backup]")
        status_value = self.run_cmd(self.net_info_backup_cmd, True)

    # routing table 정보 기반 loopback num 확인
    def route_table_status(self):
        print("[route table status]")
        status_value = self.run_cmd(self.route_table_status_cmd)
        try:
            self.loopback_interface_num = re.search(r'(\d)\.{2,}Software Loopback Interface',status_value.stdout).group(1)
        except:
            self.loopback_interface_num = 1

    # interface 정보 확인
    def net_interface_info(self):
        print(f"[net_interface_info]")
        status_value = self.run_cmd(self.net_interface_list_cmd)

        try:
            int_wifi = re.compile(r'(\d+)[\s\d]+[\w]+[\s]+([wifWFI-]+)')
            int_eth = re.compile(r'(\d+)[\s\d]+[\w]+[\s]+(이더넷|Ethernet[\d\w\s]*)')
            for line in status_value.stdout.splitlines():
                wifi = int_wifi.search(line)
                eth = int_eth.search(line)
                if wifi:
                    # self.net_interface_dict[wifi.group(1)] = {'name': wifi.group(2)}
                    self.net_interface_dict[wifi.group(2)] = {'idx': wifi.group(1)}
                if eth:
                    # self.net_interface_dict[eth.group(1)] = {'name': eth.group(2)}
                    self.net_interface_dict[eth.group(2)] = {'idx': eth.group(1)}
        except:
            print('error')

        print("[ip_info]")
        try:
            dhcp_re = re.compile(r'DHCP enabled:[\s]+([\w]+)')
            ip_re = re.compile(r'IP Address:[\s]+(([\d]{1,3}\.){3}([\d]+))')
            mask_re = re.compile(r'Subnet Prefix:[\s]+[\d\.\/]+ \(mask (([\d]{1,3}\.){3}([\d]+))')
            gw_re = re.compile(r'Default Gateway:[\s]+(([\d]{1,3}\.){3}([\d]+))')
            dns_re = re.compile(r'Statically Configured DNS Servers:[\s]+(([\d]{1,3}\.){3}([\d]+))\n[\s]*(([\d]{1,3}\.){3}([\d]+))*')

            for name, idx in self.net_interface_dict.items():
                status_value = self.run_cmd(f"netsh interface ipv4 show config name={name}")
                tmp_dict = idx
                if dhcp_re.search(status_value.stdout):
                    tmp_dict['dhcp_enabled'] = dhcp_re.search(status_value.stdout).group(1)
                if ip_re.search(status_value.stdout):
                    tmp_dict['ipv4_address'] = ip_re.search(status_value.stdout).group(1)
                if mask_re.search(status_value.stdout):
                    tmp_dict['ipv4_mask'] = mask_re.search(status_value.stdout).group(1)
                if gw_re.search(status_value.stdout):
                    tmp_dict['gw_address'] = gw_re.search(status_value.stdout).group(1)
                if dns_re.search(status_value.stdout):
                    tmp_dict['dns1'] = dns_re.search(status_value.stdout).group(1)
                    if dns_re.search(status_value.stdout).group(4):
                        tmp_dict['dns2'] = dns_re.search(status_value.stdout).group(4)
                self.net_interface_dict[name] = tmp_dict

            for k,v in self.net_interface_dict.items():
                print(f"{k}=> {v}")
        except:
            print("[ip_info] error")
    
    #netsh 명령어 실행 함수
    def run_cmd(self, cmd_str, shell_flag=False):
        result = subprocess.run(cmd_str.split(' '),
                       capture_output=True, shell=shell_flag, encoding='utf8')
        print(f"실행결과 코드: {result.returncode} | 명령어: {cmd_str}")
        if result.returncode != 0:
            print(f"에러코드: {result.stderr}")
        return result

    #1. 어댑터 비활성화
    def adapter_disable(self):
        print("[adapter_disable]")
        for cmd in self.adapter_disable_cmd:
            disable_value = self.run_cmd(cmd)

    def adapter_enable(self):
        print("[adapter_enable]")
        for cmd in self.adapter_enable_cmd:
            disable_value = self.run_cmd(cmd)

    #2. dns 변경
    def dns_disable(self):
        print("[dns_disable]")
        for cmd in self.dns_disable_cmd:
            disable_value = self.run_cmd(cmd)

    def dns_enable(self):
        print("[dns_enable]")
        for cmd in self.dns_enable_cmd:
            enable_value = self.run_cmd(cmd)

    #5. IP변경
    def ip_addr_disable(self):
        print("[ip_addr_disable]")
        for cmd in self.ip_addr_disable_cmd:
            disable_value = self.run_cmd(cmd)

    def ip_addr_enable(self):
        print("[ip_addr_enable]")
        for cmd in self.ip_addr_enable_cmd:
            enable_value = self.run_cmd(cmd)

    #8. 라우팅 테이블 관련
    def route_table_disable(self):
        print("[route table disable]")
        for cmd in self.route_table_disable_cmd:
            disable_value = self.run_cmd(cmd)

    def route_table_enable(self):
        print("[route table enable]")
        for cmd in self.route_table_enable_cmd:
            enable_value = self.run_cmd(cmd)


if __name__ == "__main__":
    print("*"*80)
    print("Start Network enable or disable!!")

    pc1 = block_internet()
    
    pc1.net_info_dump()
    pc1.net_interface_info()
    pc1.route_table_status()

    #Todo self.net_interface_dict 파일 저장 함수 호출
    pc1.save_def_net_info()

    #기본 정보를 바탕으로 명령어 세팅
    pc1.set_cmd()

    while(True):
        try:
            print("1. 차단시행 | 2. 차단해지 | 3. 종료")
            num = int(input("번호입력: "))
        except Exception as e:
            print("메뉴 번호를 입력하세요")
        if num == 1:
            pc1.route_table_disable()
            pc1.ip_addr_disable()
            pc1.dns_disable()
            pc1.adapter_disable()
        elif num == 2:
            pc1.route_table_enable()
            pc1.ip_addr_enable()
            pc1.dns_enable()
            pc1.adapter_enable()
            pc1.net_info_backup()
        elif num == 3:
            print("종료")
            break
        else:
            print('다시 입력하세요')

    print("*" * 80)
