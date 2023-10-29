from django.shortcuts import render
from msgapp.models import CloudMsg
from datetime import datetime
import json
import requests
from requests.auth import HTTPBasicAuth
import time
import re

# Create your views here.

z1 = ''
list = []
class GetNodes:
    def __init__(self, ip):
        self.ip = ip

    def get_switch_id(self):
        url = 'http://' + self.ip + '/stats/switches'
        re_switch_id = requests.get(url=url).json()
        switch_id_hex = []
        for i in re_switch_id:
            switch_id_hex.append(hex(i))

        return switch_id_hex

    def getflow(self):
        url = 'http://' + self.ip + '/stats/flow/%d'
        switch_list = self.get_switch_id()
        ret_flow = []
        for switch in switch_list:
            new_url = format(url % int(switch, 16))
            re_switch_flow = requests.get(url=new_url).json()
            ret_flow.append(re_switch_flow)
        return ret_flow

    def show(self):
        global list
        flow_list = self.getflow()
        for flow in flow_list:
            for dpid in flow.keys():
                dp_id = dpid
                switchnum = '{1}'.format(hex(int(dp_id)), int(dp_id))
                print('s' + switchnum, end=" ")
                list.append('s' + switchnum)
                switchnum = int(switchnum)
            for list_table in flow.values():
                for table in list_table:
                    string1 = str(table)
                    if re.search("'dl_vlan': '(.*?)'", string1) is not None:
                        num = re.search("'dl_vlan': '(.*?)'", string1).group(1);
                        if num == '0' and switchnum == 1:
                            print('h1', end=" ")
                            list.append('h1')
                        if num == '1' and switchnum == 1:
                            print('h2', end=" ")
                            list.append('h2')
                        if num == '0' and switchnum == 2:
                            print('h3', end=" ")
                            list.append('h3')
                        if num == '1' and switchnum == 2:
                            print('h4', end=" ")
                            list.append('h4')
        print('s1<->s2')
        list.append('s1<->s2')
        print('s1<->h1')
        list.append('s1<->h1')
        print('s1<->h2')
        list.append('s1<->h2')
        print('s2<->h3')
        list.append('s2<->h3')
        print('s2<->h4')
        list.append('s2<->h4')
        flow_list = self.getflow()
        for flow in flow_list:
            for dpid in flow.keys():
                dp_id = dpid
                print('switch_name:s{1}'.format(hex(int(dp_id)), int(dp_id)))
                list.append('switch_name:s{1}'.format(hex(int(dp_id)), int(dp_id)))
            for list_table in flow.values():
                for table in list_table:
                    print(table)
                    list.append(table)

