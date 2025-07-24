import os
import json
import random
import string
import hashlib
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO, join_room, emit
from openai import OpenAI
from filtro import censurar_mensagem
from music_bot import extract_query, find_youtube_embed

app = Flask(__name__)
app.secret_key = "intranet_chat_secret"
socketio = SocketIO(app, cors_allowed_origins="*")

# Configure sua chave de API do OpenAI aqui (ou via variável ambiente)
API_KEY = os.getenv("OPENAI_API_KEY") or "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"
client = OpenAI(api_key=API_KEY)

DATA_FILE = "mensagens.json"

def gerar_nick():
    random_str = f"{datetime.now().timestamp()}_{random.randint(0, 999999)}"
    return hashlib.md5(random_str.encode()).hexdigest()[:8]

def gerar_chave(tamanho=12):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho))

def gerar_id_sala(tamanho=6):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(tamanho))

def carregar_salas():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Corrige salas antigas sem id, mensagens, chave
            for sala_nome, sala_data in data.items():
                if "id" not in sala_data:
                    sala_data["id"] = gerar_id_sala()
                if "mensagens" not in sala_data:
                    sala_data["mensagens"] = []
                if "privada" not in sala_data:
                    sala_data["privada"] = False
                if "chave" not in sala_data:
                    sala_data["chave"] = None
            return data
    else:
        # Cria sala geral padrão
        return {
            "geral": {
                "id": "geral01",
                "mensagens": [],
                "privada": False,
                "chave": None
            }
        }

def salvar_mensagens():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(salas, f, ensure_ascii=False, indent=4)

