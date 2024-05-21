# Rostos&Frases
_Projeto que, ao identificar um rosto, mostra frases com base na sua posição._

## Objetivo:
Criar um programa que:
* Ao identificar um rosto, mostre frases;
   * aleatórias?
* Manter a frase alinhada ao rosto identificada (na parte superior);
   * Redimensionar a frase quando o rosto de afastar.
* Mudar a frase quando o rosto de aproximar e se afastar;
* Capturar o rosto (após a permissão) e construir um mosaico de rostos;
   * Com ou sem frases?
   * Redimensionar o mosaico a cada rosto inserido ou preencher um de tamanho fixo?
   * * Repetir rostos?

## Andamento:

Inicialmente usamos as bibliotecas:
Nesse projeto, as seguintes bibliotecas estão sendo usadas:

* **cv2** (OpenCV): É uma biblioteca para processamento de imagem e visão computacional;

* **dlib**: Uma biblioteca que inclui recursos para detecção facial e pontos-chave (landmarks).

* **numpy**: Amplamente usada para computação numérica em Python.

Também estávamos usando um modelo já treinado para fazer o reconhecimento facial:
```python
dlib.shape_predictor
```

Tivemos avanços e bons resultados, no entanto, encontramos uma alternativa mais interessante, um recurso da `Google`.

Agora estamos dando seguimento ao projeto usando [**MediaPipe**](https://developers.google.com/mediapipe/solutions/vision/face_detector)

## ToDo:
* ~~Usar o Face detection ao invés do Face Landmark;~~
    * será usado o Face Landmark pela distância que mantêm o rosto identificado.
* ~~Fixar as frases no rosto identificado;~~
* ~~Arrumar a velocidade das frases;~~
* ~~Arrumar a posição das frases;~~
* ~~Arrumar a direção das frases;~~
* Desenvolver o redimensionamento das frases com o deslocamento do rosto em Z (aumentar quando se afastar para conseguir ler);
* ~~Mudar a frase com o deslocamento em Z;~~
* Fazer um mosaico com os rostos;
* ~~O rosto precisa ser salvo automaticamente;~~
* novo programa para gerar o mosaico;
* ~~mudar a cor da frase (semáforo);~~
* ~~aumentar o tamanho da frase quando se afastar;~~
* ~~Possibilitar que 3 rostos interajam ao mesmo tempo;~~
* ~~Tamanho inicial estático pro mosaico;~~
* Atualizar o mosaico com um filtro que distorce a imagem;
* ~~Suporte para 360?;~~
* Testes;
* ~~Corrigir o problema de um rosto que é identificado muito próximo de uma das bordas e gera um problema para a captura (não tem a medida do queixo, então o resultado da conta é um noneType e dá erro na execução);~~
* ~~Trocar a cor do fundo do mosaico para preto;~~
* Ver como identificar quando a pessoa sorrir, piscar, etc;
* ~~Possibilitar que o programa seja desligado e ligado novamente;~~
   * ~~Salvar o cont localmente.~~
* a biblioteca tem limite de memória?
* o computador está com pouco espaço?
* Aumentar o tamanho das letras vermelhas;
* Aumentar a distância para detectar o rosto;
* Mosaico do formato da máscara;