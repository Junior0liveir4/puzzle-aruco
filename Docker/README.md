# 🐳 ArUco Puzzle Game – Versão Dockerizada
Esta versão do projeto foi estruturada para rodar de forma distribuída e escalonável dentro de um cluster Kubernetes. A principal mudança em relação à versão local é a transição de uma interface gráfica (GUI) para um modelo de serviço headless, onde o processamento ocorre no container e o resultado é publicado via tópicos para visualização remota.

---

## 🏗️ Arquitetura de Microserviços
Diferente da versão desktop, o sistema agora opera sem periféricos locais (teclado/monitor):

- **Processamento Central:** O container detecta os marcadores ArUco e realiza a sobreposição das imagens das peças em tempo real.


- **Publicação de Frames:** Em vez de abrir uma janela com cv2.imshow, o sistema codifica os frames processados e os publica no tópico Puzzle.Frame.{camera_id}.

- **Visualização Remota:** O resultado pode ser consumido por qualquer cliente (como um browser ou dashboard) que esteja inscrito no tópico de saída do RabbitMQ.

---

## 📦 Detalhamento do Dockerfile
O Dockerfile foi projetado para ser leve e eficiente, garantindo que todas as dependências de visão computacional estejam presentes em um ambiente de servidor:


- **Imagem Base:** Utiliza python:3.9-slim para otimizar o tamanho da imagem e o tempo de deploy.


- **Dependências de Sistema:** Instala bibliotecas como libglib2.0-0 e libgl1, que são fundamentais para o funcionamento do OpenCV em containers Linux que não possuem uma interface gráfica nativa.

- **Configurações de Ambiente:**

    1. PYTHONDONTWRITEBYTECODE=1: Evita a criação de arquivos .pyc, mantendo o container limpo.

    2. PYTHONUNBUFFERED=1: Garante que os logs de execução e detecção sejam enviados imediatamente para o console do Kubernetes.


- **Empacotamento de Assets:** O arquivo copia automaticamente o script puzzle-aruco.py, o módulo streamChannel.py e todas as pastas de temas (Imagem1 a Imagem7) para garantir que o jogo tenha todos os recursos necessários internamente.

---

## ☸️ Orquestração com Kubernetes (YAML)
A implantação no cluster do LabSEA é gerenciada por um arquivo YAML que separa a configuração da lógica de execução:

1. **ConfigMap (puzzle-aruco-config)**
Permite alterar o comportamento do sistema sem precisar reconstruir a imagem Docker:

- BROKER_URI: Define o endereço de conexão com o RabbitMQ.

- CAMERA_ID: Especifica qual câmera o serviço deve processar.

- GAME_NAME: Variável de ambiente que define o tema ativo (ex: Angry ArUcos, Super Mario Puzzle).

2. **Deployment (puzzle-aruco)**
Define como o container deve rodar no cluster:

- **Imagem:** Utiliza a tag versionada juniorgui/puzzle-aruco:v2.

- **Gerenciamento de Recursos:** Estabelece limites de CPU (800m) e Memória (512Mi) para garantir que o serviço de visão computacional tenha performance estável sem afetar outros pods do nó.

3. **Service**
Cria um ponto de acesso estável dentro do cluster para o serviço do quebra-cabeça.

##  🚀 Guia de Deploy
```
kubectl apply -f puzzle-aruco.yaml
```

---

##  📂 Ferramentas de Apoio Incluídas
- **crop_png.py:** Script para preparar novas imagens, realizando o recorte técnico em grade 4x4.

- **test_esp32.py:** Utilitário para testar a publicação de mensagens de vitória para o hardware externo.

---

##  📬 Contato
Desenvolvido por Junior e o time do **LabSEA (IFES Guarapari)**. Este projeto exemplifica a modernização de ferramentas de laboratório através da containerização.