salas = carregar_salas()
# Rota principal com render_template_string do HTML que você vai colocar depois
@app.route("/")
def index():
    username = gerar_nick()
    return render_template_string(
        '''<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Chat com Gemini</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      background: url('https://wallpapercave.com/wp/wp12195644.jpg') no-repeat center center fixed;
      background-size: cover;
      font-family: "Segoe UI", sans-serif;
      color: #fff;
      display: flex;
      height: 100vh;
      overflow: hidden;
    }
    
    #sidebar {
      width: 300px;
      background: rgba(32, 34, 37, 0.95);
      padding: 20px;
      overflow-y: auto;
      display: flex;
      flex-direction: column;
      z-index: 2;
    }
    #chat-container {
      flex: 1;
      display: none; /* só aparece depois que entrar numa sala */
      flex-direction: column;
      z-index: 2;
      position: relative;
    }
    #chat {
      flex: 1;
      padding: 20px;
      overflow-y: auto;
      background: rgba(47, 49, 54, 0.6);
      display: flex;
      flex-direction: column;
      gap: 10px;
      position: relative;
      z-index: 2;
    }
    .mensagem {
      display: flex;
      align-items: center;
      gap: 10px;
    }
    .avatar {
      width: 40px;
      height: 40px;
      border-radius: 50%;
      color: white;
      font-weight: bold;
      display: flex;
      align-items: center;
      justify-content: center;
      user-select: none;
      flex-shrink: 0;
      font-size: 18px;
      text-transform: uppercase;
    }
    .texto {
      background: rgba(32, 34, 37, 0.8);
      padding: 10px 15px;
      border-radius: 10px;
      max-width: 70%;
      word-wrap: break-word;
    }
    #message-box {
      display: flex;
      background: rgba(64, 68, 75, 0.9);
      padding: 10px;
      z-index: 2;
    }
    #message {
      flex: 1;
      padding: 10px;
      border: none;
      background: rgba(47, 49, 54, 0.9);
      color: #fff;
      font-size: 16px;
    }
    #send {
      background: #7289da;
      border: none;
      color: white;
      padding: 10px 15px;
      cursor: pointer;
      font-size: 16px;
    }
    .sala-btn {
      background: #36393f;
      color: #fff;
      border: none;
      padding: 10px;
      width: 100%;
      margin-bottom: 10px;
      text-align: left;
      cursor: pointer;
      font-size: 16px;
    }
    .sala-btn:hover {
      background: #4f545c;
    }
    form {
      margin-bottom: 15px;
    }
    label {
      display: block;
      margin: 8px 0 4px 0;
      font-weight: bold;
    }
    input[type="text"], select {
      width: 100%;
      padding: 6px;
      margin-bottom: 8px;
      border-radius: 4px;
      border: none;
      font-size: 14px;
    }
    button {
      background: #7289da;
      border: none;
      color: white;
      padding: 8px 12px;
      cursor: pointer;
      font-size: 14px;
      border-radius: 4px;
    }
    #form-criar-sala {
      display: flex;
      flex-direction: column;
      gap: 10px;
      margin-bottom: 20px;
    }
    #chave-privada-container {
      background: #2f3136;
      padding: 10px;
      margin-top: 10px;
      border-radius: 6px;
      word-break: break-word;
      font-weight: bold;
      user-select: all;
      color: #0f0;
      border: 1px dashed #0f0;
      display: none;
    }

    /* Botão Gemini */
    #botao-gemini {
      position: fixed;
      bottom: 100px;
      right: 25px;
      width: 60px;
      height: 60px;
      border-radius: 50%;
      background: #000;
      border: none;
      cursor: pointer;
      box-shadow: 0 0 15px 3px rgba(0,0,0,0.7);
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      transition: transform 0.3s ease;
      z-index: 20;
      overflow: hidden;
    }
    #botao-gemini img {
      width: 40px;
      height: 40px;
      user-select: none;
      pointer-events: none;
      filter: invert(1);
      object-fit: contain;
      display: block;
    }
    #botao-gemini:hover {
      transform: scale(1.2);
      box-shadow: 0 0 25px 5px #60a5fa;
    }
    @keyframes bounce {
      0%, 100% { transform: scale(1); }
      50% { transform: scale(1.3); }
    }
    #botao-gemini.animating {
      animation: bounce 0.4s ease forwards;
    }

    /* Gemini sidebar */
    #gemini-sidebar {
      position: fixed;
      top: 0;
      right: -400px;
      width: 400px;
      height: 100vh;
      background: rgba(32, 34, 37, 0.95);
      box-shadow: -3px 0 15px rgba(0,0,0,0.5);
      padding: 20px;
      display: flex;
      flex-direction: column;
      transition: right 0.4s ease;
      z-index: 25;
      color: #fff;
    }
    body.gemini-active #gemini-sidebar {
      right: 0;
    }
    #gemini-chat {
      flex: 1;
      overflow-y: auto;
      margin-bottom: 10px;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }
    #gemini-input {
      padding: 10px;
      border-radius: 5px;
      border: none;
      font-size: 16px;
      width: 100%;
      box-sizing: border-box;
      background: rgba(47, 49, 54, 0.8);
      color: white;
    }
    #gemini-send {
      background: #7289da;
      border: none;
      color: white;
      padding: 10px 15px;
      margin-top: 10px;
      cursor: pointer;
      font-size: 16px;
      border-radius: 5px;
      align-self: flex-end;
    }
  </style>
</head>
<body>
  <div id="sidebar" role="navigation" aria-label="Lista de salas">
    <h3>Salas Existentes</h3>

    <label for="busca-salas" style="margin-bottom:8px; font-weight:bold;">Buscar Sala (nome ou ID)</label>
    <input type="text" id="busca-salas" placeholder="Digite nome ou ID da sala..." autocomplete="off" />

    <!-- Loop de salas do Flask -->
    {% for nome, sala in salas.items() %}
      <button class="sala-btn" onclick="entrarSalaPrompt('{{ nome }}', {{ 'true' if sala['privada'] else 'false' }})" data-nome="{{ nome }}" data-id="{{ sala['id'] }}">
        {{ nome }} (ID: {{ sala['id'] }}) {% if sala['privada'] %}(Privada){% endif %}
      </button>
    {% endfor %}

    <hr />

    <!-- Adicione dentro do seu <div id="sidebar">, abaixo de "Criar Sala" -->
<h3>Escolher Wallpaper</h3>
<select id="seletor-wallpaper" onchange="alterarWallpaper()" style="margin-bottom: 15px;">
  <option value="https://wallpapers.com/images/hd/tokyo-ghoul-dark-anime-aesthetic-desktop-sm9shfcpesqr4m4h.jpg">Kaneki</option>
  <option value="https://wallpaper-house.com/data/out/8/wallpaper2you_256424.jpg">Anime-Lofi</option>
  <option value="https://wallpapers.com/images/hd/goku-4k-ultra-hd-on-white-wall-pwsjrujt5i0hwjqr.jpg">Goku</option>
  <option value="https://wallpapercave.com/wp/wp6558336.jpg">White-Anime</option>
  <option value="https://wallpapers.com/images/featured/black-and-white-anime-c6diyqi5z2j4o559.jpg">White-Clean</option>
 <option value="https://rare-gallery.com/mocahbig/391691-anime-girl-white-hair-red-eye-mask-art-4k-pc.jpg">White/Red-Clean</option>
  </select>




    <h3>Criar Sala</h3>
    <form id="form-criar-sala" onsubmit="criarSala(event)" aria-label="Criar uma nova sala">
      <label for="nome-sala">Nome da Sala</label>
      <input type="text" id="nome-sala" placeholder="Digite o nome da sala" required minlength="1" maxlength="20" autocomplete="off" />

      <label for="tipo-sala">Tipo de Sala</label>
      <select id="tipo-sala" required>
        <option value="publica" selected>Pública</option>
        <option value="privada">Privada</option>
      </select>

      <button type="submit">Criar</button>
    </form>

    <div id="chave-privada-container" title="Chave da sala privada (compartilhe com quem quiser)">
      <strong>Chave da Sala Privada:</strong> <span id="chave-privada"></span>
    </div>
  </div>

  <div id="chat-container" role="main" aria-live="polite" aria-atomic="false">
    <h2>Chat - Sala: <span id="nome-sala-atual"></span></h2>
    <div id="chat" tabindex="0" aria-label="Mensagens do chat"></div>

    <div id="message-box">
      <input id="message" placeholder="Digite sua mensagem..." autocomplete="off" aria-label="Digite sua mensagem" />
      <button id="send" aria-label="Enviar mensagem">Enviar</button>
    </div>
  </div>

  <!-- Botão Gemini flutuante -->
  <button id="botao-gemini" title="Ativar modo Gemini" aria-label="Ativar modo Gemini">
    <img src="https://static.vecteezy.com/system/resources/thumbnails/044/185/680/small_2x/star-sparkle-icon-futuristic-shapes-christmas-stars-icons-flashes-from-fireworks-png.png" alt="Gemini IA" />
  </button>

  <!-- Sidebar Gemini -->
  <aside id="gemini-sidebar" aria-label="Chat da inteligência artificial Gemini" role="complementary" aria-hidden="true">
    <div id="gemini-chat" aria-live="polite" aria-atomic="false"></div>
    <input id="gemini-input" placeholder="Digite sua pergunta para Gemini..." autocomplete="off" aria-label="Digite sua pergunta para Gemini" />
    <button id="gemini-send" aria-label="Enviar pergunta para Gemini">Enviar</button>
  </aside>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
  <script>
    const socket = io();
    let salaAtual = null;
    let username = "{{ username }}";

    // Elementos principais
    const chatContainer = document.getElementById('chat-container');
    const chat = document.getElementById('chat');
    const messageInput = document.getElementById('message');
    const sendButton = document.getElementById('send');

    // Gemini
    const botaoGemini = document.getElementById('botao-gemini');
    const geminiSidebar = document.getElementById('gemini-sidebar');
    const geminiChat = document.getElementById('gemini-chat');
    const geminiInput = document.getElementById('gemini-input');
    const geminiSend = document.getElementById('gemini-send');

    let modoGemini = false;

    // Toggle Gemini sidebar
    botaoGemini.addEventListener('click', () => {
      modoGemini = !modoGemini;

      if (modoGemini) {
        document.body.classList.add('gemini-active');
        geminiSidebar.setAttribute('aria-hidden', 'false');
        geminiInput.focus();
      } else {
        document.body.classList.remove('gemini-active');
        geminiSidebar.setAttribute('aria-hidden', 'true');
        geminiInput.value = '';
        geminiChat.innerHTML = '';
      }
    });

    geminiSend.addEventListener('click', enviarPerguntaGemini);
    geminiInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') enviarPerguntaGemini();
    });

    async function enviarPerguntaGemini() {
      const pergunta = geminiInput.value.trim();
      if (!pergunta) return;

      adicionarMensagemGemini({ username: username, msg: pergunta });
      geminiInput.value = '';
      geminiInput.disabled = true;
      geminiSend.disabled = true;

      try {
        const resp = await fetch('/gemini_api', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ pergunta })
        });
        const data = await resp.json();
        adicionarMensagemGemini({ username: 'Gemini', msg: data.resposta || 'Sem resposta da IA.' });
      } catch (err) {
        adicionarMensagemGemini({ username: 'Gemini', msg: 'Erro ao conectar com a IA.' });
      } finally {
        geminiInput.disabled = false;
        geminiSend.disabled = false;
        geminiInput.focus();
      }
    }

    function adicionarMensagemGemini(data) {
      const msgDiv = document.createElement('div');
      msgDiv.classList.add('mensagem');
      const avatar = criarAvatar(data.username);
      msgDiv.appendChild(avatar);
      const texto = document.createElement('div');
      texto.classList.add('texto');
      texto.innerHTML = `<strong>${data.username}:</strong> ${data.msg}`;
      msgDiv.appendChild(texto);
      geminiChat.appendChild(msgDiv);
      geminiChat.scrollTop = geminiChat.scrollHeight;
    }

    // Funções salas e chat

    sendButton.addEventListener('click', enviarMensagem);
    messageInput.addEventListener('keydown', e => {
      if (e.key === 'Enter') enviarMensagem();
    });

    async function entrarSalaPrompt(nomeSala, isPrivada) {
      if (isPrivada) {
        const chave = prompt("Esta sala é privada. Por favor, digite a chave:");
        if (chave === null) return;
        entrarSalaPorNome(nomeSala, chave);
      } else {
        entrarSalaPorNome(nomeSala);
      }
    }

    function entrarSalaPorNome(nomeSala, chave = null) {
      fetch("/validar_entrada", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sala: nomeSala, chave: chave })
      })
      .then(res => res.json())
      .then(data => {
        if (data.sucesso) {
          salaAtual = nomeSala;
          mostrarChat();
          socket.emit("entrar", { sala: salaAtual, username: username });
        } else {
          alert("Chave inválida ou sala não existe!");
        }
      });
    }

    function mostrarChat() {
      chatContainer.style.display = "flex";
      document.getElementById("nome-sala-atual").textContent = salaAtual;
      chat.innerHTML = "";
    }

    function criarSala(e) {
      e.preventDefault();
      const nomeSala = document.getElementById("nome-sala").value.trim();
      const tipoSala = document.getElementById("tipo-sala").value;

      fetch("/criar_sala", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome: nomeSala, tipo: tipoSala })
      }).then(res => res.json()).then(data => {
        if (data.sucesso) {
          if (data.privada) {
            const divChave = document.getElementById("chave-privada-container");
            divChave.style.display = "block";
            document.getElementById("chave-privada").textContent = data.chave;
          } else {
            alert("Sala pública criada com sucesso!");
            location.reload();
          }
        } else {
          alert("Erro ao criar sala: " + data.msg);
        }
      });
    }

    socket.on("historico", data => carregarMensagens(data.mensagens));
    socket.on("mensagem", data => adicionarMensagem(data));

    function carregarMensagens(mensagens) {
  chat.innerHTML = "";
  mensagens.forEach(m => adicionarMensagem(m));
  scrollToBottom();
}

    function adicionarMensagem(data) {
      const container = document.createElement("div");
      container.classList.add("mensagem");

      const avatar = criarAvatar(data.username);
      container.appendChild(avatar);

      const texto = document.createElement("div");
      texto.classList.add("texto");
      texto.innerHTML = `<strong>${data.username}:</strong> ${data.msg}`;
      container.appendChild(texto);

      chat.appendChild(container);
      scrollToBottom();
    }

    function criarAvatar(nick) {
      const letra = nick.charAt(0).toUpperCase();
      let hash = 0;
      for (let i = 0; i < nick.length; i++) {
        hash = nick.charCodeAt(i) + ((hash << 5) - hash);
      }
      const color = `hsl(${hash % 360}, 70%, 50%)`;
      const div = document.createElement("div");
      div.classList.add("avatar");
      div.style.backgroundColor = color;
      div.textContent = letra;
      return div;
    }

    function scrollToBottom() {
      chat.scrollTop = chat.scrollHeight;
    }

    async function enviarMensagem() {
      const texto = messageInput.value.trim();
      if (!texto || !salaAtual) return;

      socket.emit("mensagem", { msg: texto, sala: salaAtual, username: username });
      messageInput.value = "";
    }

    // Filtra salas na lista conforme busca
    document.getElementById("busca-salas").addEventListener("input", e => {
      const termo = e.target.value.toLowerCase();
      const btns = document.querySelectorAll(".sala-btn");
      btns.forEach(btn => {
        const nome = btn.dataset.nome.toLowerCase();
        const id = btn.dataset.id.toLowerCase();
        btn.style.display = (nome.includes(termo) || id.includes(termo)) ? "block" : "none";
      });
    });

    // Form criar sala
    document.getElementById("form-criar-sala").addEventListener("submit", criarSala);
  
  // Wallpaper dinâmico
  function alterarWallpaper() {
    const seletor = document.getElementById("seletor-wallpaper");
    const url = seletor.value;
    document.body.style.backgroundImage = `url('${url}')`;
    localStorage.setItem("wallpaper", url);
  }

  // Carrega wallpaper salvo
  window.addEventListener("load", () => {
    const wallpaperSalvo = localStorage.getItem("wallpaper");
    const seletor = document.getElementById("seletor-wallpaper");
    if (wallpaperSalvo) {
      document.body.style.backgroundImage = `url('${wallpaperSalvo}')`;
      for (let i = 0; i < seletor.options.length; i++) {
        if (seletor.options[i].value === wallpaperSalvo) {
          seletor.selectedIndex = i;
          break;
        }
      }
    }
  });
  </script>
</body>
</html>

''',
        salas=salas,
        username=username
    )

