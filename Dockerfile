FROM python:3.10-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Etapa 1: Instala ferramentas necessárias e remove pacotes conflitantes
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    gpg \
    ca-certificates \
    apt-transport-https \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    libsasl2-dev \
    libldap2-dev \
    && apt-get remove -y unixodbc libodbc1 libodbcinst2 unixodbc-dev || true \
    && rm -rf /var/lib/apt/lists/*

# Etapa 2: Adiciona repositório da Microsoft (forma segura)
RUN mkdir -p /etc/apt/keyrings \
    && curl -sSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /etc/apt/keyrings/microsoft.gpg \
    && echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/microsoft.gpg] https://packages.microsoft.com/debian/11/prod bullseye main" > /etc/apt/sources.list.d/mssql-release.list

# Etapa 3: Instala somente os drivers da Microsoft (sem conflitos)
RUN apt-get update \
    && ACCEPT_EULA=Y apt-get install -y \
        msodbcsql17 \
        unixodbc \
        unixodbc-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o projeto
COPY . /app

# Instala dependências Python
RUN pip install --upgrade pip
RUN pip install flask pyodbc gunicorn

# Porta do app
EXPOSE 5000

# Start do app
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "chamados_serviceaide:application"]
