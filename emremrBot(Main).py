import discord
import traceback
import openai
from typing import Literal, Optional
import os
import subprocess
from urllib.parse import quote
from discord.ext import commands
from data import APIKEY, TOKEN2
import urllib.request
import urllib
from discord.ext import listening
import shutil

TOKEN = TOKEN2
FILE_FORMATS = {"mp3": listening.MP3AudioFile, "wav": listening.WaveAudioFile}

openai.api_key = APIKEY
bot = commands.Bot(command_prefix='!',intents=discord.Intents.all())

prompts = ""
logs = ""

chatType = "QnA"
# "QnA" : 간단한 질문답변 형식은 이것을 활성화 (토큰 소모 적음)
# "Chat" : 저장된 prompt만을 이용해서 사용할 경우 활성화 (토큰 소모 중간)
# "LearningChat" : 기존의 질문 답변도 반영해서 계속 하려면 활성화 (토큰 소모 심함)

f = open("ChatLog.txt", "r")
logs = f.read()
f.close()
process_pool = listening.AudioProcessPool(1)
async def get_vc(interaction: discord.Interaction) -> Optional[listening.VoiceClient]:
    # If the bot is currently in a vc
    if interaction.guild.voice_client is not None:
        # If the bot is in a vc other than the one of the user invoking the command
        if interaction.guild.voice_client.channel != interaction.user.voice.channel:
            # Move to the vc of the user invoking the command.
            await interaction.guild.voice_client.move_to(interaction.user.voice.channel)
        return interaction.guild.voice_client
    # If the user invoking the command is in a vc, connect to it
    if interaction.user.voice is not None:
        return await interaction.user.voice.channel.connect(cls=listening.VoiceClient)
    
async def change_deafen_state(vc: discord.VoiceClient, deafen: bool) -> None:
    state = vc.guild.me.voice
    await vc.guild.change_voice_state(channel=vc.channel, self_mute=state.self_mute, self_deaf=deafen)
    
# The key word arguments passed in the listen function MUST have the same name.
# You could alternatively do on_listen_finish(sink, exc, channel, ...) because exc is always passed
# regardless of if it's None or not.
async def on_listen_finish(sink: listening.AudioFileSink, exc=None, channel=None):
    # Convert the raw recorded audio to its chosen file type
    # kwargs can be specified to convert_files, which will be specified to each AudioFile.convert call
    # here, the stdout and stderr kwargs go to asyncio.create_subprocess_exec for ffmpeg
    await sink.convert_files(stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Raise any exceptions that may have occurred
    if exc is not None:
        raise exc
@bot.command()
async def join(ctx):
    if bot.voice_clients == []:
        if ctx.author.voice is None:
            ctx.message.send("사용자가 음성 채널에 참가해야 사용할 수 있습니다.")
        else:
            channel = ctx.author.voice.channel
            await channel.connect()

@bot.command()
async def leave(ctx):
    voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=ctx.guild)
    if voice_client is None:
        await ctx.channel.send("봇이 음성채팅에 접속했을때만 사용가능합니다.",reference=ctx.message)
    else:
        await voice_client.disconnect()
        await ctx.channel.send("성공적으로 종료되었습니다.",reference=ctx.message)

@bot.event
async def on_ready():
    print('다음으로 로그인합니다: ' + bot.user.name)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game("대기"))
    print('Login Successful')

@bot.command()
async def type(message,*var):

    global chatType
    global logs
    global prompts

    if len(var) == 0:
        await message.channel.send(f"현재 타입 : {chatType}\n", reference=message.message)
    elif var[0] == "QnA":
        chatType = "QnA"
        prompts = ""
        await message.channel.send("QnA로 기능을 변경했습니다.", reference=message.message)
    elif var[0] == "Chat":
        chatType = "Chat"
        f = open("ChatPrompt.txt", "r", encoding='UTF8')
        prompts = f.read()
        f.close()
        await message.channel.send("Chat으로 기능을 변경했습니다.", reference=message.message)
    elif var[0] == "LearningChat":
        chatType = "LearningChat"
        f = open("ChatPrompt.txt", "r", encoding='UTF8')
        prompts = f.read()
        f.close()
        await message.channel.send("LearningChat으로 기능을 변경했습니다. 다른 기능으로 변경/종료 전에 저장하시기를 권장합니다.", reference=message.message)
    else:
        await message.channel.send(f"현재 타입 : {chatType}\n'QnA', 'Chat', 'LearningChat' 중 하나를 선택할 수 있습니다.", reference=message.message)

