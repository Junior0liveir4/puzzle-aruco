# 🧩📷 ArUco Puzzle Game – Visão Computacional & Interatividade
Este repositório contém o ecossistema completo do **ArUco Puzzle Game**, uma aplicação interativa que combina visão computacional, sistemas distribuídos e automação. O projeto transforma marcadores ArUco em peças dinâmicas de um quebra-cabeça, permitindo montar diferentes temas (Pokémon, GTA, Mario, etc.) em tempo real com feedback visual e sonoro.

Desenvolvido no **LabSEA (IFES - Campus Guarapari)**, o sistema utiliza o framework IS-Wire para consumir streams de vídeo via RabbitMQ e enviar comandos para atuadores externos (ESP32) e câmeras PTZ.

---

## ✨ Funcionalidades
Além da detecção de marcadores, esta versão aprimorada inclui:

- 🎭 **Multi-Temas:** Suporte a 6 temas diferentes configuráveis via código.

- 🎬 **Intro Cinematográfica:** Reprodução de vídeo e áudio de introdução antes do início da partida.

- 🔊 **Sistema de Áudio:** Integração com pygame para trilha sonora e efeitos.

- 🤖 **Integração com Hardware:**

    1. **PTZ Control:** Envio automático de coordenadas para posicionar a câmera IP no início do jogo.

    2. **ESP32 Feedback:** Publicação do status de vitória em um tópico específico para acionamento de dispositivos físicos.

- 🧠 **Validação Inteligente:** Algoritmo baseado em K-Means e Homografia para verificar se o quebra-cabeça foi montado na ordem correta.

---

## 🛠️ Requisitos do Sistema
Dependências Python
Instale as bibliotecas necessárias:

```Bash
pip install opencv-python numpy is-wire is-msgs pygame scikit-learn Pillow
```
    Nota: É recomendável o uso do opencv-contrib-python para garantir suporte total aos módulos ArUco.

**Infraestrutura**
- **Broker:** RabbitMQ rodando (padrão: 10.10.2.211:30000).

- **Câmera:** Gateway de câmera publicando frames via IS-Wire.

---

## 🚀 Como Executar o Jogo Principal
1. **Configuração do Tema:** No arquivo projeto_jepe+sound.py, escolha o tema desejado alterando a variável game.

2. **Caminhos:** Certifique-se de que as pastas Imagem1, Imagem3, etc., contenham os arquivos mapa_X.png.

3. **Execução:**

```Bash
python3 projeto_jepe+sound.py
```

---

## 📂 Códigos Auxiliares e de Apoio
Para facilitar a preparação do ambiente e testes, o repositório conta com:

1. ✂️ **crop_png.py (Preparador de Imagens)**
Este script automatiza a criação das peças do quebra-cabeça.

- **O que faz:** Recebe uma imagem quadrada (representando 92x92 cm), realiza um corte central e a divide em 16 partes (4x4) de 21x21 cm cada, considerando um espaçamento de 2 cm entre elas.

- **Uso:** Ideal para converter qualquer arte (ex: um mapa ou poster) nas peças mapa_1.png a mapa_16.png que o jogo utiliza.

2. 🔌 **test_esp32.py (Teste de Comunicação)**
Um script minimalista para validar a integração com o hardware externo.

- **O que faz:** Publica manualmente uma mensagem no tópico result.

- **Uso:** Utilize para testar se o seu ESP32 (ou outro atuador) está recebendo corretamente o sinal de "Vitória" via RabbitMQ sem precisar montar o quebra-cabeça inteiro.

---

## 📂 Estrutura do Projeto
```
quebra-cabeça_aruco/
├── projeto_jepe+sound.py   # Script principal do jogo
├── streamChannel.py        # Abstração de comunicação IS-Wire
├── crop_png.py             # Utilitário de recorte de imagens
├── test_esp32.py           # Script de teste de publicação
├── Imagem1/                # Pasta de imagens (Tema Demo)
├── Imagem3/                # Pasta de imagens (Tema Pokémon)
│   ├── mapa_1.png
│   ├── intro_pokemon.mp4
│   └── intro_pokemon.mp3
└── ...
```

---

## 🧠 Detalhes Técnicos do Processamento
O sistema opera com três threads principais para garantir fluidez (Zero Latency):

1. **Thread de Recepção:** Consome o broker RabbitMQ e mantém apenas o frame mais recente em uma fila (queue.Queue).

2. **Thread de Overlay (Visual):** Detecta os ArUcos, calcula a transformação de perspectiva e sobrepõe as imagens das peças no frame original.

3. **Thread de Validação (Lógica):**

- Aplica Homografia para retificar a visão do tabuleiro.

- Usa K-Means Clustering para organizar os centros dos marcadores detectados em uma grade 4x4, mesmo com distorção de perspectiva.

- Compara a grade detectada com a grade expected (gerada aleatoriamente no início de cada jogo, exceto no modo Demo).

---

## 📬 Contato
Desenvolvido por Junior e a equipe do LabSEA.
Para suporte, verifique a documentação interna do laboratório ou entre em contato com os responsáveis pelo projeto de Visão Computacional.
