# -*- coding: utf-8 -*-
import os
import subprocess
import re

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

        self.set_cmd()

    def set_cmd(self):
        # ------------------------------------------------------------------------------------
        # 정보수집 및 복원용 명령어

        #interface 정보 백업
        self.net_info_backup_cmd = f"netsh -c interface dump > {self.backup_path}net_info_backup.txt"
        # interface 정보 확인
        self.net_interface_list_cmd = "netsh interface ipv4 show interface"
        # 라우팅 테이블 기반 loopback interface num 확인용
        self.route_table_status_cmd = "route print -4"

        #------------------------------------------------------------------------------------
        # disable / enable 명령어

        # 8 라우팅 테이블
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

    # network 설정정보 백업
    def net_info_backup(self):
        print(f"[net_info_backup]: {self.net_info_backup_cmd}")
        status_value = self.run_cmd(self.net_info_backup_cmd, True)
        print(f"실행결과 코드: {status_value.returncode}")
        if status_value.returncode != 0:
            print(f"에러코드: {status_value.stderr}")

    # routing table 정보 기반 loopback num 확인
    def route_table_status(self):
        print("[route table status]")
        status_value = self.run_cmd(self.route_table_status_cmd)
        try:
            self.loopback_interface_num = re.search(r'(\d)\.{2,}Software Loopback Interface',status_value.stdout).group(1)
        except:
            self.loopback_interface_num = 1
        print(f"실행결과 코드: {status_value.returncode}")
        if status_value.returncode != 0:
            print(f"에러코드: {status_value.stderr}")       

    # interface 정보 확인
    def net_interface_info(self):
        status_value = self.run_cmd(self.net_interface_list_cmd)
        print(f"실행결과 코드: {status_value.returncode}")
        if status_value.returncode != 0:
            print(f"에러코드: {status_value.stderr}")
        try:
            int_wifi = re.compile(r'(\d+)[\s\d]+[\w]+[\s]+([wifWFI-]+)')
            int_eth = re.compile(r'(\d+)[\s\d]+[\w]+[\s]+(이더넷|Ethernet[\d\w\s]*)')
            for line in status_value.stdout.splitlines():
                wifi = int_wifi.search(line)
                eth = int_eth.search(line)
                if wifi:
                    self.net_interface_dict[wifi.group(1)] = {'name': wifi.group(2)}
                if eth:
                    self.net_interface_dict[eth.group(1)] = {'name': eth.group(2)}
        except:
            print('error')

        print("[ip_info]")
        try:
            dhcp_flag = re.compile(r'DHCP enabled:[\s]+([\w]+) ')
            ip_addr = re.compile(r'IP Address:[\s]+(([\d]{1,3}\.){3}([\d]+))')
            mask = re.compile(r'Subnet Prefix:[\s]+[\d\.\/]+ \(mask (([\d]{1,3}\.){3}([\d]+))')
            gw_addr = re.compile(r'Default Gateway:[\s]+(([\d]{1,3}\.){3}([\d]+))')
            dns_addr = re.compile(r'Statically Configured DNS Servers:[\s]+(([\d]{1,3}\.){3}([\d]+))\n[\s]*(([\d]{1,3}\.){3}([\d]+))* ')

            for idx, name in self.net_interface_dict.items():
                status_value = self.run_cmd(f"netsh interface ipv4 show config name={idx}")
                print("#"*50)
                tmp_dict = name

                # result = dhch_flag.search(status_value.stdout)
                # if result:
                #     tmp_dict['dhch'] = result.group(1)
                if dhcp_flag.search(status_value.stdout):
                    tmp_dict['dhcp'] = dhcp_flag.search(status_value.stdout).group(1)
                if ip_addr.search(status_value.stdout):
                    tmp_dict['ip_addr'] = ip_addr.search(status_value.stdout).group(1)

                print(tmp_dict)
                # for s in status_value.stdout.splitlines():
                #     tmp = list((s.split(' ')))
                #     if len(tmp) <= 1: continue
                #     tmp = [i.replace('"','') for i in tmp if i not in ['']]
                #     print(s)
                #     tmp_dict[tmp[0]] = tmp[-1]

                print("#" * 50)
        except:
            print("[ip_info] error")
    
    #netsh 명령어 실행 함수
    def run_cmd(self, cmd_str, shell_flag=False):
        result = subprocess.run(cmd_str.split(' '),
                       capture_output=True, shell=shell_flag, encoding='utf8')
        return result

    


    # 8 라우팅 테이블 관련
    def route_table_disable(self):
        print("[route table disable]")
        for d_cmd in self.route_table_disable_cmd:
            disable_value = self.run_cmd(d_cmd)
            print(f"실행결과 코드: {disable_value.returncode}")
            if disable_value.returncode != 0:
                print(f"에러코드: {disable_value.stderr}")

    def route_table_enable(self):
        print("[route table enable]")
        for d_cmd in self.route_table_enable_cmd:
            enable_value = self.run_cmd(d_cmd)
            print(f"실행결과 코드: {enable_value.returncode}")
            if enable_value.returncode != 0:
                print(f"에러코드: {enable_value.stderr}")

    

if __name__ == "__main__":
    print("*"*80)
    print("Start Network enable or disable!!")

    pc1 = block_internet()
    
    pc1.net_info_backup()
    pc1.net_interface_info()
    pc1.route_table_status()

    while(True):
        try:
            print("1. 차단시행 | 2. 차단해지 | 3. 종료")
            num = int(input("번호입력: "))
        except Exception as e:
            print("메뉴 번호를 입력하세요")
        if num == 1:
            pc1.route_table_disable()
        elif num == 2:
            pc1.route_table_enable()
        elif num == 3:
            print("종료")
            break
        else:
            print('다시 입력하세요')

    print("*" * 80)
