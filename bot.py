import discord
import json
import os
from discord import Webhook, RequestsWebhookAdapter
import random, string


with open ("config.json",mode="r",encoding="utf-8") as filt:
    data = json.load(filt)
前輟 = data["prefix"]
TOKEN = data["token"]
OWNER_ID = data["owner"]


client = discord.Client()

@client.event   
async def on_ready():
    print('機器人已啟動，目前使用的bot：',client.user)
    status_w = discord.Status.online
    activity_w = discord.Activity(type=discord.ActivityType.watching, name=f"{前輟}help")
    await client.change_presence(status= status_w, activity=activity_w)


@client.event
async def on_message(message):
    if message.content == f"{前輟}help":
        await message.delete()
        embed = discord.Embed(title="指令清單", description="這些指令僅限群組管理員使用", color=0x04f108)
        embed.add_field(name=f"{前輟}help", value="操作手冊")
        embed.add_field(name=f"{前輟}new", value="創建一個聯接碼")
        embed.add_field(name=f"{前輟}start", value=f"{前輟}start `webhook網址` `連接瑪`")
        embed.add_field(name=f"{前輟}now", value="查看有幾個頻道連接")
        embed.add_field(name=f"{前輟}dlt", value="取消連接此頻道")
        await message.channel.send(content=None, embed=embed)

#群組數量
    if message.content == f'{前輟}now':
        await message.delete()
        with open (f"server/{message.channel.id}.json",mode="r",encoding="utf-8") as filt:
            data = json.load(filt)
        with open(f'code/{data["code"]}.txt') as myfile:
            total_lines = sum(1 for line in myfile)
        await message.channel.send(f"目前有`{total_lines}`個頻道連接")

#斷開連接
    if message.content == f'{前輟}dlt':
        if message.author.guild_permissions.manage_messages:
            with open (f"server/{message.channel.id}.json",mode="r",encoding="utf-8") as filt:
                data = json.load(filt)
            fileTest = f"server/{message.channel.id}.json"
            os.remove(fileTest)
            with open(f'code/{data["code"]}.txt','r') as r:
                lines=r.readlines()
            with open(f'code/{data["code"]}.txt','w') as w:
                for l in lines:
                    if f'{data["wh"]}\n' not in l:
                        w.write(l) 
            await message.channel.send("已取消連接")
        else:
            await message.channel.send("你需要有管理權限才可取消連接")

#強制斷聯
    if message.content == f'{前輟}opdlt':
        if message.author.id == int(OWNER_ID):
            with open (f"server/{message.channel.id}.json",mode="r",encoding="utf-8") as filt:
                data = json.load(filt)
            fileTest = f"server/{message.channel.id}.json"
            os.remove(fileTest)
            with open(f'code/{data["code"]}.txt','r') as r:
                lines=r.readlines()
            with open(f'code/{data["code"]}.txt','w') as w:
                for l in lines:
                    if f'{data["wh"]}\n' not in l:
                        w.write(l) 
            await message.channel.send("已取消連接")
        else:
            await message.channel.send("你必須是擁有者才可取消連接")

#連接碼
    if message.content == f'{前輟}new':
        if message.author.guild_permissions.manage_messages:
            代碼 = ''.join(random.choices(string.ascii_letters + string.digits, k=5))
            filepath = f"code/{代碼}.txt"
            if os.path.isfile(filepath):
                return
            else:
                await message.delete()
                tmp = message.content.split(" ",2)
                with open (f"code/{代碼}.txt",mode="w",encoding="utf-8") as filt:
                    await message.channel.send("建立成功,將私訊給你連接代碼")
                await message.author.send(f'你的連接碼是:`{代碼}`')
        else:
            await message.channel.send("你需要有管理權限才可創建連接碼")

#連接
    if message.content.startswith(f'{前輟}start'):
        if message.author.guild_permissions.manage_messages:
            await message.delete()
            tmp = message.content.split(" ",2)
            wh網址 = tmp[1]
            if len(tmp) == 1:
              await message.channel.send(f"`{前輟}start` `webhook網址` `連接碼`")
            tmp = message.content.split(f"{wh網址} ",2)
            代碼 = tmp[1]
            #亨哥0126
            if len(tmp) == 1:
              await message.channel.send(f"`{前輟}start` `webhook網址` `連接碼`")
            else:
                filepath = f"code/{代碼}.txt"
                if os.path.isfile(filepath):
                    filepath = f"server/{message.channel.id}.json"
                    if os.path.isfile(filepath):
                        await message.channel.send("你已經連接過了")
                    else:
                        with open (f"server/{message.channel.id}.json",mode="w",encoding="utf-8") as filt:
                          data = {"code":代碼,"wh":wh網址}
                          json.dump(data,filt)
                        with open(f"code/{代碼}.txt", 'a') as filt:
                            filt.write(f'{wh網址}\n')
                        await message.channel.send("連接成功!")
                else:
                    await message.channel.send(f"未找到連接瑪:`{代碼}`")
        else:
            await message.channel.send("你需要有管理權限才可連接跨群")
                    
#訊息
    if message.author.bot:
        return
    else:
        filepath = f"server/{message.channel.id}.json"
        if os.path.isfile(filepath):
            if "@everyone" in message.content :
                return
            else:
                if "@here" in message.content :
                    return
                else:
                    with open (f"server/{message.channel.id}.json",mode="r",encoding="utf-8") as filt:
                        data = json.load(filt)
                        use_code = data["code"]
                    await message.delete()
                    f = open(f"code/{use_code}.txt") 
                    lines = f.readlines()#讀取全部內容 
                    for line in lines :
        #print (line)
                        webhook = Webhook.from_url(line, adapter=RequestsWebhookAdapter()) 
                        webhook.send(username=f"來自[{message.guild.name}]--{message.author}的訊息:", avatar_url=message.author.avatar_url, content=message.content)

client.run(TOKEN)