@app.route("/criar_sala", methods=["POST"])
def criar_sala():
    data = request.get_json()
    nome = data.get("nome", "").strip()
    tipo = data.get("tipo", "publica")

    if not nome:
        return jsonify({"sucesso": False, "msg": "Nome da sala é obrigatório."})
    if nome in salas:
        return jsonify({"sucesso": False, "msg": "Sala já existe."})

    id_sala = gerar_id_sala()
    privada = (tipo == "privada")
    chave = gerar_chave() if privada else None

    salas[nome] = {
        "id": id_sala,
        "mensagens": [],
        "privada": privada,
        "chave": chave
    }
    salvar_mensagens()

    return jsonify({"sucesso": True, "privada": privada, "chave": chave})

@app.route("/validar_entrada", methods=["POST"])
def validar_entrada():
    data = request.get_json()
    nome = data.get("sala", "")
    chave = data.get("chave", None)

    if nome not in salas:
        return jsonify({"sucesso": False, "msg": "Sala não encontrada."})

    sala = salas[nome]
    if sala["privada"] and chave != sala["chave"]:
        return jsonify({"sucesso": False, "msg": "Chave inválida."})

    return jsonify({"sucesso": True})

@app.route("/gemini_api", methods=["POST"])
def gemini_api():
    data = request.get_json()
    pergunta = data.get("pergunta", "").strip()

    if not pergunta:
        return jsonify({"resposta": "Por favor, envie uma pergunta válida."})

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": pergunta}],
            temperature=0.7,
            max_tokens=200
        )
        resposta = completion.choices[0].message.content
    except Exception as e:
        print("Erro OpenAI:", e)
        resposta = "Erro ao processar a resposta da IA."

    return jsonify({"resposta": resposta})

