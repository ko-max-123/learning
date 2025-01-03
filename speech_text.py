import requests
import json
import time
import discord
from discord.ext import commands
import asyncio
import os
import io
import ffmpeg

# VOICEVOXサーバー設定
BASE_URL = "http://localhost:50021"

# サーバー接続確認
session = requests.Session()
def check_server_status():
    try:
        response = session.get(f"{BASE_URL}/setting", timeout=5)
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"サーバーチェックエラー: {e}")
        return False

# 音声合成処理
def text_to_speech(text):
    if not check_server_status():
        print("VOICEVOXサーバーに接続できませんでした。")
        return None

    params = (
        ("text", text),
        ("speaker", 8)
    )
    query_response = session.post(
        f"{BASE_URL}/audio_query",
        headers={"Content-Type": "application/json"},
        params=params
    )
    query = query_response.json()
    query["speedScale"] = 0.9
    query["intonationScale"] = 1.1
    query["pauseLength"] = 1.1
    query["volumeScale"] = 0.9

    synthesis_response = session.post(
        f"{BASE_URL}/synthesis",
        headers={"Content-Type": "application/json"},
        params=params,
        data=json.dumps(query)
    )
    return io.BytesIO(synthesis_response.content)

# Discordボット設定
with open('token.txt', 'r') as file:
    TOKEN = file.read().strip()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'ログインしました: {bot.user}')

# 常時接続とメッセージ再生処理
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # メッセージの内容をVOICEVOXで音声化
    audio_data = text_to_speech(message.content)

    # ボイスチャンネルに常時在駐
    if message.author.voice and audio_data:  # ボイスチャンネルに接続中の場合
        voice_channel = message.author.voice.channel
        vc = discord.utils.get(bot.voice_clients, guild=message.guild)
        if not vc or not vc.is_connected():
            vc = await voice_channel.connect()

        # 音声データを直接再生
        vc.play(discord.FFmpegPCMAudio(audio_data, pipe=True), after=lambda e: print('再生完了'))
        while vc.is_playing():
            await asyncio.sleep(1)

bot.run(TOKEN)
