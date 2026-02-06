import socket
import struct
import time
import hmac
import hashlib

NTP_PORT = 123
NTP_EPOCH = 2208988800  # Epoch do NTP (começa em 1900)
STRATUM = 2  # Define o nível hierárquico do servidor NTP
CHAVE_SECRETA = b"senha_autenticacao"  # Chave compartilhada para autenticação HMAC

def criar_pacote_resposta(receive_timestamp, client_transmit_timestamp, autenticado=False):
    """Cria um pacote NTP de resposta baseado na requisição do cliente.
       Se autenticado=True, adiciona HMAC-SHA256 na resposta.
    """
    transmit_timestamp = int(time.time() + NTP_EPOCH)

    pacote_ntp = struct.pack(
        "!B B B b 11I",
        0b00100100,  # Leap Indicator (0), Versão (4), Modo (4 = Servidor)
        STRATUM,  # Stratum (nível hierárquico do servidor)
        6,  # Poll Interval
        0,  # Precision
        0,  # Root Delay
        0,  # Root Dispersion
        0x4C4F434C,  # Reference ID (pode ser alterado)
        transmit_timestamp, 0,  # Reference Timestamp
        receive_timestamp, 0,  # Originate Timestamp (enviado pelo cliente)
        int(time.time() + NTP_EPOCH), 0,  # Receive Timestamp
        transmit_timestamp, 0  # Transmit Timestamp (hora do servidor)
    )

    if autenticado:
        # Adiciona HMAC-SHA256 ao pacote
        assinatura = hmac.new(CHAVE_SECRETA, pacote_ntp, hashlib.sha256).digest()
        return pacote_ntp + assinatura  # Anexa HMAC ao final
    
    return pacote_ntp

def verificar_hmac(mensagem, assinatura_recebida):
    """Verifica se a assinatura HMAC recebida é válida."""
    hmac_calculado = hmac.new(CHAVE_SECRETA, mensagem, hashlib.sha256).digest()
    return hmac.compare_digest(hmac_calculado, assinatura_recebida)

def iniciar_servidor_ntp(port=NTP_PORT, autenticado=False):
    """Inicia um servidor NTP que responde a requisições de clientes.
       Se autenticado=True, verifica e adiciona HMAC nos pacotes.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.bind(("0.0.0.0", port))  # Escuta em todas as interfaces de rede
        tipo_servidor = "local (com autenticação)" if autenticado else "oficial (sem autenticação)"
        print(f"Servidor NTP rodando na porta {port} - Modo: {tipo_servidor}")

        while True:
            dados, endereco = sock.recvfrom(48 + (32 if autenticado else 0))  # Espera pacote maior se autenticado
            receive_timestamp = int(time.time() + NTP_EPOCH)  # Tempo ao receber a requisição

            if len(dados) < 48:
                print(f"Pacote inválido recebido de {endereco}")
                continue

            if autenticado:
                # Se for autenticado, separa a mensagem do HMAC recebido
                mensagem, assinatura_recebida = dados[:48], dados[48:]
                if not verificar_hmac(mensagem, assinatura_recebida):
                    print(f"Falha na verificação HMAC de {endereco}. Ignorando requisição.")
                    continue
                dados = mensagem  # Continua processando a mensagem NTP normal
            
            # Extrai o Originate Timestamp (enviado pelo cliente)
            client_transmit_timestamp = struct.unpack("!12I", dados)[10]

            # Cria e envia a resposta
            resposta = criar_pacote_resposta(receive_timestamp, client_transmit_timestamp, autenticado)
            sock.sendto(resposta, endereco)
            print(f"Resposta enviada para {endereco}")

if __name__ == "__main__":
    # Pergunta ao usuário se deseja iniciar um servidor oficial ou local (com autenticação)
    escolha = input("Digite 1 para servidor oficial ou 0 para servidor local (com autenticação): ").strip()
    
    if escolha == "1":
        autenticado = False  # Servidor oficial não usa autenticação HMAC
    else:
        autenticado = True  # Servidor local exige autenticação HMAC

    iniciar_servidor_ntp(autenticado=autenticado)
