import requests
import UserCredentials as ug

# Use the Bot in order to send Notifications about calculated progress to Telegram

key = ug.key
userID = ug.userID

url = f"https://api.telegram.org/bot{key}"


class NotifierBot():
    def __init__(self,sizeStatements,modelDescription):
        self.sizeStatements = str(sizeStatements)
        self.modelDescription = str(modelDescription)
        self.LogHead = ["BotInfo", "Size:{}".format(self.sizeStatements), self.modelDescription]

    def sentBotMessage(self,messageList):
        params = {"chat_id": userID}
        messageListStr = [str(x) for x in messageList]
        contentList = self.LogHead + messageListStr
        textcontent = "\n".join(contentList)
        params.update({"text":textcontent})
        r = requests.get(url + "/sendMessage", params=params)

