from flask import Flask, request, jsonify, render_template
from web3 import Web3
import json

app = Flask(__name__)

ganache_url = "http://127.0.0.1:7545"
web3 = Web3(Web3.HTTPProvider(ganache_url))

if web3.is_connected():
    print("успешное подключение к Ganache")

web3.eth.default_account = web3.eth.accounts[0]

with open('compiled_election.json', 'r') as file:
    compiled_sol = json.load(file)

abi = compiled_sol['contracts']['Election.sol']['Election']['abi']
bytecode = compiled_sol['contracts']['Election.sol']['Election']['evm']['bytecode']['object']

Election = web3.eth.contract(abi=abi, bytecode=bytecode)
tx_hash = Election.constructor().transact()
tx_receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

print("контракт задеплоен по адресу:", tx_receipt.contractAddress + 'n')

election = web3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

@app.route('/')
def index():
    candidates_count = election.functions.candidatesCount().call()
    candidates = []
    for i in range(1, candidates_count + 1):
        candidate = election.functions.candidates(i).call()
        candidates.append(candidate)
    return render_template('index.html', candidates=candidates)

@app.route('/vote', methods=['POST'])
def vote():
    candidate_name = request.form['candidate_name']
    accounts = web3.eth.accounts
    account_index = int(request.form['account_index'])

    candidate_id = get_candidate_id(candidate_name)

    if candidate_id is not None:
        web3.eth.default_account = accounts[account_index]
        try:
            tx_hash = election.functions.vote(candidate_id).transact()
            web3.eth.wait_for_transaction_receipt(tx_hash)
            return jsonify({"message": f"аккаунт {accounts[account_index]} проголосовал за кандидата {candidate_name}"})
        except Exception as e:
            return jsonify({"error": f"аккаунт {accounts[account_index]} не смог проголосовать: {e}"})
    else:
        return jsonify({"error": f"кандидат с именем {candidate_name} не найден."})

def get_candidate_id(candidate_name):
    candidates_count = election.functions.candidatesCount().call()
    for i in range(1, candidates_count + 1):
        candidate = election.functions.candidates(i).call()
        if candidate[1] == candidate_name:
            return candidate[0]
    return None

if __name__ == '__main__':
    app.run(debug=True)