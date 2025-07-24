# filtro.py

PALAVROES = {
    "puta",
    "caralho",
    "merda",
    "porra",
    "bosta",
    "cu",
    "fodase",
    "foda-se",
    "fuder",
    "foda",
    "cacete",
    "cuzão",
    "buceta",
    "viado",
    "filho da puta",
    "filho da puta",
    "corno",
    "otario",
    "otário",
    "babaca",
    "idiota",
    "imbecil",
    "burro",
    "besta",
    "retardado",
    "retardada",
    "viado",
    "viado",
    "cabrão",
    "cabrao",
    "puta que pariu",
    "caralho",
    "arrombado",
    "viado",
    "pau no cu",
    "vai se foder",
    "vai tomar no cu",
    "vai tomar no **",
    "escroto",
    "escrota",
    "merdalhão",
    "fudido",
    "fudida",
    "piranha",
    "vagabunda",
    "vagabundo",
    "bucetinha",
    "cuzao",
    "boceta",
    "fuder",
    "fodendo",
    "fodido",
    "cuzinho",
    "xota",
    "xota",
    "rola",
    "rolinha",
    "porra nenhuma",
    "puta que pariu",
    "caralho",
    "desgraçado",
    "desgraçada",
    "cacete",
    "chupa",
    "chupador",
    "chupadora",
    "viado",
    "boiola",
    "bicha",
    "bicha do caralho",
    "caralho",
    "pau no rabo",
    "puta merda",
    "pqp",
    "fdp",
    "fdp",
    "filha da puta",
}

def censurar_mensagem(mensagem: str) -> tuple[str, bool]:
    """
    Substitui palavrões por *** e retorna a nova mensagem e se houve censura.
    """
    censurada = False
    palavras = mensagem.split()
    nova = []

    for palavra in palavras:
        limpa = palavra.lower().strip(".,!?")
        if limpa in PALAVROES:
            nova.append("***")
            censurada = True
        else:
            nova.append(palavra)

    return " ".join(nova), censurada
