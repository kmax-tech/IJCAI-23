import requests

# Use the Bot in order to send Notifications about progress to Telegram

key = "5623303244:AAHrS3FSoKGTUM252nXXCtEPkSdNcr0CVyo"
userID = "652558199"

url = f"https://api.telegram.org/bot{key}"
print(url)

def sentBotMessage(messageList):
    params = {"chat_id": userID}
    textcontent = "\n".join(messageList)
    params.update({"text":textcontent})
    r = requests.get(url + "/sendMessage", params=params)

