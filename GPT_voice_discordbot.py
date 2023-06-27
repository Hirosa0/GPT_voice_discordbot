import os
import openai
import discord
from discord.ext import commands
import os
from google.cloud import texttospeech

# Google Cloudの認証に必要なJSONファイルへのパスを設定
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'PATH_TO_JSONFILE'

intents = discord.Intents.all()

# OpenAIとDiscordのAPIキーを設定
OPENAI_API_KEY = "openai_api_key"
TOKEN = 'discord_bot_token'

# Discordのクライアントオブジェクトを作成
client = discord.Client(intents=intents)

# ログインの角印
@client.event
async def on_ready():
    print('ログインしました')

# ボットがメッセージを受信したとき
@client.event
async def on_message(message):
    if message.content == "!join":
        if message.author.voice is None:
            await message.channel.send("あなたはボイスチャンネルに接続していません。")
            return
        # ユーザーが参加しているボイスチャンネルにボットを接続
        await message.author.voice.channel.connect()
    else:
        # 
        if message.channel.id == 00000000:
            if not message.author.bot:
                # OpenAIのAPIキーを設定してGPT-3.5から応答を取得
                openai.api_key = OPENAI_API_KEY
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "user", "content": message.content},
                    ],
                )
                # GPT-3.5からの応答を取得して音声に変換
                answer = response.choices[0]["message"]["content"].strip()
                client2 = texttospeech.TextToSpeechClient()
                synthesis_input = texttospeech.SynthesisInput(text=answer)
                voice = texttospeech.VoiceSelectionParams(language_code="ja-JP", ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL)
                audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
                response = client2.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
                # 音声データをファイルに保存
                with open("output.mp3", "wb") as out:
                    out.write(response.audio_content)
                    print('Audio content written to file "output.mp3"')
                # ボイスチャンネルに接続している場合、音声を再生
                if message.guild.voice_client is None:
                    await message.channel.send("接続していません。")
                    return
                message.guild.voice_client.play(discord.FFmpegPCMAudio("output.mp3"))
                # メッセージチャンネルにもテキストとして応答を送信
                await message.channel.send(answer)

# ボットをDiscordに接続
client.run(TOKEN)
