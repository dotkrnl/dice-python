# dice-python
dice-python is a program used to take Python code and output that equivalent code in Dice, a probabilistic programming language.

Prerequisite setup is in the Linux Environment Setup section below. Do this before trying to run any example.

To test the examples under the evaluate() function in transform.py, comment in and out whichever example you currently want to test. Note that this program tests one example at a time.

Once you have selected an example that you want, do ```python3.9 transform.py``` to run transform.py. The translated.dice file should be populated with the translated Dice code. The output from transform.py should be a dictionary of the form ```{True: <value>, False: <value>, 'Time': <value>}```.

## Linux Environment Setup
Setup Docker:
```
sudo apt-get remove docker docker-engine docker.io containerd runc

sudo apt-get update

sudo apt-get install \ 
ca-certificates \ 
curl \ 
gnupg \ 
lsb-release

sudo mkdir -p /etc/apt/keyrings

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
$(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update

sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

sudo groupadd docker

sudo usermod -aG docker $USER

newgrp docker
```
Pull Docker Dice container:
```
docker pull sholtzen/dice

docker run -d sholtzen/dice tail -f /dev/null

docker ps --all

docker exec -it <nameOfContainer> bash
```
Update Dice container's Debian distribution so we can use Python 3.9
```
sudo apt-mark showhold

sudo apt update

sudo apt upgrade

sudo apt full-upgrade

sudo apt autoremove

sudo sed -i 's/buster/bullseye/g' /etc/apt/sources.list

sudo sed -i 's#/debian-security bullseye/updates# bullseye-security#g' /etc/apt/sources.list

export LC_ALL=C

sudo apt update

sudo apt upgrade

sudo apt full-upgrade

sudo apt autoremove

sudo apt install python3.9
```
Setup Dice environment in container
```
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
Install text editor for coding in container
```
sudo apt install vim
```

Clone project into container
```
git clone https://github.com/dotkrnl/dice-python.git
```
