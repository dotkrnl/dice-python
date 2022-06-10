FROM ocaml/opam:debian-11-ocaml-4.09

WORKDIR /dice-python

# Install Python 3.9 and other dependencies
RUN sudo apt-get update && sudo apt-get install python3.9 m4 pkg-config libffi-dev libgmp-dev -y

# Install Rust and Cargo
RUN sh -c "$(curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs)" -- -y

# Install Dice dependencies
RUN sudo mkdir -p /dice && sudo chown $(id -un) /dice-python && sudo chown $(id -un) /dice
RUN git clone https://github.com/SHoltzen/dice.git /dice
RUN cd /dice && git submodule update --init --recursive && cd rsdd && git checkout master
RUN cd /dice && opam init && opam install . --deps-only

# Build Dice
RUN /bin/bash -c "cd /dice && eval '$(opam env)' && source $HOME/.cargo/env && dune build"

# Install Dice
RUN /bin/bash -c "cd /dice && eval '$(opam env)' && dune install"

# Install Vim for user's convience
RUN sudo apt-get install vim -y

# Clone dice-python
RUN VERSION=0710-b1
RUN git clone https://github.com/dotkrnl/dice-python.git /dice-python

CMD python3.9 /dice-python/transform.py