def msgsolve(request):
    content={}
    if request.method=='POST':
        cloudmsg=CloudMsg()
        cloudmsg.userA=request.POST.get("userA",None)
        cloudmsg.userB=request.POST.get("userB",None)
        cloudmsg.msg=request.POST.get("msg",None)
        cloudmsg.time=datetime.now().date()
        cloudmsg.save()
        if cloudmsg.userB == '6':
            global list
            list.clear()
            s1 = GetNodes("127.0.0.1:8080")
            s1.show()
            content["list"] = list
        if cloudmsg.userB == '5':
            url = 'http://127.0.0.1:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:1/flow-node-inventory:table/0/flow/1'
            with open("/home/ubuntu/PycharmProjects/pythonProject/xiaochengxu/msgapp/timeout.json") as file:
                str = file.read()
            headers = {'Content-Type': 'application/json'}
            res = requests.put(url, str, headers=headers, auth=HTTPBasicAuth('admin', 'admin'))
            print(res.content)
        if cloudmsg.userB == '4':
            url = 'http://127.0.0.1:8181/restconf/operational/opendaylight-inventory:nodes/node/openflow:1/' \
                  'flow-node-inventory:table/0/opendaylight-flow-table-statistics:flow-table-statistics'
            headers = {'Content-Type': 'application/json'}
            response = requests.get(url=url, headers=headers, auth=HTTPBasicAuth('admin', 'admin'))
            print(response.content)
            x = response.content
            content["x"] = x
        if cloudmsg.userB == '3':
            url = 'http://127.0.0.1:8181/restconf/operational/opendaylight-inventory:nodes/node/openflow:1/'
            headers = {'Content-Type': 'application/json'}
            response = requests.delete(url=url, headers=headers, auth=HTTPBasicAuth('admin', 'admin'))
            print(response.content)
            x=response.content
            content["x"] = x
        if cloudmsg.userB == '2':
            url = 'http://127.0.0.1:8080/stats/flowentry/add'
            with open("/home/ubuntu/PycharmProjects/pythonProject/xiaochengxu/msgapp/ryu_timeout.json") as file:
                str = file.read()
            headers = {'Content-Type': 'application/json'}
            res = requests.post(url, str, headers=headers)
            print(res.content)
        if cloudmsg.userB == '1':
            url = 'http://127.0.0.1:8080/stats/flowentry/add'
            headers = {'Content-Type': 'application/json'}
            flow1 = {
                "dpid": 1,
                "priority": 1,
                "match": {
                    "in_port": 1
                },
                "actions": [
                    {
                        "type": "PUSH_VLAN",
                        "ethertype": 33024
                    },
                    {
                        "type": "SET_FIELD",
                        "field": "vlan_vid",
                        "value": 4096
                    },
                    {
                        "type": "OUTPUT",
                        "port": 3
                    }
                ]
            }
            flow2 = {
                "dpid": 1,
                "priority": 1,
                "match": {
                    "in_port": 2
                },
                "actions": [
                    {
                        "type": "PUSH_VLAN",
                        "ethertype": 33024
                    },
                    {
                        "type": "SET_FIELD",
                        "field": "vlan_vid",
                        "value": 4097
                    },
                    {
                        "type": "OUTPUT",
                        "port": 3
                    }
                ]
            }
            flow3 = {
                "dpid": 1,
                "priority": 1,
                "match": {
                    "vlan_vid": 0
                },
                "actions": [
                    {
                        "type": "POP_VLAN",
                        "ethertype": 33024
                    },
                    {
                        "type": "OUTPUT",
                        "port": 1
                    }
                ]
            }
            flow4 = {
                "dpid": 1,
                "priority": 1,
                "match": {
                    "vlan_vid": 1
                },
                "actions": [
                    {
                        "type": "POP_VLAN",
                        "ethertype": 33024
                    },
                    {
                        "type": "OUTPUT",
                        "port": 2
                    }
                ]
            }
            flow5 = {
                "dpid": 2,
                "priority": 1,
                "match": {
                    "in_port": 1
                },
                "actions": [
                    {
                        "type": "PUSH_VLAN",
                        "ethertype": 33024
                    },
                    {
                        "type": "SET_FIELD",
                        "field": "vlan_vid",
                        "value": 4096
                    },
                    {
                        "type": "OUTPUT",
                        "port": 3
                    }
                ]
            }
            flow6 = {
                "dpid": 2,
                "priority": 1,
                "match": {
                    "in_port": 2
                },
                "actions": [
                    {
                        "type": "PUSH_VLAN",
                        "ethertype": 33024
                    },
                    {
                        "type": "SET_FIELD",
                        "field": "vlan_vid",
                        "value": 4097
                    },
                    {
                        "type": "OUTPUT",
                        "port": 3
                    }
                ]
            }
            flow7 = {
                "dpid": 2,
                "priority": 1,
                "match": {
                    "vlan_vid": 0
                },
                "actions": [
                    {
                        "type": "POP_VLAN",
                        "ethertype": 33024
                    },
                    {
                        "type": "OUTPUT",
                        "port": 1
                    }
                ]
            }
            flow8 = {
                "dpid": 2,
                "priority": 1,
                "match": {
                    "vlan_vid": 1
                },
                "actions": [
                    {
                        "type": "POP_VLAN",
                        "ethertype": 33024
                    },
                    {
                        "type": "OUTPUT",
                        "port": 2
                    }
                ]
            }
            res1 = requests.post(url, json.dumps(flow1), headers=headers)
            res2 = requests.post(url, json.dumps(flow2), headers=headers)
            res3 = requests.post(url, json.dumps(flow3), headers=headers)
            res4 = requests.post(url, json.dumps(flow4), headers=headers)
            res5 = requests.post(url, json.dumps(flow5), headers=headers)
            res6 = requests.post(url, json.dumps(flow6), headers=headers)
            res7 = requests.post(url, json.dumps(flow7), headers=headers)
            res8 = requests.post(url, json.dumps(flow8), headers=headers)
    if request.method=='GET':
        userC=request.GET.get('userC',None)
        if userC==''or userC:
            msg=CloudMsg.objects.all()
            data=msg.filter(userB__contains=userC)
            print(data)
            if len(data)>10:
                data=data[:10]
            content["data"]=data
    return render(request,'g.html',content)
