#!/bin/bash
set -ex

# Update and install dependencies
sudo apt update
sudo apt install -y python3 python3-pip pythonpy python3-pytest postgresql postgresql-plpython3-16 git git-core

# Start PostgreSQL service
sudo systemctl start postgresql

# Clone the repository
git clone https://gitlab.com/CodeDarkin/memelang.git
cd memelang

# Set up PostgreSQL with embedded commands
sudo -u postgres psql -c "CREATE DATABASE meme;"
sudo -u postgres psql -d meme -c "CREATE EXTENSION plpython3u;"

# Run the setup SQL script
sudo -u postgres psql -d meme -f memelang_plpythonu_setup.sql

# Insert default data
sudo -u postgres psql -d meme -f data.sql
