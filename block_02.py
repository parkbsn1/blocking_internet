# -*- coding: utf-8 -*-
import os
import subprocess
import re

#console창 깨짐 방지
os.system('chcp 65001')
os.system('dir/w')

class block_internet:
    def __init__(self):
        #기본 명령어 세팅
        #interface 정보 백업
        self.backup_path = 'c:/net_info/'
        if not os.path.exists(self.backup_path):
            os.mkdir(self.backup_path)
        self.net_info_backup_cmd = f"netsh -c interface dump > {self.backup_path}net_info_backup.txt"
        #interface 정보 확인
        self.net_interface_list_cmd = "netsh interface ipv4 show interface"
        self.net_interface_dict = {}
        #1
        #2

        #3
        #4
        #5
        #6
        #7
        #8 라우팅 테이블
        self.route_table_status_cmd = "route print -4"
        self.loopback_interface_num = 1 #loopback interface num
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

    # loopback interface 번호 조회
    def loopback_info(self, status_value):
        try:
            self.loopback_interface_num = re.search(r'(\d)\.{2,}Software Loopback Interface',status_value.stdout).group(1)
        except:
            # loopback interface 번호 보통 1번(추측)
            self.loopback_interface_num = 1

    def net_interface_info(self):
        status_value = self.run_cmd(self.net_interface_list_cmd)
        print(f"실행결과 코드: {status_value.returncode}")
        if status_value.returncode != 0:
            print(f"에러코드: {status_value.stderr}")
        try:
            int_wifi = re.compile(r'(\d+)[\s\d]+[\w]+[\s]+([wifWFI-]+)')
            int_eth = re.compile(r'(\d+)[\s\d]+[\w]+[\s]+(이더넷|Ethernet[\d\w\s]*)')
            for line in status_value.stdout.splitlines():
                w = int_wifi.search(line)
                e = int_eth.search(line)
                if w:
                    self.net_interface_dict[w.group(1)] = {'name': w.group(2)}
                if e:
                    self.net_interface_dict[e.group(1)] = {'name': e.group(2)}
        except:
            print('error')

    def ip_info(self):
        print("[ip_info]")
        for idx, v in self.net_interface_dict.items():
            status_value = self.run_cmd(f"netsh interface ipv4 show config name={idx}")
            # print(status_value.stdout)
            print("^"*50)
            for s in status_value.stdout.splitlines():
                tmp = list(set(s.split(' ')))
                if len(tmp) <= 1: continue
                del tmp[0]
                print(tmp)

            print("^" * 50)

    #8 라우팅 테이블 관련
    def route_table_status(self):
        print("[route table status]")
        status_value = self.run_cmd(self.route_table_status_cmd)
        self.loopback_info(status_value)
        print(f"실행결과 코드: {status_value.returncode}")
        if status_value.returncode != 0:
            print(f"에러코드: {status_value.stderr}")

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

    def run_cmd(self, cmd_str, shell_flag=False):
        result = subprocess.run(cmd_str.split(' '),
                       capture_output=True, shell=shell_flag, encoding='utf8')
        return result



    #enable

    #disable

    #staus check

if __name__ == "__main__":
    print("*"*80)
    print("Start Network enable or disable!!")

    pc1 = block_internet()
    pc1.net_info_backup()
    pc1.net_interface_info()
    pc1.ip_info()

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
