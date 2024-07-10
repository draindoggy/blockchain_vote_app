from solcx import compile_standard, install_solc
import json

install_solc('0.8.0')

with open('Election.sol', 'r') as file:
    election_source_code = file.read()

compiled_sol = compile_standard({
    'language': 'Solidity',
    'sources': {
        'Election.sol': {
            'content': election_source_code
        }
    },
    'settings': {
        'outputSelection': {
            '*': {
                '*': ['abi', 'metadata', 'evm.bytecode', 'evm.sourceMap']
            }
        }
    }
}, solc_version='0.8.0')

with open('compiled_election.json', 'w') as file:
    json.dump(compiled_sol, file)

abi = compiled_sol['contracts']['Election.sol']['Election']['abi']
bytecode = compiled_sol['contracts']['Election.sol']['Election']['evm']['bytecode']['object']

print("ABI:", abi)
print("Bytecode:", bytecode)