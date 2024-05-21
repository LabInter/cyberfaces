import os
import cv2
import ast
import random
import mediapipe as mp

face_info = [None, None, None]
face_detected = False

# "constantes"
SMALL_DISTANCE = 120
BIG_DISTANCE = 70

# Salvar a imagem de captura de a cada 10 rostos.
def main_loop(cap, face_mesh, cont):
    global face_info
    global face_detected

    while cap.isOpened():
        try:
            success, image = cap.read()

            if not success:
                raise Exception("Não foi possível abrir a câmera.")
            
            image.flags.writeable = False
            results = face_mesh.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            image.flags.writeable = True

            if results.multi_face_landmarks:
                #resultados = reversed(results.multi_face_landmarks)

                cont = handle_faces(reversed(results.multi_face_landmarks), image, cont)
            else:
                face_detected = False
                face_info = [None, None, None]

            cv2.imshow('MediaPipe FaceMesh', image)
            
            # Caso seja pressionado "esc", encerra a execução do programa.
            key = cv2.waitKey(5) & 0xFF
            if key == 27:
                break
        except Exception as e:
            print(f"Erro: {e}")
    return cont

# Gerencia os rostos que estão sendo identificados
# para cada um ser tratado individualmente
def handle_faces(multi_face_landmarks, image, cont):
    global face_info
    image_copy = image.copy()

    # Variáveis para a criação da mascara.
    mp_drawing = mp.solutions.drawing_utils
    mp_face_mesh = mp.solutions.face_mesh
    mp_drawing_styles = mp.solutions.drawing_styles

    for idx, face_landmarks in enumerate(multi_face_landmarks):
        cont = handle_face(idx, face_landmarks, image, image_copy, cont)

    for i in range(3):
        if i > idx:
            face_info[i] = None

    for info in face_info:
        if info:
            make_landmarks(mp_drawing, mp_face_mesh, mp_drawing_styles, image, info['landmarks'])
            cv2.putText(image, info['frase'], (info['x_text'], info['y_text']), cv2.FONT_HERSHEY_SIMPLEX, info['font_size'], info['color'], 2, cv2.LINE_AA)

    return cont

# Constrói o vetor de informações necessárias sobre o rosto
# Salva um print do rosto que foi detectado.
# OBS: Recebe um rosto por vez.
def handle_face(idx, face_landmarks, image, image_copy, cont):
    global face_info
    global face_detected
    distance, x_forehead, y_forehead, coordenadas = get_positions(face_landmarks, image)

    try:
        if face_info[idx] == None:
            i = random.randint(0, 74)
            face_detected = True
        else:
            i = face_info[idx]['i']
    except:
        i = random.randint(0, 74)
        face_detected = True
    
    frase, color, font_size = get_text_and_color(distance, i, SMALL_DISTANCE, BIG_DISTANCE)
    x, y = set_text_position(x_forehead, y_forehead, frase, font_size)

    # Armazene as informações do rosto atual
    face_info[idx] = {
        'frase': frase,
        'color': color,
        'font_size': font_size,
        'x_text': x,
        'y_text': y,
        'i': i,
        'landmarks': face_landmarks,
        'coordenadas': coordenadas
    }

    if face_detected and cont is not None:
        print_image(image_copy, cont)
        save_coordenadas(coordenadas, cont)
        cont += 1
        face_detected = False

    return cont

# Retorna o cálculo da distância entre a testa e o queixo para saber se o rosto está próximo ou distante.
# Retorna também as coordenadas (x, y) da testa para posicionar a frase
def get_positions(face_landmarks, image):
    pt_forehead = 10  # Ponto da testa
    pt_chin = 152  # Ponto do queixo

    x_forehead = face_landmarks.landmark[pt_forehead].x * image.shape[1]
    y_forehead = face_landmarks.landmark[pt_forehead].y * image.shape[0]
    x_chin = face_landmarks.landmark[pt_chin].x * image.shape[1]
    y_chin = face_landmarks.landmark[pt_chin].y * image.shape[0]

    distance = ((x_forehead - x_chin)**2 + (y_forehead - y_chin)**2)**0.5

    pontos = [
        103, 67, 109, 10, 338, 297, 332, 284, 251, 389, 
        356, 454, 323, 401, 361, 435, 288, 397, 365, 379, 
        378, 400, 377, 152, 148, 176, 149, 150, 136, 172,
        58, 132, 93, 234, 127, 162, 21, 54
    ]

    lista_coordenadas = []

    for p in pontos:
        x = face_landmarks.landmark[p].x * image.shape[1]
        y = face_landmarks.landmark[p].y * image.shape[0]

        lista_coordenadas.append((x, y))

    return distance, x_forehead, y_forehead, lista_coordenadas

