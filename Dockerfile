FROM python:3.10-slim

# Evitar prompts durante instalação
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Diretório de trabalho
WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    gpg \
    ca-certificates \
    apt-transport-https \
    gcc \
    g++ \
    unixodbc \
    unixodbc-dev \
    libpq-dev \
    libsqlite3-dev \
    libssl-dev \
    libffi-dev \
    libsasl2-dev \
    libldap2-dev \
    libodbc1 \
    && rm -rf /var/lib/apt/lists/*

# Adiciona o repositório da Microsoft de forma moderna (sem apt-key)
RUN mkdir -p /etc/apt/keyrings \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17 \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos da aplicação
COPY . /app

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install flask pyodbc gunicorn

# Expor a porta usada pela aplicação
EXPOSE 5000

# Comando padrão ao iniciar o container
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "chamados_serviceaide:application"]
