from PIL import Image
import os

def cortar_imagem(entrada, saida):
    """
    Corta a imagem em 16 partes (4x4) de 21x21 cm
    com espaçamento de 2 cm entre os cortes.
    Assume que a imagem quadrada de entrada representa 92x92 cm.
    """

    # Criar pasta de saída
    os.makedirs(saida, exist_ok=True)

    # Abrir imagem
    img = Image.open(entrada)
    largura, altura = img.size

    # --- 1) Garantir que seja quadrada (corte central) ---
    lado = min(largura, altura)
    esquerda = (largura - lado) // 2
    superior = (altura - lado) // 2
    direita = esquerda + lado
    inferior = superior + lado
    img = img.crop((esquerda, superior, direita, inferior))

    nome_completo = os.path.join(saida, "mapa.png")
    # Salva a imagem
    img.save(nome_completo)

    # Atualizar dimensões após o crop
    largura, altura = img.size

    # --- 2) Calcular pixels por cm ---
    px_por_cm = largura / 92.0   # já que 92 cm corresponde ao lado inteiro

    # --- 3) Definir tamanhos em pixels ---
    corte_px = int(round(21 * px_por_cm))
    espaco_px = int(round(2 * px_por_cm))

    contador = 1
    for i in range(4):  # linhas
        for j in range(4):  # colunas
            x0 = j * (corte_px + espaco_px)
            y0 = i * (corte_px + espaco_px)
            x1 = x0 + corte_px
            y1 = y0 + corte_px

            # Realizar o corte
            corte = img.crop((x0, y0, x1, y1))

            # Nome do arquivo
            nome_arquivo = os.path.join(saida, f"mapa_{contador}.png")
            corte.save(nome_arquivo)
            contador += 1

    print(f"✅ Cortes concluídos! As 16 imagens foram salvas em: {saida}")


# -------------------------------
# Exemplo de uso:
# -------------------------------
cortar_imagem("/homes/joliveira/Desktop/Junior/Códigos/quebra-cabeça_aruco/JEPE 2025/mapa_original.png", "/homes/joliveira/Desktop/Junior/Códigos/quebra-cabeça_aruco/JEPE 2025/Imagem")
