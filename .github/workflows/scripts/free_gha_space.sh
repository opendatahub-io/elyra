#!/bin/bash

df -h

sudo apt-get update
sudo apt-get remove -y '^dotnet-.*'
sudo apt-get remove -y '^llvm-.*'
sudo apt-get remove -y 'php.*'
sudo apt-get remove -y '^mongodb-.*'
sudo apt-get autoremove -y
sudo apt-get clean
sudo rm -rf /usr/local/.ghcup &
sudo rm -rf /usr/local/lib/android &
sudo rm -rf /usr/local/share/boost &
sudo rm -rf /usr/share/dotnet &
sudo rm -rf /opt/ghc &
sudo rm -rf /opt/hostedtoolcache/CodeQL &

sudo docker image prune --all --force &

wait

df -h
