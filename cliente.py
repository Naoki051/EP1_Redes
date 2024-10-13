import socket
import threading

# Variável global para sinalizar o encerramento da conexão
# Usada para interromper o loop principal e a thread de recebimento de mensagens.
encerrar_conexao = False  

def criar_socket():
    return socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def conectar_servidor(cliente_socket, host, port):
    try:
        cliente_socket.connect((host, port))
        print("Conectado ao servidor de adivinhação.")
    except Exception as e:
        print(f"Erro ao conectar ao servidor: {e}")
        raise e  # Lança a exceção para ser tratada pelo chamador.

def receber_mensagens(cliente_socket):
    global encerrar_conexao
    while not encerrar_conexao:
        try:
            resposta = cliente_socket.recv(1024).decode()
            if not resposta or resposta.upper() == "/DESCONECTAR":
                print("Servidor solicitou desconexão.")
                encerrar_conexao = True  # Sinaliza para encerrar o loop no cliente.
                break
            print(f"Servidor: {resposta}")
        except ConnectionResetError:
            print("Conexão com o servidor encerrada.")
            encerrar_conexao = True
            break
        except Exception as e:
            if not encerrar_conexao:
                print(f"Erro ao receber mensagem: {e}")
            break

def iniciar_thread_recebimento(cliente_socket):
    thread_receber = threading.Thread(target=receber_mensagens, args=(cliente_socket,))
    thread_receber.start()
    return thread_receber

def enviar_mensagens(cliente_socket):
    global encerrar_conexao
    while not encerrar_conexao:
        mensagem = input()  # Aguarda a mensagem do usuário.
        if mensagem.upper() == "/DESCONECTAR":
            encerrar_conexao = True  # Sinaliza para encerrar a conexão.
            cliente_socket.sendall(mensagem.encode())  # Envia o comando de desconexão ao servidor.
            break
        cliente_socket.sendall(mensagem.encode())  # Envia a mensagem ao servidor.

def fechar_socket(cliente_socket):
    global encerrar_conexao
    encerrar_conexao = True  # Garante que o loop e a thread sejam finalizados.
    try:
        cliente_socket.shutdown(socket.SHUT_RDWR)
    except Exception as e:
        print(f"Erro ao tentar encerrar o socket: {e}")
    finally:
        cliente_socket.close()

def start_client(host='localhost', port=12345):
    cliente_socket = criar_socket()
    try:
        conectar_servidor(cliente_socket, host, port)

        # Inicia a thread de recebimento de mensagens
        thread_receber = iniciar_thread_recebimento(cliente_socket)

        # Inicia o envio de mensagens
        enviar_mensagens(cliente_socket)

        # Espera a thread de recebimento terminar
        thread_receber.join()

    except KeyboardInterrupt:
        print("\nFechando conexão.")
        encerrar_conexao = True
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        fechar_socket(cliente_socket)  # Garante que o socket seja fechado no final.
        print("Conexão encerrada.")

if __name__ == "__main__":
    start_client()  # Inicia o cliente.