@socketio.on("entrar")
def handle_entrar(data):
    sala = data.get("sala")
    username = data.get("username")
    if not sala or sala not in salas:
        return
    join_room(sala)
    emit("historico", {"mensagens": salas[sala].get("mensagens", [])}, to=request.sid)

    sistema_msg = {"username": "Sistema", "msg": f"{username} entrou na sala."}
    salas[sala].setdefault("mensagens", []).append(sistema_msg)
    salvar_mensagens()

    emit("mensagem", sistema_msg, to=sala)

@socketio.on("mensagem")
def handle_mensagem(data):
    sala = data.get("sala")
    username = data.get("username")
    msg = data.get("msg")

    if not sala or sala not in salas or not username or not msg:
        return

    # Aplica censura (garanta que retorne string)
    msg_censurada = censurar_mensagem(msg)
    if isinstance(msg_censurada, tuple):
        msg_censurada = msg_censurada[0]

    # Verifica comando /music
    query = extract_query(msg_censurada)
    if query:
        url_embed = find_youtube_embed(query)
        if url_embed:
            mensagem_video = {
                "username": "MusicBot",
                "msg": (
                    f"🎵 Música solicitada por {username}:<br>"
                    f"<iframe width='300' height='170' src='{url_embed}' "
                    f"frameborder='0' allow='autoplay; encrypted-media' allowfullscreen></iframe>"
                ),
                "timestamp": datetime.now().isoformat()
            }
            salas[sala].setdefault("mensagens", []).append(mensagem_video)
            salvar_mensagens()
            emit("mensagem", mensagem_video, to=sala)
        else:
            mensagem_erro = {
                "username": "MusicBot",
                "msg": f"Não encontrei nenhum resultado para: {query}",
                "timestamp": datetime.now().isoformat()
            }
            salas[sala].setdefault("mensagens", []).append(mensagem_erro)
            salvar_mensagens()
            emit("mensagem", mensagem_erro, to=sala)
        return  # não enviar a mensagem original

    # Mensagem comum
    mensagem = {
        "username": username,
        "msg": msg_censurada,
        "timestamp": datetime.now().isoformat()
    }
    salas[sala].setdefault("mensagens", []).append(mensagem)
    salvar_mensagens()
    emit("mensagem", mensagem, to=sala)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)