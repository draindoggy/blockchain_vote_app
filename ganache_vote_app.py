from web3 import Web3
import json


ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

if web3.is_connected():
    print("успешное подключение к Ganache\n")

web3.eth.default_account = web3.eth.accounts[0]

with open('compiled_election.json', 'r') as file:
    compiled_sol = json.load(file)

abi = compiled_sol['contracts']['Election.sol']['Election']['abi']
bytecode = compiled_sol['contracts']['Election.sol']['Election']['evm']['bytecode']['object']

Election = web3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = Election.constructor().transact()
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

print("контракт задеплоен по адресу:", tx_receipt.contractAddress + '\n')

election = web3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

candidates_count = election.functions.candidatesCount().call()

print('имена кандидатов:')
candidates = []
for i in range(1, candidates_count + 1):
    candidate = election.functions.candidates(i).call()
    candidates.append(candidate)
    print(f"кандидат {candidate[0]}: {candidate[1]}")

def get_candidate_id(candidate_name):
    for candidate in candidates:
        if candidate[1] == candidate_name:
            return candidate[0]
    return None


accounts = web3.eth.accounts
account_count = int(input('введите количество аккаунтов, которые будут принимать участие в голосовании:'))
for i in range(account_count):
    candidate_name = input(f"введите имя кандидата, за которого хотите проголосовать (аккаунт {i + 1}): ")
    candidate_id = get_candidate_id(candidate_name)

    if candidate_id is not None:
        web3.eth.default_account = accounts[i]
        try:
            tx_hash = election.functions.vote(candidate_id).transact()
            web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"аккаунт {accounts[i]} проголосовал за кандидата {candidate_name}\n")
        except Exception as e:
            print(f"аккаунт {accounts[i]} не смог проголосовать: {e}")
    else:
        print(f"кандидат с именем {candidate_name} не найден.")

for i in range(1, candidates_count + 1):
    candidate = election.functions.candidates(i).call()
    print(f"кандидат {candidate[0]}: {candidate[1]} - голоса: {candidate[2]}")