# NTP Client and Server Implementation (RFC 5905)

Este projeto consiste na implementação manual de um cliente e um servidor NTP (Network Time Protocol), seguindo a especificação do NTPv4 definida na RFC 5905.

O sistema foi desenvolvido em Python, utilizando sockets UDP e construção manual de pacotes NTP, incluindo cálculo de offset e round-trip delay (RTT), além de suporte opcional à autenticação via HMAC-SHA256.

---

## 1. Objetivo do Projeto

O objetivo principal foi compreender e implementar o funcionamento interno do protocolo NTP, permitindo:

* Construção manual de pacotes NTP
* Comunicação via UDP na porta 123
* Cálculo de offset
* Cálculo de round-trip delay (RTT)
* Implementação opcional de autenticação HMAC-SHA256
* Testes com servidores NTP oficiais
* Testes de compatibilidade com o serviço Windows Time (w32time)

---

## 2. Fundamentação Teórica

A sincronização de tempo é fundamental para:

* Sistemas distribuídos
* Segurança de redes
* Registro de eventos (logs)
* Protocolos criptográficos
* Auditorias

O NTP utiliza uma arquitetura hierárquica cliente-servidor e baseia-se na troca de quatro timestamps para calcular:

* Offset (diferença entre relógios)
* Delay (tempo de ida e volta do pacote)

Baseado na RFC 5905.

---

## 3. Tecnologias Utilizadas

* Python
* Sockets UDP
* Biblioteca hashlib (HMAC-SHA256)
* Windows 10
* Testes com servidores oficiais NTP

---

## 4. Implementação

### 4.1 Cliente NTP

O cliente:

* Constrói manualmente o pacote NTP
* Define campos:

  * Leap Indicator (LI)
  * Version Number (VN)
  * Mode
* Envia requisição para servidor NTP
* Recebe resposta
* Calcula:

  * Offset
  * Round-trip delay (RTT)
* Exibe horário sincronizado

Também possui opção de autenticação HMAC-SHA256 para comunicação com servidor local.

---

### 4.2 Servidor NTP

O servidor:

* Escuta requisições via UDP
* Extrai timestamps enviados pelo cliente
* Gera timestamps de resposta
* Constrói pacote NTP válido
* Retorna resposta formatada

Opcionalmente:

* Valida HMAC
* Rejeita clientes não autorizados

---

## 5. Autenticação via HMAC-SHA256

Foi implementado mecanismo opcional de autenticação para:

* Garantir integridade da mensagem
* Impedir sincronização por clientes não autorizados
* Simular cenário de servidor NTP seguro

Cenários testados:

* Cliente autorizado: sincronização realizada com sucesso
* Cliente não autorizado: requisição rejeitada

---

## 6. Testes Realizados

### 6.1 Teste com Servidores Oficiais

O cliente foi testado com:

* a.st1.ntp.br

Resultados:

* Comunicação bem-sucedida
* Cálculo correto de offset
* Cálculo correto de RTT
* Sincronização precisa

---

### 6.2 Teste com Servidor Local

Testes realizados:

* Cliente customizado com autenticação
* Cliente Windows (w32tm)

O servidor mostrou compatibilidade com o serviço de tempo do Windows.

---

## 7. Aprendizados Técnicos

Este projeto permitiu aprofundar conhecimentos em:

* Protocolos de rede
* Comunicação via UDP
* Estrutura de pacotes binários
* Cálculo de sincronização temporal
* Implementação baseada em RFC
* Segurança com HMAC
* Testes de interoperabilidade com sistemas reais

---

## 8. Referências

KUROSE, J.; ROSS, K. Redes de Computadores e a Internet – Uma Abordagem Top Down.
TANENBAUM, A. Redes de Computadores.
COMER, D. Redes de Computadores e Internet.
RFC 5905 – Network Time Protocol Version 4 (NTPv4).

[https://datatracker.ietf.org/doc/html/rfc5905](https://datatracker.ietf.org/doc/html/rfc5905)
