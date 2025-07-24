
# IntraGhost

#  IntraGhost — Comunicação anônima. Rápida. Livre.

> Um chat em tempo real anônimo, direto na rede local ou privada, onde qualquer pessoa pode entrar, conversar e sair — sem rastros, sem contas, sem limites.

---

##  Sobre o Projeto

**ShadowChat** é um sistema de **chat descentralizado e anônimo** desenvolvido em **Python + Flask + Socket.IO**, ideal para comunicação privada em redes locais (intranet), ambientes isolados, CTFs ou projetos sigilosos.

> Criado com foco em **liberdade**, **velocidade** e **anonimato**.

---

## ⚙️ Funcionalidades

✅ Criar ou entrar em qualquer sala de bate-papo  
✅ Comunicação em tempo real via WebSockets  
✅ Sem login, sem cadastro — apenas um nome aleatório ou apelido  
✅ Interface minimalista e dark (modo hacker)  
✅ Suporte a múltiplas salas simultâneas  
✅ Mensagens com marcação de horário e ID do usuário  
✅ Compatível com redes locais/offline  
✅ Armazena histórico local opcionalmente (via JSON ou SQLite)

---

## 🧱 Tecnologias Utilizadas

- [Python 3.10+](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [HTML5 + CSS3](https://developer.mozilla.org/en-US/docs/Web)
- [JavaScript](https://developer.mozilla.org/en-US/docs/Web/JavaScript)

---

## 📦 Como Rodar Localmente

### 1. Clone o repositório

```bash
git clone https://github.com/seuusuario/shadowchat.git
cd shadowchat

Instale os requisitos
Copiar
Editar
pip install -r requirements.txt
3. Inicie o servidor
bash
Copiar
Editar
python app.py
Ou com Waitress:
Copiar
Editar
python run_waitress.py
4. Acesse no navegador:
arduino
Copiar
Editar
http://localhost:5000
Se estiver em rede local, outros dispositivos podem acessar pelo IP da máquina (ex: http://192.168.0.10:5000)

📦 shadowchat/
├── app.py               # Servidor principal com Flask + SocketIO
├── run_waitress.py      # Versão com Waitress para produção
├── mensagens.json       # Armazena mensagens localmente (opcional)
├── templates/
│   └── index.html       # Interface do chat
└── static/
    └── style.css        # Estilo visual dark

🔐 Privacidade & Segurança
Nenhum dado pessoal é armazenado

Chat pode ser executado sem internet

Histórico é opcional e pode ser desativado

Projeto open-source: audite à vontade

🌌 Exemplos de Uso
Empresas com redes internas

Hackathons / CTFs

Ambientes escolares/universitários

Ambientes onde privacidade importa

Comunidades descentralizadas

🧠 Contribuindo
Contribuições são bem-vindas!
Forke, abra uma issue ou envie um PR.

📜 Licença
Este projeto está sob a licença MIT.

🕳️ Disclaimer
Este sistema foi criado para fins educacionais e uso ético apenas. Não nos responsabilizamos pelo uso indevido.

💬 Contato
Se quiser trocar ideias ou contribuir, me chama no Discord ou GitHub!

yaml
Copiar
Editar

