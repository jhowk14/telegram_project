from telethon import TelegramClient
import pandas as pd
from datetime import datetime, timedelta

# Substitua pelos seus próprios valores
api_id = "29149496"
api_hash = "7922ba58e7072444a0ab2e4636bf39ff"
group_name = "caveiratipsfree"

# Inicia o cliente do Telegram
client = TelegramClient("tete", api_id, api_hash)


# Função para extrair dados das mensagens
def extract_message_data(message_text):
    if not message_text:
        return None

    lines = message_text.split("\n")
    data = {}

    for line in lines:
        if line.startswith("📈"):
            parts = line.split("@")
            data["Aposta"] = parts[0].split("📈")[1].strip()
            data["Odds"] = parts[1].split(":")[0].strip()
            data["Evento"] = parts[1].split(":")[1].strip()
        elif line.startswith("🎮 Estratégia:"):
            data["Estratégia"] = line.split("Estratégia:")[1].strip()
        elif line.startswith("⚽ Liga:"):
            data["Liga"] = line.split("Liga:")[1].strip()
        elif line.startswith("🏟️ Tempo:"):
            data["Tempo"] = line.split("Tempo:")[1].strip()
        elif line.startswith("🪧 Placar:"):
            data["Placar"] = line.split("Placar:")[1].strip()
        elif line.startswith("📆"):
            data["Data"], data["Hora"] = line.split("📆")[1].strip().split(" - ")
        elif line.startswith("Placar final:"):
            data["Placar Final"] = line.split("Placar final:")[1].strip()
        elif (
            line.startswith("✅✅✅✅ Green")
            or line.startswith("🔄🔄🔄🔄 Reembolso")
            or line.startswith("❌❌❌❌ Red")
        ):
            data["Resultado"] = line.strip()
        elif line.startswith("Lucro:"):
            data["Lucro"] = line.split("Lucro:")[1].strip()

    return data


# Função para exibir o menu e selecionar o intervalo de datas
def get_date_range_option():
    print("Escolha o intervalo de datas:")
    print("1. Últimas 24 horas")
    print("2. Última semana")
    print("3. Último mês")
    print("4. Desde o início")

    choice = input("Digite o número da opção desejada: ")

    if choice == "1":
        return datetime.now() - timedelta(days=1)
    elif choice == "2":
        return datetime.now() - timedelta(weeks=1)
    elif choice == "3":
        return datetime.now() - timedelta(days=30)
    elif choice == "4":
        return None  # Sem limite de data
    else:
        print("Opção inválida. Selecionando 'Últimas 24 horas' por padrão.")
        return datetime.now() - timedelta(days=1)


async def main():
    await client.start()

    # Obtém o grupo pelo nome
    group = await client.get_entity(group_name)

    # Determina o intervalo de datas com base na escolha do usuário
    date_from = get_date_range_option()

    # Obtém todas as mensagens do grupo
    messages_data = []
    try:
        async for message in client.iter_messages(group):
            if message.message is None:
                continue  # Pular mensagens que não contêm texto

            message_date = message.date.replace(tzinfo=None)  # Remove o timezone

            if date_from and message_date < date_from:
                break

            message_data = extract_message_data(message.message)
            if message_data:
                messages_data.append(message_data)

    except Exception as e:
        print(f"Erro ocorrido: {e}")

    finally:
        # Cria um DataFrame com os dados extraídos
        df = pd.DataFrame(messages_data)

        # Salva em um arquivo Excel
        df.to_excel("telegram_messages.xlsx", index=False)

        print("Mensagens salvas com sucesso!")


with client:
    client.loop.run_until_complete(main())