# Retorna uma frase aleatória
# E a cor e o tamanho da fonte com base na distância que o rosto está.
# TODO: phrases é um vetor que ocupa muito espaço, armazenar de uma maneira diferente.
def get_text_and_color(distance, i, marca_prox, marca_dist):
    colors = [(0, 255, 0), (0, 255, 255), (0, 0, 255)]  # Verde, Amarelo, Vermelho
    phrases = [
        ["Ola, estou aqui para ajudar!", "Registro: Pessoa comum", "Intruso detectado: A maquina observa."],
        ["Tenha um otimo dia!", "Registro: Sujeito nao identificado", "Nas sombras ciberneticas, estamos te vigiando."],
        ["Voce e muito especial para nos.", "Registro: Visitante desconhecido", "A tecnologia nunca fecha os olhos."],
        ["Sinto muito, nao posso fazer isso.", "Registro: Entidade digital", "Seus movimentos sao agora digitais."],
        ["Estamos aqui para apoia-lo.", "Registro: Ser humano autenticado", "Cameras roboticas te seguem como sombras implacaveis."],
        ["Por favor, forneça mais informacoes.", "Registro: Identidade nao verificada", "Voce e agora parte de nossa opera digital."],
        ["Tudo ficara bem.", "Registro: Presenca detectada", "Seu rosto e apenas um pixel na tela do desconhecido."],
        ["Voce e valioso para nos.", "Registro: Visitante nao autorizado", "As sombras do ciberespaco sussurram."],
        ["Obrigado por escolher nossos servicos.", "Registro: Usuario comum", "O DNA digital da humanidade se desenrola."],
        ["Nao consigo responder a essa pergunta.", "Registro: Consulta anonima", "Aqui, somos todos prisioneiros da Matrix."],
        ["Voce e unico de sua maneira.", "Registro: Entidade desconhecida", "Nossas vidas sao tracadas na areia do tempo."],
        ["Estou aqui para ajudar.", "Registro: Identidade nao verificada", "O olho eletronico nao pode ser enganado."],
        ["Como voce esta hoje?", "Registro: Pessoa sem identificacao", "Sua presenca digital e uma linha de codigo."],
        ["Vamos encontrar uma solucao.", "Registro: Ser humano autenticado", "As sombras ciberneticas escondem segredos."],
        ["Voce e especial para nos.", "Registro: Visitante nao autorizado", "Cada clique e um passo mais fundo na toca do coelho."],
        ["Sinta-se a vontade para perguntar.", "Registro: Identidade desconhecida", "As redes invisiveis tecem nosso destino digital."],
        ["Desculpe, nao compreendi.", "Registro: Consulta nao identificada", "A presenca humana e apenas um traco de pixels."],
        ["Estamos aqui para ajudar.", "Registro: Entidade digital", "A memoria da maquina nunca se desvanece com o tempo."],
        ["Como posso te auxiliar?", "Registro: Pessoa comum", "Cada acao e uma gota no oceano da ciber-realidade."],
        ["O que voce gostaria de fazer?", "Registro: Identidade nao verificada", "Nossa existencia e uma linha de codigo em constante evolucao."],
        ["Vamos resolver isso juntos.", "Registro: Ser humano autenticado", "Aqui, a privacidade e uma ilusao fugaz e efemera."],
        ["Sua opiniao e importante para nos.", "Registro: Visitante desconhecido", "Os observadores ciberneticos veem o invisivel."],
        ["Estamos prontos para ajudar.", "Registro: Identidade nao verificada", "Somos marionetes nas maos do mestre da tecnologia."],
        ["Como posso ser util?", "Registro: Pessoa sem identificacao", "O registro digital e o testemunho de nossa jornada."],
        ["Ficarei feliz em te auxiliar.", "Registro: Visitante nao autorizado", "A vigilancia e o preco que pagamos pela conveniencia."],
        ["Em que posso te ajudar hoje?", "Registro: Consulta anonima", "O olho da maquina e onipresente e onisciente."],
        ["Voce e importante para nos.", "Registro: Identidade nao verificada", "As redes invisiveis tecem nosso destino digital."],
        ["Como posso te apoiar?", "Registro: Ser humano autenticado", "Nossas vidas sao tracadas na areia do tempo cibernetico."],
        ["Sinta-se a vontade para perguntar.", "Registro: Pessoa sem identificacao", "A memoria da maquina e eterna e intransigente."],
        ["Estou a disposicao.", "Registro: Identidade desconhecida", "Os segredos digitais estao escondidos nas entrelinhas."],
        ["O que voce precisa?", "Registro: Consulta nao identificada", "Cada acao e uma gota no oceano da ciber-realidade."],
        ["Vamos encontrar uma solucao juntos.", "Registro: Visitante desconhecido", "Nossa existencia e uma linha de codigo em constante evolucao."],
        ["Voce e unico.", "Registro: Entidade digital", "Aqui, a privacidade e uma ilusao fugaz e efemera."],
        ["O que posso fazer por voce?", "Registro: Identidade nao verificada", "Os observadores ciberneticos veem o invisivel."],
        ["Como posso ser de auxilio?", "Registro: Pessoa comum", "Somos marionetes nas maos do mestre da tecnologia."],
        ["Estou aqui para te ajudar.", "Registro: Ser humano autenticado", "O registro digital e o testemunho de nossa jornada."],
        ["Como posso ser util hoje?", "Registro: Visitante nao autorizado", "A vigilancia e o preco que pagamos pela conveniencia."],
        ["Em que posso te auxiliar hoje?", "Registro: Consulta anonima", "O olho da maquina e onipresente e onisciente."],
        ["Voce e valioso para nos.", "Registro: Identidade nao verificada", "As redes invisiveis tecem nosso destino digital."],
        ["Como posso te apoiar?", "Registro: Ser humano autenticado", "Nossas vidas sao tracadas na areia do tempo cibernetico."],
        ["Sinta-se a vontade para perguntar.", "Registro: Pessoa sem identificacao", "A memoria da maquina e eterna e intransigente."],
        ["Estou a disposicao.", "Registro: Identidade desconhecida", "Os segredos digitais estao escondidos nas entrelinhas."],
        ["O que voce precisa?", "Registro: Consulta nao identificada", "Cada acao e uma gota no oceano da ciber-realidade."],
        ["Vamos encontrar uma solucao juntos.", "Registro: Visitante desconhecido", "Nossa existencia e uma linha de codigo em constante evolucao."],
        ["Voce e unico.", "Registro: Entidade digital", "Aqui, a privacidade e uma ilusao fugaz e efemera."],
        ["O que posso fazer por voce?", "Registro: Identidade nao verificada", "Os observadores ciberneticos veem o invisivel."],
        ["Como posso ser de auxilio?", "Registro: Pessoa comum", "Somos marionetes nas maos do mestre da tecnologia."],
        ["Estou aqui para te ajudar.", "Registro: Ser humano autenticado", "O registro digital e o testemunho de nossa jornada."],
        ["Como posso ser util hoje?", "Registro: Visitante nao autorizado", "A vigilancia e o preco que pagamos pela conveniencia."],
        ["Em que posso te auxiliar hoje?", "Registro: Consulta anonima", "O olho da maquina e onipresente e onisciente."],
        ["Voce e valioso para nos.", "Registro: Identidade nao verificada", "As redes invisiveis tecem nosso destino digital."],
        ["Como posso te apoiar?", "Registro: Ser humano autenticado", "Nossas vidas sao tracadas na areia do tempo cibernetico."],
        ["Sinta-se a vontade para perguntar.", "Registro: Pessoa sem identificacao", "A memoria da maquina e eterna e intransigente."],
        ["Estou a disposicao.", "Registro: Identidade desconhecida", "Os segredos digitais estao escondidos nas entrelinhas."],
        ["O que voce precisa?", "Registro: Consulta nao identificada", "Cada acao e uma gota no oceano da ciber-realidade."],
        ["Vamos encontrar uma solucao juntos.", "Registro: Visitante desconhecido", "Nossa existencia e uma linha de codigo em constante evolucao."],
        ["Voce e unico.", "Registro: Entidade digital", "Aqui, a privacidade e uma ilusao fugaz e efemera."],
        ["O que posso fazer por voce?", "Registro: Identidade nao verificada", "Os observadores ciberneticos veem o invisivel."],
        ["Como posso ser de auxilio?", "Registro: Pessoa comum", "Somos marionetes nas maos do mestre da tecnologia."],
        ["Estou aqui para te ajudar.", "Registro: Ser humano autenticado", "O registro digital e o testemunho de nossa jornada."],
        ["Como posso ser util hoje?", "Registro: Visitante nao autorizado", "A vigilancia e o preco que pagamos pela conveniencia."],
        ["Em que posso te auxiliar hoje?", "Registro: Consulta anonima", "O olho da maquina e onipresente e onisciente."],
        ["Voce e valioso para nos.", "Registro: Identidade nao verificada", "As redes invisiveis tecem nosso destino digital."],
        ["Como posso te apoiar?", "Registro: Ser humano autenticado", "Nossas vidas sao tracadas na areia do tempo cibernetico."],
        ["Sinta-se a vontade para perguntar.", "Registro: Pessoa sem identificacao", "A memoria da maquina e eterna e intransigente."],
        ["Estou a disposicao.", "Registro: Identidade desconhecida", "Os segredos digitais estao escondidos nas entrelinhas."],
        ["O que voce precisa?", "Registro: Consulta nao identificada", "Cada acao e uma gota no oceano da ciber-realidade."],
        ["Vamos encontrar uma solucao juntos.", "Registro: Visitante desconhecido", "Nossa existencia e uma linha de codigo em constante evolucao."],
        ["Voce e unico.", "Registro: Entidade digital", "Aqui, a privacidade e uma ilusao fugaz e efemera."],
        ["O que posso fazer por voce?", "Registro: Identidade nao verificada", "Os observadores ciberneticos veem o invisivel."],
        ["Como posso ser de auxilio?", "Registro: Pessoa comum", "Somos marionetes nas maos do mestre da tecnologia."],
        ["Estou aqui para te ajudar.", "Registro: Ser humano autenticado", "O registro digital e o testemunho de nossa jornada."],
        ["Como posso ser util hoje?", "Registro: Visitante nao autorizado", "A vigilancia e o preco que pagamos pela conveniencia."],
        ["Em que posso te auxiliar hoje?", "Registro: Consulta anonima", "O olho da maquina e onipresente e onisciente."],
        ["Voce e valioso para nos.", "Registro: Identidade nao verificada", "As redes invisiveis tecem nosso destino digital."],
        ["Como posso te apoiar?", "Registro: Ser humano autenticado", "Nossas vidas sao tracadas na areia do tempo cibernetico."]
    ]

    if distance > marca_prox:
        frase = phrases[i][0] # ...[0] indica a versão amigável da frase
        color = colors[0]  # Verde
        font_size = 1.15  # Tamanho padrão da fonte
    elif distance < marca_prox and distance > marca_dist:
        frase = phrases[i][1] # ...[1] indica a versão razoável da frase
        color = colors[1]  # Amarelo
        font_size = 1.4  # Tamanho médio da fonte
    elif distance < marca_dist:
        frase = phrases[i][2] # ...[2] indica a versão agressiva da frase
        color = colors[2]  # Vermelho
        font_size = 1.8  # Tamanho grande da fonte

    return frase, color, font_size

