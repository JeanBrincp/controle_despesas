#!/bin/bash

# Atualiza os pacotes
apt-get update

# Importa chave da Microsoft
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

# Adiciona repositório para o driver
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

apt-get update

# Instala o driver ODBC 17 e dependências
ACCEPT_EULA=Y apt-get install -y msodbcsql17 unixodbc-dev

# Roda o app Python (ajuste conforme sua necessidade)
python app.py
