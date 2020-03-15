import confuse

config = confuse.Configuration("Bot", __name__)
config.set_file("config.yaml")

def text_edit(message):
    with open("hello_message.txt", "w") as file:
        file.write(message)

def get_text():
    with open("hello_message.txt", "r") as file:
        text = file.read()
        return text