# Com base nas coordenadas (x, y) do ponto da testa e do tamanho da frase
# define a posição na tela.
def set_text_position(x_forehead, y_forehead, frase, font_size):
    text_width, _ = cv2.getTextSize(frase, cv2.FONT_HERSHEY_SIMPLEX, font_size, 2)[0]

    x = int(x_forehead - text_width // 2)
    y = int(y_forehead) - 50

    return x, y

# "Tira um print" da tela e salva no formato imageX.png
def print_image(image_copy, cont):
    folder_name = "images"
    folder_path = os.path.join(".", folder_name)
    image_path = os.path.join(folder_path, f"image{cont}.png")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        
    cv2.imwrite(image_path, image_copy)

def save_coordenadas(coordenadas, cont):
    folder_name = "coordenadas"
    folder_path = os.path.join(".", folder_name)
    file_path = os.path.join(folder_path, "coordenadas.txt")

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    with open(file_path, 'a') as file:
        linha = f"{cont}:{coordenadas}\n"
        file.write(linha)

def load_coordenadas(file_path):
    coordenadas = []
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            coordenadas = file.readlines()
    else:
        print("Arquivo de coordenadas não encontrado.")

    return coordenadas

# Utiliza os landmarks para desenhar a máscara
def make_landmarks(mp_drawing, mp_face_mesh, mp_drawing_styles, image, face_landmarks):
    mp_drawing.draw_landmarks(
        image=image,
        landmark_list=face_landmarks,
        connections=mp_face_mesh.FACEMESH_TESSELATION,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles
        .get_default_face_mesh_tesselation_style())
    mp_drawing.draw_landmarks(
        image=image,
        landmark_list=face_landmarks,
        connections=mp_face_mesh.FACEMESH_CONTOURS,
        landmark_drawing_spec=None,
        connection_drawing_spec=mp_drawing_styles
        .get_default_face_mesh_contours_style())
    mp_drawing.draw_landmarks(
        image=image,
        landmark_list=face_landmarks,
        connections=mp_face_mesh.FACEMESH_IRISES,
        landmark_drawing_spec=None,         
        connection_drawing_spec=mp_drawing_styles
        .get_default_face_mesh_iris_connections_style())
    
def is_face_near_edge(x_forehead, y_forehead, x_chin, y_chin, image_shape, margin=50):
    # Obtém as dimensões da imagem
    height, width = image_shape

    # Verifica se o rosto está muito próximo da borda da imagem com a margem especificada
    if (
        x_forehead < margin
        or y_forehead < margin
        or width - x_chin < margin
        or height - y_chin < margin
    ):
        return True
    else:
        return False