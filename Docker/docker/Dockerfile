# Utiliza uma imagem Python leve e estável
FROM python:3.9-slim

# Evita que o Python gere arquivos .pyc e permite logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instala dependências básicas do sistema operacional para o OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Copia o arquivo de requisitos primeiro (otimiza o cache do Docker)
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o script principal, o canal de stream e as pastas de imagens
# Certifique-se de que as pastas Imagem1, Imagem3, etc., estão no mesmo diretório
COPY puzzle-aruco.py .
COPY streamChannel.py .
COPY Imagem1/ ./Imagem1/
COPY Imagem3/ ./Imagem3/
COPY Imagem4/ ./Imagem4/
COPY Imagem5/ ./Imagem5/
COPY Imagem6/ ./Imagem6/
COPY Imagem7/ ./Imagem7/

# Comando para iniciar a aplicação
CMD ["python", "puzzle-aruco.py"]
