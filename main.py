import json
import os

import paramiko
import requests
from flask import Flask,redirect

from utils.utils import fprint, Cp, get_logs, thread_runner, hyp_loader, check_if_get_ok, string_to_contract

hyp = hyp_loader('E:/Programming/Python/NFT/DNFT-Server/hyper-parameters.yaml')


def print_client_out(outs):
    fprint(outs[1].read().decode())


def runcommand(client_server, command):
    return client_server.exec_command(command)


def connect(hostname, username, password, port: int = 22):
    client_server = paramiko.client.SSHClient()
    client_server.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client_server.connect(hostname, username=username, password=password, port=port)
    return client_server


app = Flask(__name__)


def init(cpath: str = 'Dynamic-NFT'):
    if not os.getcwd().endswith(cpath):
        fprint('INIT RUNNING ...\n')
        current: str = os.getcwd()
        goto: str = os.path.join(current, cpath)
        fprint('CURRENT : ', current)
        fprint('APPENDING TO PATH : ', goto)
        os.chdir(goto)
        if not os.path.exists('accounts'):
            os.mkdir('accounts')
        else:
            fprint('{:<15}{}'.format('', "--**--  ACCOUNTS FILE ALREADY EXIST IGNORING CREATION  --**--"), color=Cp.red)
        if not os.path.exists(os.path.join(goto, 'node_modules')):
            fprint('ADDING NEW TASK TO THREAD TO INSTALL NODE MODULES ...', color=Cp.blue)
            thread_runner(get_logs, ('npm i ',))
        else:
            fprint('{:<15}{}'.format('', 'NODE MODULES EXISTS IGNORE INSTALLATION PROCESS ...'), color=Cp.blue)
    else:
        fprint('{:<15}{}'.format('', "--**--      IGNORE INIT FUNCTION      --**--"), color=Cp.red)


@app.route('/')
def main():
    return 'this is main page lad get out!'


@app.route('/<hash_key>/<name>/<level>')
def stage_one(hash_key, name, level):
    lines = [
        "const DN = artifacts.require('DynamicNFT')\n",
        f"const HASH_CASH = '{hash_key}'\n",
        f'const uri = "https://dynamicnft.metavers.ae/Dynamic-NFT/accounts/metadata-{hash_key}.json"\n',
        "module.exports = async (deployer, network, [defaultAccount]) => { \n",
        '   deployer.deploy(DN,HASH_CASH,uri) \n',
        '   let dnd = await DN.deployed() \n',
        "}"

    ]
    with open('migrations/2_DynamicNFT.js', 'w') as w:
        w.writelines(lines)
    if hyp['on_client_server'] == 'True':
        if not check_if_get_ok(requests.get(hyp['url_jsons'] + f'{hash_key}.json')):
            # try:
            log: str = get_logs('truffle migrate DynamicNFT --network matic -f 2')

            fprint(f'log : {log}')
            contract = string_to_contract(log)
            contract = contract.replace('\n', '')
            # contract = '0xsadjkowiej91u98AOISJI09u21093i90fake'
            qr_string = f'https://testnets.opensea.io/assets/mumbai/{contract}/0'.replace(' ', '')
            data = f'&"wallet_address": "{hash_key}","name": "{name}","contract_address": "{contract}","level": "{level}"='
            data = data.replace('&', '{').replace('=', '}')
            meta_data = f'&"name": "{name}", "description": "{hash_key}", "image": "https://www.halaholidays.com/nft/{level}.png"='
            meta_data = meta_data.replace('&', '{').replace('=', '}')
            qr_save_path = hyp['qr_save_path']
            json_save_path = hyp['json_save_path']
            run_cmd_hash_key = f'python3 json_parser.py --name "{hash_key}" --data "{data}"'
            run_cmd_meta_data_hash_key = f'python3 json_parser.py --name "metadata-{hash_key}" --data "{meta_data}"'
            command_0 = f'cd {hyp["cd_path"]} && python3 json_metadata.py --name "metadata-{hash_key}" --data "{meta_data}" --save "{json_save_path}"'

            command_1 = f'cd {hyp["cd_path"]} && python3 json_contract.py --name "{hash_key}" --data "{data}" --save "{json_save_path}"'
            command_2 = f'cd {hyp["cd_path"]} && python3 qr_code.py --name "{hash_key}.png" --url "{qr_string}" --save "{qr_save_path}"'
            client = connect(hyp['hostname_login'], hyp['username_login'], hyp['password_login'], hyp['port_login'])
            fprint(command_0)
            fprint(command_1)
            fprint(command_2)
            out_0 = runcommand(client,
                               command=command_0
                               )
            out_1 = runcommand(client,
                               command=command_1
                               )
            out_2 = runcommand(client,
                               command=command_2
                               )
            # print_client_out(out_0)
            # print_client_out(out_1)
            # for i, s in enumerate(['OUT', 'ERR']):
            #     fprint(f'{s} : {out_2[i+1].read().decode()}')
            # print_client_out(out_2)
            # return {'status': True, 'contract_address': contract, "level": level,
            #         'log': 'Account is Created', 'qr_code': f'{hyp["qr_path"]}{hash_key}.png'}
            return redirect(f'{hyp["qr_path"]}{hash_key}.png')
            # except:
            #     return {'status': False, 'contract_address': None, "level": level,
            #             'log': "Network Can't Reach Blockchain "}
        else:
            req_to = hyp['url_jsons'] + f'{hash_key}.json'
            fprint(req_to)
            dt = json.loads(requests.get(req_to).text.replace("'", '"'))
            fprint(dt)
            return {'status': False, 'contract_address': dt["contract_address"], "level": dt["level"],
                    'log': 'Account is Already Exists', 'qr_code': f'{hyp["qr_path"]}/{hash_key}.png'}

    else:
        if not os.path.exists(f'accounts/{hash_key}.json'):
            log: str = get_logs('truffle migrate DynamicNFT --network matic -f 2')
            fprint(f'log : {log}')
            contract = string_to_contract(log)
            contract = contract.replace(r'\n', '')

            data = {
                'wallet_address': f'{hash_key}',
                'name': f'{name}',
                'contract_address': f'{contract}',
                'level': f"{level}"
            }
            meta_data = {
                'name': f'{name}',
                'description': f'{hash_key}',
                'image': f"https://www.halaholidays.com/nft/{level}.png"
            }

            with open(f'accounts/{hash_key}.json', 'w') as w:
                json.dump(data, w)
            with open(f'accounts/metadata-{hash_key}.json', 'w') as w:
                json.dump(meta_data, w)
            return {'status': True, 'contract_address': contract, "level": level,
                    'log': 'Account is Created'}

        else:
            with open(f'accounts/{hash_key}.json', 'r') as r:
                dt = json.load(r)
            return {'status': False, 'contract_address': dt["contract_address"], "level": dt["level"],
                    'log': 'Account is Already Exists'}


