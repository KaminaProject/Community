# Kamina Community
<p align="center">
    <img src="logo/kamina.svg" width="400"/>
</p>

Kamina's ***Kamina Community*** component implemented in Python. 

## What is Kamina?
Kamina is a decentralized social network which achieves it's goals using IPFS. 
IPFS can be disabled. If it is disabled, the community node will lose its 
decentralization until we can achieve decentralization
 without the usage of IPFS.

#### Further reading
[Kamina's documentation](https://github.com/KaminaProject/kDocumentation)
[IPFS's api python implementation's documentation](https://ipfs.io/ipns/QmZ86ow1byeyhNRJEatWxGPJKcnQKG7s51MtbHdxxUddTH/Software/Python/ipfsapi/)

## Installation
#### Prerequisites
- Python (version 3.6)
- Pipenv (for python 3.6)

####  Install

1. Clone the repo and cd into the directory
```sh
git clone https://github.com/KaminaProject/Community.git
cd Community
```

2. Install the python dependencies with:
```
PIPENV_VENV_IN_PROJECT=1 pipenv install
```

#### Run
3. Initialize a pipenv shell
```
pipenv shell
```


4. Initialize the community node
```
./kcn init
```

5. Start the community daemon
```
./kcn daemon
```

---

In memory of Miguel Vesga
