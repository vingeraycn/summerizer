import discord
import openai
import re

try:
  # 设置 Discord API 密钥和 ChatGPT API 密钥
  discord_bot = os.environ["DISCORD_BOT"]
  openai.api_key = os.environ["OPEN_API_KEY"]
except KeyError:
  print('Get Secret Failed')

intents = discord.Intents.default()
intents.message_content = True

# 创建一个 Discord 客户端
client = discord.Client(intents=intents)


async def get_all_messages(thread):
    msgs = []
    async for msg in thread.history(limit=None):
        msgs.append(msg)
    return msgs

# 当机器人已经启动时运行
@client.event
async def on_ready():
    print('Bot is ready.')

# 当机器人收到新消息时运行
@client.event
async def on_message(message):

    print(message)
    # 判断消息来自哪个 Thread
    channel = message.channel
    thread_name = channel.name
    target_thread = None

    if channel.type == discord.ChannelType.public_thread or channel.type == discord.ChannelType.private_thread or channel.type == discord.ChannelType.news_thread:
      # 当前消息来自 Thread
      target_thread = channel
    else:
      threads = channel.threads

      for thread in threads:
          if thread.name == thread_name:
              target_thread = thread
              break

    print(f"target_thread: {target_thread}")

    
    msgs = []
    if target_thread:
        raw_msgs = await get_all_messages(target_thread)
        raw_msgs.reverse()

        for msg in raw_msgs:
            msgs.append({
              'role': 'user',
              'content': msg.content
            })


    # 检查消息是否包含有效的对话内容
    if re.search('(?i)请总结', message.content):
        msgs.append({
          'role': 'user',
          'content': 'Summarize the conversations above in Chinese'
        })

        # 使用 ChatGPT 生成对话总结
        response = openai.ChatCompletion.create(
              model="gpt-3.5-turbo",
              messages=msgs
        )
        summary = response.choices[0].message.content.strip()
        # 发送总结到 Thread 频道
        await message.channel.send(summary)

# 运行机器人
client.run(discord_bot)