@app.route('/getpath')
def getpath():
    return {'path': os.getcwd()}


@app.route('/levelup/<hash_key>/<level>')
def level_up(hash_key, level):
    req = requests.get(hyp['url_jsons'] + f"metadata-{hash_key}.json")
    if check_if_get_ok(req):
        jd = json.loads(req.text.replace("'", '"'))
        qr_save_path = hyp['qr_save_path']
        json_save_path = hyp['json_save_path']
        client = connect(hyp['hostname_login'], hyp['username_login'], hyp['password_login'], hyp['port_login'])
        name = jd['name']
        meta_data = f'&"name": "{name}", "description": "{hash_key}", "image": "https://www.halaholidays.com/nft/{level}.png"='
        meta_data = meta_data.replace('&', '{').replace('=', '}')
        out = runcommand(client,
                         f'cd {hyp["cd_path"]} && python3 json_metadata.py --name "metadata-{hash_key}" --data "{meta_data}" --save "{json_save_path}"')
        print_client_out(out)
        return {'status': True,
                'updated': True,
                'level': level,
                'log': 'Updated Successfully'}
    else:
        return {'status': False,
                'updated': False,
                'level': None,
                'log': 'Wallet Not Exists'}
    #


@app.route('/swap/<address_owner>/<address_customer>/<name>')
def swap_item(address_owner, address_customer, name):
    if os.path.exists(f'accounts/{address_owner}.json'):
        with open(f'accounts/{address_owner}.json', 'r') as r:
            current_data = json.load(r)

        current_data['wallet_address'] = address_customer
        current_data['name'] = name

        if 'transferred' in current_data:
            current_data['transferred'] += 1
        else:
            current_data['transferred'] = 1
        data = current_data
        with open(f'accounts/{address_owner}.json', 'w') as w:
            json.dump(data, w)
        os.rename(f'accounts/{address_owner}.json', f'accounts/{address_customer}.json')
        os.rename(f'accounts/metadata-{address_owner}.json', f'accounts/metadata-{address_customer}.json')
        return {
            'status': True,
            'from': address_owner,
            'to': address_customer,
            'at_level': r['at_level'],
            'contract_address': r['contract_address']
        }
    else:
        return {
            'status': False,
            'error': f'{address_owner} for wallet not exists'
        }


if __name__ == "__main__":
    init()
    app.run(debug=True, host='192.168.1.103')
