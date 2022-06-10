# dice-python

`dice-python` is a Python module which takes Python code and outputs that equivalent code in Dice, a probabilistic programming language.  You may use `dice-python` by pulling our pre-built Docker image, or follow the manual setup guide below.

## Usage

Before running examples, please install `dice-python` following the instructions in the *Installation* section.  If you use Docker for the setup, you may run `docker run -it dotkrnl/dice-python bash` to get into the environment.

To test the examples under the `evaluate()` function in `transform.py`, comment in and out whichever example you currently want to test. Note that this program tests one example at a time.

Once you have selected an example that you want, use ```python3.9 transform.py``` to run `transform.py`. The `translated.dice` file should then be populated with the translated Dice code. The output from `transform.py` should then be a dictionary of the form ```{True: <value>, False: <value>, 'Time': <value>}```.

To run unit tests of all examples, use `python3.9 -m unittest discover tests`.

## Installation

### Docker Setup

A pre-built [Docker image](https://hub.docker.com/r/dotkrnl/dice-python) is available, and can be installed with:

```bash
docker pull dotkrnl/dice-python
```

If you have not setup Docker yet, please follow the *Setup Docker* instructions in the following *Manual Installation* section.

### Manual Installation

#### Setup Docker
```bash
# Install Docker prerequisites
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo apt-get update
sudo apt-get install ca-certificates curl gnupg lsb-release

# Add Docker APT repository
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Make sure that the docker environment is properly setup
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

#### Pull and Run Dice in Docker

```bash
docker pull sholtzen/dice
docker run -d sholtzen/dice tail -f /dev/null
docker ps --all
docker exec -it <name of container> bash
```

#### Upgrade Dice Docker Container

```bash
sudo sed -i 's/buster/bullseye/g' /etc/apt/sources.list
sudo sed -i 's#/debian-security bullseye/updates# bullseye-security#g' /etc/apt/sources.list

export LC_ALL=C
sudo apt update
sudo apt upgrade
sudo apt full-upgrade
sudo apt autoremove

sudo apt install python3.9
```

#### Setup Dice in Container

```bash
opam init
opam switch create 4.09.0
eval `opam config env`
opam depext mlcuddidl
opam pin add dice git+https://github.com/SHoltzen/dice.git
dune build
dune exec dice
dune test
dune exec dicebench
```

#### Install Vim in Container

```bash
sudo apt install vim
```

####  Clone project into container

```bash
git clone https://github.com/dotkrnl/dice-python.git
```
