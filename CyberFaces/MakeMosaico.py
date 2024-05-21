import os
import cv2
import ast
import time
import random
import numpy as np
import Functionalities as func
from PIL import Image, ImageDraw, UnidentifiedImageError

def redimensionar_imagem(imagem, tamanho):
    return imagem.resize((tamanho, tamanho))

def recortar_rosto(imagem, pontos):
    recorte = Image.new('RGBA', imagem.size, (0, 0, 0, 0))

    designer = ImageDraw.Draw(recorte)
    designer.polygon(pontos, fill=(0, 0, 0))

    recorte.paste(imagem, mask=recorte)

    xy = random.randint(200, 800)
    return recorte.resize((xy, xy)), xy

def criar_mosaico(imagens, tamanhos_imagens):
    num_imagens = len(imagens)
    largura_mosaico = 1500
    altura_mosaico = 800

    # Crie uma imagem branca com suporte a canal alfa (RGBA)
    mosaico = Image.new("RGBA", (largura_mosaico, altura_mosaico), (0, 0, 0, 0))

    posUsadas = []

    for i, imagem in enumerate(imagens):
        tamanho_imagem = tamanhos_imagens[i]

        while True:
            posicao_x = random.randint(-10, largura_mosaico - tamanho_imagem)
            posicao_y = random.randint(-10, altura_mosaico - tamanho_imagem)

            if ((posicao_x, posicao_y) not in posUsadas):
                break
            
        mosaico.paste(imagem, (posicao_x, posicao_y), imagem)
        posUsadas.append((posicao_x, posicao_y))
        for j in range(200):
            posUsadas.append((posicao_x + j, posicao_y + j))
            posUsadas.append((posicao_x - j, posicao_y - j))
            posUsadas.append((posicao_x + j, posicao_y - j))
            posUsadas.append((posicao_x - j, posicao_y + j))
    return mosaico


#TODO: Salvar um mosaico a cada x rostos. 10
images_folder = r'./images'
coordenadas_folder = r'./coordenadas'
coordenadas_file = r'./coordenadas/coordenadas.txt'

len_images_folder = 0

rostos_recortados = []
tamanhos_imagens = []

while True:
    if os.path.exists(images_folder) and os.path.exists(coordenadas_folder) and os.path.exists(coordenadas_file):
        len_folder = len(os.listdir(images_folder))
        if len_images_folder < len_folder:
            len_images_folder = len_folder

            arquivos_png = [arquivo for arquivo in os.listdir(images_folder) if arquivo.endswith('.png')]
            coordenadas = func.load_coordenadas(coordenadas_file)
            
            rostos_recortados = []
            tamanhos_imagens = []

            for arquivo_png, coordenada in zip(arquivos_png, coordenadas):
                try:
                    imagem = Image.open(os.path.join(images_folder, arquivo_png))
                except UnidentifiedImageError:
                    print(f'O arquivo {arquivo_png} não é uma imagem válida.')
                    continue
                
                pontos = None
                pontos = [ast.literal_eval(coordenada[len(arquivo_png[5:-4]+':'): ]) for coordenada in coordenadas if coordenada.startswith(arquivo_png[5:-4]+':')]
                if pontos:
                    pontos = pontos[0]
                    rosto_recortado, tamanho_imagem = recortar_rosto(imagem, pontos)
                    rostos_recortados.append(rosto_recortado)
                    tamanhos_imagens.append(tamanho_imagem)
                else:
                    print(f'Coordenadas do arquivo {arquivo_png} não encontradas.')
                    break
        #TODO: TEMPO!
        mosaico = criar_mosaico(rostos_recortados, tamanhos_imagens)

        # Converta o mosaico para uma matriz numpy (formato que o OpenCV pode lidar)
        mosaico = cv2.cvtColor(np.array(mosaico), cv2.COLOR_RGB2BGR)

        # Salve o mosaico no diretório atual
        mosaico_path = r'./mosaico.png'
        cv2.imwrite(mosaico_path, mosaico)
    else:
        print(f'Problema com as pastas de arquivos, verifique se os diretórios estão corretos.')

    time.sleep(1)