# Kamina Community
<p align="center">
    <img src="logo/kamina.svg" width="400"/>
</p>

Kamina's community node implementation in python 

## What is Kamina?
Kamina is a decentralized social network. We achieve decentralization by the usage of ipfs.
Ipfs can be disabled(TODO), if it is disabled, the community node will lose its decentralization
until we can achieve decentralization without the usage of ipfs.

#### Further reading
[Kamina's documentation](https://github.com/KaminaProject/kDocumentation)
[IPFS's api python implementation's documentation](https://ipfs.io/ipns/QmZ86ow1byeyhNRJEatWxGPJKcnQKG7s51MtbHdxxUddTH/Software/Python/ipfsapi/)

## Installation
There are some prerequisites in order to start tinkering with the project.
- Python (version 3.6)
- Pipenv (for python 3.6)

1. Clone the repo and cd into the directory
```sh
git clone https://github.com/KaminaProject/community-node.git
cd community-node
```

2. Install the python dependencies with:
```
PIPENV_VENV_IN_PROJECT=1 pipenv install
```

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
