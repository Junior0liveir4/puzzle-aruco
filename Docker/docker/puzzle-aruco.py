import cv2
import time
import random
import numpy as np
import threading
import queue
import os
from sklearn.cluster import KMeans
from is_wire.core import Subscription, Message, Logger
from is_msgs.camera_pb2 import CameraConfig
from is_msgs.image_pb2 import Image
from streamChannel import StreamChannel

# === Configurações via Variáveis de Ambiente ===
game = os.environ.get('GAME_NAME', 'Demo')
broker_uri = os.environ.get('BROKER_URI', "amqp://guest:guest@10.10.2.211:30000")
camera_id = int(os.environ.get('CAMERA_ID', '5'))

log = Logger(name="PuzzleGame")

# === Funções de Conversão (Baseadas no rgb2gray.py) ===
def to_np(input_image):
    if isinstance(input_image, np.ndarray):
        return input_image
    elif isinstance(input_image, Image):
        buffer = np.frombuffer(input_image.data, dtype=np.uint8)
        return cv2.imdecode(buffer, flags=cv2.IMREAD_COLOR)
    return np.array([], dtype=np.uint8)

def to_image(input_image, encode_format='.jpeg', compression_level=0.5):
    if isinstance(input_image, np.ndarray):
        params = [cv2.IMWRITE_JPEG_QUALITY, int(compression_level * 100)]
        cimage = cv2.imencode(ext=encode_format, img=input_image, params=params)
        return Image(data=cimage[1].tobytes())
    return Image()

def puzzle_result(canal, result):
    msg_text = str(result)
    img_msg = Message()
    img_msg.body = msg_text.encode("utf-8")
    canal.publish(img_msg, topic='result')

# === Threads de Processamento ===
def receber_frames():
    channel = StreamChannel(broker_uri)
    subscription = Subscription(channel=channel)
    subscription.subscribe(topic=f'CameraGateway.{camera_id}.Frame')
    while True:
        msg = channel.consume()
        if isinstance(msg, bool): continue
        img = msg.unpack(Image)
        if not img.data: continue
        frame = to_np(img)
        if frame_queue.full():
            frame_queue.get_nowait()
        frame_queue.put_nowait(frame)

def processar_frames(id_map, imagens):
    pub_channel = StreamChannel(broker_uri)
    resize_scale = 0.4
    log.info(f"Iniciando processamento visual para o jogo: {game}")

    while True:
        try:
            frame_full = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        frame_small = cv2.resize(frame_full, None, fx=resize_scale, fy=resize_scale)
        gray = cv2.cvtColor(frame_small, cv2.COLOR_BGR2GRAY)
        markerCorners, markerIds, _ = detector.detectMarkers(gray)

        if markerIds is not None:
            for corners, marker_id in zip(markerCorners, markerIds.flatten()):
                numero_da_peca = id_map.get(int(marker_id))
                if numero_da_peca is not None:
                    overlay = imagens[numero_da_peca - 1]
                    if overlay is None: continue
                    h, w = overlay.shape[:2]
                    dst_pts = (corners[0] / resize_scale).astype(np.float32)
                    src_pts = np.array([[0, 0], [w-1, 0], [w-1, h-1], [0, h-1]], np.float32)
                    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
                    warped = cv2.warpPerspective(overlay, matrix, (frame_full.shape[1], frame_full.shape[0]))
                    mask = np.zeros((frame_full.shape[0], frame_full.shape[1]), dtype=np.uint8)
                    cv2.fillConvexPoly(mask, dst_pts.astype(np.int32), 255)
                    mask_3ch = cv2.merge([mask]*3)
                    frame_full = cv2.bitwise_and(frame_full, cv2.bitwise_not(mask_3ch))
                    frame_full = cv2.add(frame_full, cv2.bitwise_and(warped, mask_3ch))

        # Publica o frame processado para visualização no browser
        msg_out = Message()
        msg_out.pack(to_image(frame_full))
        pub_channel.publish(msg_out, topic=f"Puzzle.Frame.{camera_id}")

