# -*- coding: utf-8 -*-
import os
import subprocess
import re

#console창 깨짐 방지
os.system('chcp 65001')
os.system('dir/w')

#8:라우팅 테이블 이용
class route_table:
    def __init__(self):
        self.status_cmd = "route print -4"
        self.disable_cmd = [
            "netsh interface ipv4 set interface 1 metric=1",
            "route add 0.0.0.0 mask 128.0.0.0 10.10.10.10 metric 3 if 1 -p",
            "route add 128.0.0.0 mask 128.0.0.0 10.10.10.10 metric 3 if 1 -p"
        ]
        self.able_cmd = [
            "netsh interface ipv4 set interface 1 metric=auto",
            "route delete 0.0.0.0 mask 128.0.0.0",
            "route delete 128.0.0.0 mask 128.0.0.0"
        ]

        self.status_value = subprocess.run(self.status_cmd.split(' '), capture_output=True, shell=False, encoding='utf8')
        self.loopback_interface_num = re.search(r'(\d)\.{2,}Software Loopback Interface',self.status_value.stdout).group(1)

    def show_status(self):
        status_value = subprocess.run(self.status_cmd.split(' '), capture_output=True, shell=False, encoding='utf8')
        print(f"실행결과 코드: {status_value.returncode}")
        if status_value.returncode != 0:
            print(f"에러코드: {status_value.stderr}")
        # print(f"출력물{type(self.status_value.stdout)}: {self.status_value.stdout}")
        print("+"*60)

    def route_table_disable(self):
        for d_cmd in self.disable_cmd:
            disable_value = subprocess.run(d_cmd.split(' '),
                                                capture_output=True, shell=False,encoding='utf8')
            print(f"실행결과 코드: {disable_value.returncode}")
            if disable_value.returncode != 0:
                print(f"에러코드: {disable_value.stderr}")
            print(f"출력물{type(disable_value.stdout)}: {disable_value.stdout}")

    def route_table_able(self):
        for d_cmd in self.able_cmd:
            disable_value = subprocess.run(d_cmd.split(' '),
                                                capture_output=True, shell=False,encoding='utf8')
            print(f"실행결과 코드: {disable_value.returncode}")
            if disable_value.returncode != 0:
                print(f"에러코드: {disable_value.stderr}")
            print(f"출력물{type(disable_value.stdout)}: {disable_value.stdout}")



    #enable

    #disable

    #staus check

if __name__ == "__main__":
    print("Start Network enable or disable!!")

    pc_1 = route_table()
    pc_1.show_status()
    # pc_1.route_table_disable()
    pc_1.route_table_able()

