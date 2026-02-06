import socket
import struct
import time
import sys
import hmac
import hashlib

NTP_SERVER_PADRAO = "a.st1.ntp.br"  # Servidor NTP padrão do Brasil
NTP_PORT = 123
NTP_EPOCH = 2208988800  # Epoch do NTP (começa em 1900)
CHAVE_SECRETA = b"senha_autenticacao"  # Chave compartilhada para autenticação HMAC

def criar_pacote_ntp(autenticado=False):
    """Cria um pacote NTP com os campos necessários. Se autenticado=True, adiciona HMAC."""
    
    pacote_ntp = struct.pack(
        "!B B B b 11I",  # Formato do pacote NTP (48 bytes)
        0b11100011,  
        # 11  100  011 -> 0b11100011  (227 em decimal)
        # Esse valor representa LI = 3, VN = 4, Mode = 3. 
        # LI = 3 -> Indica "não sincronizado" (padrão para clientes). 
        # VN = 4 -> Define que estou usando NTP versão 4. 
        # Mode = 3 -> Indica que esta é uma mensagem de cliente.
        
        0,  # Stratum (não usado pelo cliente)
        6,  # Poll Interval
        0,  # Precision
        0,  # Root Delay
        0,  # Root Dispersion
        0,  # Reference ID
        0, 0,  # Reference Timestamp
        0, 0,  # Originate Timestamp
        0, 0,  # Receive Timestamp
        int(time.time() + NTP_EPOCH), 0  # Transmit Timestamp
    )

    if autenticado:
        # Calcula HMAC-SHA256 para o pacote
        assinatura = hmac.new(CHAVE_SECRETA, pacote_ntp, hashlib.sha256).digest()
        return pacote_ntp + assinatura  # Anexa HMAC ao final
    
    return pacote_ntp

def verificar_hmac(mensagem, assinatura_recebida):
    """Verifica se a assinatura HMAC recebida é válida."""
    hmac_calculado = hmac.new(CHAVE_SECRETA, mensagem, hashlib.sha256).digest()
    return hmac.compare_digest(hmac_calculado, assinatura_recebida)

def obter_tempo_ntp(servidor, autenticado=False):
    """Obtém o horário sincronizado de um servidor NTP."""
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(5)  # Define um timeout de 5 segundos
        try:
            # Tempo local antes do envio do pacote
            t1_envio = time.time()
            sock.sendto(criar_pacote_ntp(autenticado), (servidor, NTP_PORT))
            
            dados, _ = sock.recvfrom(48 + (32 if autenticado else 0))  # Tamanho extra se autenticado
            t4_recebido = time.time()  # Tempo local ao receber a resposta

            if len(dados) < 48:
                raise ValueError("Resposta NTP inválida ou incompleta.")

            if autenticado:
                # Se for autenticado, separa a mensagem do HMAC recebido
                mensagem, assinatura_recebida = dados[:48], dados[48:]
                if not verificar_hmac(mensagem, assinatura_recebida):
                    raise ValueError("Falha na verificação HMAC: resposta não autenticada.")
                dados = mensagem  # Continua processando a mensagem NTP normal
            
            # Desempacota os dados NTP
            ntp_data = struct.unpack("!12I", dados)
            t2_recebido = ntp_data[8] - NTP_EPOCH  # Receive Timestamp
            t3_enviado = ntp_data[10] - NTP_EPOCH  # Transmit Timestamp

            # Cálculo do Round-Trip Delay (RTT)
            delay = (t4_recebido - t1_envio) - (t3_enviado - t2_recebido)

            # Cálculo do Offset (diferença de tempo entre cliente e servidor)
            offset = ((t2_recebido - t1_envio) + (t3_enviado - t4_recebido)) / 2

            # Ajusta o tempo local com base no offset
            hora_sincronizada = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t4_recebido + offset))
            
            return hora_sincronizada, delay, offset

        except Exception as e:
            return f"Erro ao obter hora NTP: {e}", None, None

if __name__ == "__main__":
    # Pergunta ao usuário se deseja usar um servidor oficial ou local
    escolha = input("Digite 1 para servidor oficial ou 0 para servidor local (com autenticação): ").strip()

    if escolha == "1":
        servidor_ntp = input("Informe o endereço do servidor oficial NTP (ou pressione Enter para usar o padrão): ").strip()
        if not servidor_ntp:  
            servidor_ntp = NTP_SERVER_PADRAO  # Usa o padrão se o usuário não informar nada
        autenticado = False  # Servidores oficiais não utilizam autenticação personalizada
    else:
        servidor_ntp = input("Informe o endereço do servidor local NTP: ").strip()
        autenticado = True  # Servidores locais exigem autenticação HMAC

    hora_atualizada, delay, offset = obter_tempo_ntp(servidor_ntp, autenticado)

    if delay is not None:
        print(f"Servidor NTP: {servidor_ntp}")
        print(f"Hora sincronizada: {hora_atualizada}")
        print(f"Round-Trip Delay (RTT): {delay:.6f} segundos")
        print(f"Offset calculado: {offset:.6f} segundos")
    else:
        print(f"Erro: {hora_atualizada}")
        print(f"Alternando para o servidor padrão ({NTP_SERVER_PADRAO})...")

        # Tenta novamente com o servidor padrão
        hora_atualizada, delay, offset = obter_tempo_ntp(NTP_SERVER_PADRAO)

        if delay is not None:
            print(f"Servidor NTP: {NTP_SERVER_PADRAO}")
            print(f"Hora sincronizada: {hora_atualizada}")
            print(f"Round-Trip Delay (RTT): {delay:.6f} segundos")
            print(f"Offset calculado: {offset:.6f} segundos")
        else:
            print("Erro: Não foi possível obter a hora de um servidor NTP válido.")