def verificar_grade(expected):
    local_channel = StreamChannel(broker_uri)
    last_match_state = None
    game_messages = {
        "Angry ArUcos": "angry-game-win", "PokéPuzzle GO!": "poke-game-win",
        "GTA: San Puzzle": "gta-game-win", "Super Mario Puzzle": "mario-game-win",
        "League of ArUcos": "lol-game-win"
    }

    while True:
        time.sleep(0.5)
        try:
            frame = frame_queue.get(timeout=1)
        except queue.Empty:
            continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        all_corners, ids, _ = detector.detectMarkers(gray)

        if ids is None or len(ids) < 15:
            continue

        # Lógica de Homografia e Grade (KMeans) mantida do original
        side_len = 150.0 
        output_size = (int(side_len * 10), int(side_len * 10))
        pts_src = all_corners[0][0]
        offset = np.array([output_size[0] / 2 - side_len / 2, output_size[1] / 2 - side_len / 2], dtype="float32")
        pts_dst = np.array([[offset[0], offset[1]], [offset[0] + side_len - 1, offset[1]],
                            [offset[0] + side_len - 1, offset[1] + side_len - 1], [offset[0], offset[1] + side_len - 1]], dtype="float32")
        
        matrix = cv2.getPerspectiveTransform(pts_src, pts_dst)
        warped_image = cv2.warpPerspective(frame, matrix, output_size)
        gray_warped = cv2.cvtColor(warped_image, cv2.COLOR_BGR2GRAY)
        warped_corners, warped_ids, _ = detector.detectMarkers(gray_warped)

        if warped_ids is not None and len(warped_ids) >= 15:
            grid_detectada = [[None for _ in range(4)] for _ in range(4)]
            warped_centers = np.array([c[0].mean(axis=0) for c in warped_corners])
            marker_ids_list = warped_ids.flatten()
            
            # Clusterização por linhas e colunas
            kmeans_rows = KMeans(n_clusters=4, random_state=0, n_init=10).fit(warped_centers[:, 1].reshape(-1, 1))
            row_map = {label: i for i, label in enumerate(np.argsort(kmeans_rows.cluster_centers_[:, 0]))}
            kmeans_cols = KMeans(n_clusters=4, random_state=0, n_init=10).fit(warped_centers[:, 0].reshape(-1, 1))
            col_map = {label: i for i, label in enumerate(np.argsort(kmeans_cols.cluster_centers_[:, 0]))}

            for i, m_id in enumerate(marker_ids_list):
                r, c = row_map[kmeans_rows.labels_[i]], col_map[kmeans_cols.labels_[i]]
                if 0 <= r < 4 and 0 <= c < 4: grid_detectada[r][c] = m_id

            match = (expected == grid_detectada)
            if match and last_match_state is not True:
                log.info("Sequência CORRETA detectada!")
                win_msg = game_messages.get(game, "1" if game == 'Demo' else "win")
                puzzle_result(local_channel, win_msg)
                last_match_state = True
            elif not match:
                last_match_state = False

# === Inicialização ===
if __name__ == '__main__':
    games_paths = {
        'Demo': "./Imagem1/", 'PokéPuzzle GO!': "./Imagem3/", 'Angry ArUcos': "./Imagem4/",
        'GTA: San Puzzle': "./Imagem5/", 'Super Mario Puzzle': "./Imagem6/", 'League of ArUcos': "./Imagem7/",
    }

    base_path = games_paths.get(game, "./Imagem1/")
    imagens = [cv2.imread(os.path.join(base_path, f"mapa_{i}.png")) for i in range(1, 16)]

    if game == 'Demo':
        expected = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, None]]
    else:
        numeros = list(range(1, 16))
        random.shuffle(numeros)
        numeros.append(None)
        expected = [numeros[i*4:(i+1)*4] for i in range(4)]

    id_para_peca_map = {}
    peca_numero = 1
    for r in range(4):
        for c in range(4):
            if peca_numero > 15: break
            id_aruco = expected[r][c]
            if id_aruco is not None: id_para_peca_map[id_aruco] = peca_numero
            peca_numero += 1

    detector = cv2.aruco.ArucoDetector(cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50))
    frame_queue = queue.Queue(maxsize=2)

    threading.Thread(target=receber_frames, daemon=True).start()
    threading.Thread(target=processar_frames, args=(id_para_peca_map, imagens), daemon=True).start()
    threading.Thread(target=verificar_grade, args=(expected,), daemon=True).start()

    while True: time.sleep(10)
