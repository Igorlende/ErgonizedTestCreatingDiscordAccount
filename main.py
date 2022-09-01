from bot import DiscordBot


def input_data() -> tuple:
    while True:
        email = input("email=")
        if DiscordBot.validate_email(email):
            break
        print("email not valid, try again")
    while True:
        nickname = input("nickname=")
        if DiscordBot.validate_nickname(nickname):
            break
        print("nickname not valid, try again")

    return email, nickname


def main():

    data = input_data()
    DiscordBot.main(*data)


if __name__ == '__main__':
    main()
