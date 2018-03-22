# Kamina Community
![Kamina_Logo](kamina_logo.svg)  
Kamina's community node implementation in python 

## What is Kamina?
Kamina is an ipfs-based decentralized social network.

#### Further reading
[IPFS's api python implementation's documentation](https://ipfs.io/ipns/QmZ86ow1byeyhNRJEatWxGPJKcnQKG7s51MtbHdxxUddTH/Software/Python/ipfsapi/)

## Installation

There are some prerequisites in order to start tinkering with the project.
- Python (version 3)
- Pipenv (for python 3)

1. Clone the repo and cd into the directory
```sh
git clone https://github.com/KaminaProject/kamina-community.git
cd kamina-community
```

2. Install the python dependencies with:
```
pipenv install
```

3. Initialize a pipenv shell
```
pipenv shell
```

4. Initialize the ipfs node
```
./kamina init
```

5. Initialize the kamina community daemon
```
./kamina daemon
```

---
In memory of Miguel Vesga