@bot.command()
async def c(message,*vars):

    global logs
    global prompts
    global chatType

    name = f"\nHuman: 나의 이름은 {message.message.author.display_name}\nAI: 알겠어. 너의 이름은 {message.message.author.display_name}."
    prefix = "\nHuman: "
    str = " ".join(vars)
    suffix = "\nAI: "

    prompt = ""

    if chatType == "Chat" or chatType == "QnA":
        prompt = [prompts]
        prompt.append(name)
        prompt.append(prefix)
        prompt.append(str)
        prompt.append(suffix)
        prompt = "".join(prompt)
    elif chatType == "LearningChat":
        prompts = [prompts]
        prompt = [name]
        prompts.append(prefix)
        prompts.append(str)
        prompts.append(suffix)
        prompts = "".join(prompts)
        prompt.append(prompts)
        prompt = "".join(prompt)
    print(prompt)

    completion = openai.Completion.create(
        model='gpt-3.5-turbo-instruct',
        prompt=prompt,
        temperature=0.9,
        max_tokens=500,
        top_p=1,
        frequency_penalty=0.0,
        presence_penalty=0.6,
        stop=[" Human:", " AI:"]
    )


    response = completion.choices[0].text
    if bot.voice_clients == []:
        print("Ignored TTS")
    else:
        getresponse = response.split(" ")
        enc = quote(response)
        tts = "voice.wav"
        voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=message.guild)
        if voice_client.is_playing() == True:
            await message.channel.send("말하는 도중에 다른 말을 할 수 없습니다.", reference=message.message)
            return
        else:
            urllib.request.urlopen(f"http://127.0.0.1:8000/TTSServer/{enc}/")
            voice_client.play(discord.FFmpegPCMAudio(tts), after=None)

    await message.channel.send(response, reference=message.message)
    print(response)

    if chatType == "LearningChat":
        prompts = [prompts]
        prompts.append(response)
        prompts = "".join(prompts)

    logs = [logs]
    logs.append(prefix)
    logs.append(str)
    logs.append(suffix)
    logs.append(response)
    logs = "".join(logs)

@bot.command()
@commands.is_owner()
async def saveprompt(message):

    global prompts

    if chatType == "LearningChat":
        f = open("ChatPrompt.txt", "w", encoding='UTF8')
        f.write(prompts)
        f.close()
        await message.channel.send("Prompt를 저장 했습니다.", reference=message.message)
    else:
        await message.channel.send("LearningChat 타입일 때만 Prompt를 저장 가능합니다.", reference=message.message)

@bot.command()
@commands.is_owner()
async def savelog(message):

    global logs

    f = open("ChatLog.txt", "w", encoding='UTF8')
    f.write(logs)
    f.close()
    await message.channel.send("채팅 로그를 저장 했습니다.", reference=message.message)

@bot.command()
@commands.is_owner()
async def delprompt(message):
    global prompts
    prompts = ''
    os.remove('ChatPrompt.txt')
    f=open("ChatPrompt.txt","w", encoding='UTF8')
    f.write("")
    await message.channel.send("저장된 Prompt를 삭제 했습니다.", reference=message.message)

@bot.event
async def on_command_error(ctx, error):
    tb = traceback.format_exception(type(error), error, error.__traceback__)
    err = [line.rstrip() for line in tb]
    errstr = '\n'.join(err)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('명령어에 필요한 값이 입력되지 않았습니다.', reference=ctx.message)
        print(errstr)
    elif isinstance(error, commands.CommandInvokeError):
        await ctx.send('명령어에 유효하지 않은 값이 입력되었습니다. (또는 코드 오류)', reference=ctx.message)
        print(errstr)
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send('올바르게 입력하지 않았거나 존재하지 않는 명령어입니다.', reference=ctx.message)
        print(errstr)
    elif isinstance(error, commands.NotOwner):
        await ctx.send('봇 주인만 사용 가능한 명령어입니다.', reference=ctx.message)
        print(errstr)        
    else:
        print(errstr)

        
bot.run(TOKEN)