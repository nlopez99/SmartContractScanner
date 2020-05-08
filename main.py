from web3.auto.infura import w3
from web3.exceptions import BlockNotFound
import argparse
from datetime import datetime
import json

# web3 is dependent on an environment variable called "WEB3_INFURA_PROJECT_ID".
# In order to use this, you need to make a Infura Developer account, and run `export WEB3_INFURA_PROJECT_ID=your_id_here


def get_block_data(block_identifier, log=False, outer_list=[]):
    current_block = w3.eth.getBlock(block_identifier=block_identifier)
    print()
    print("*" * 150)
    print()
    print(f"Block Number: {current_block['number']}")
    for transaction in current_block.transactions:
        current_transaction_data = w3.eth.getTransaction(transaction)
        if not current_transaction_data.to:
            contract_address = current_transaction_data['from']
            code = current_transaction_data['input']
            transaction_hash = str(current_transaction_data['hash'].hex())
            print(f"Transaction Hash: {transaction_hash}\nByteCode: {code}\nContract Address: {contract_address}")
            print()
            if log:
                transaction_data = {"transaction_hash": transaction_hash, "bytecode": code,
                                    "contract_address": contract_address, "block_number": current_block['number']}
                outer_list.append(transaction_data)


def scan_blockchain_for_contracts(args):

    if args['latest']:
        if args['start_block'] or args['end_block']:
            print("Invalid flag combination. If using '-l' or '--latest', don't use '-e' or '-s'.")
            return

        block_num = w3.eth.getBlock("latest")['number']
        while True:
            try:
                get_block_data(block_identifier=block_num)
                # limit calls, and try to let next block be mined
                block_num += 1
            except BlockNotFound:
                block_num -= 1

    elif args['start_block'] or args['end_block']:
        filename = datetime.now().strftime('block_scan_%Y_%m_%d_%H%M%S.json')
        outer_list = []

        start_block = args['start_block'] or w3.eth.getBlock("earliest")['number']
        end_block = args['end_block'] or w3.eth.getBlock("latest")['number']

        if end_block < start_block:
            print("Invalid option, End Block is greater than Start Block.")
            return

        for block_num in range(start_block, end_block):
            get_block_data(block_num, log=args['output'], outer_list=outer_list)

        if args['output']:
            with open(filename, "w") as output_file:
                json.dump(outer_list, output_file)

    else:
        print("Invalid combination use --help to see usage options.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--start-block', help='Block number to start scanning the blockchain from',
                        type=int, required=False)
    parser.add_argument('-e', '--end-block', help='Block number to start scanning the blockchain from',
                        type=int, required=False)
    parser.add_argument('-l', '--latest', help='Using this flag scans the latest block on',
                        action="store_true")
    parser.add_argument('-o', '--output', help='Using this flag writes to an output file in JSON format',
                        action="store_true")
    args = parser.parse_args()
    args = vars(args)
    scan_blockchain_for_contracts(args)
