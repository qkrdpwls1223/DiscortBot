import discord
from discord.utils import get
from discord import FFmpegPCMAudio
from discord.ext import commands

from urllib.request import urlopen
from urllib.parse import urlencode, quote_plus, unquote
import urllib
import json
import requests
import pandas as pd
import datetime

from selenium import webdriver
import time
from bs4 import BeautifulSoup

df = pd.read_excel('Grid_latitude(20210401).xlsx', usecols=[2,3,4,5,6])

def schoolMenu(mealtime):
    url = 'https://newgh.gnu.ac.kr/main/ad/fm/foodmenu/selectFoodMenuView.do?schSysId=cdorm&mi=1342'
    week = datetime.datetime.today().weekday() + 2


    options = webdriver.ChromeOptions()
    options.add_experimental_option('excludeSwitches', ['enable-logging'])

    driver = webdriver.Chrome(options=options, executable_path='./chromedriver.exe')
    driver.get(url)

    time.sleep(1)

    x_path = '//*[@id="sub_content"]/div[2]/div[2]/div/div[1]/div[1]/div/ul/li[2]/a'
    searchbox = driver.find_element_by_xpath(x_path)
    searchbox.click()

    time.sleep(1)

    print('--------------')

    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")

    select = '#detailForm > div > table > tbody > tr:nth-child({}) > td:nth-child({}) > div > p'.format(mealtime, week)
    try:
        contents = soup.select_one(select)
    except:
        driver.close()
        return 0
    menu = str(contents)[12:-9]

    driver.close()
    return menu.split('<br/>')

def timeArrange():
    today = datetime.datetime.now()
    hour = today.hour
    if today.minute < 40:
        if hour == 0:
            hour = 23
        else:
            hour = hour - 1
        print(hour)
        if hour < 10:
            return '0' + str(hour)
        else:
            return hour
    else:
        if hour < 10:
            return '0' + str(hour)
        else:
            return hour

def weather(area):
    try:
        name_list3 = list(df['1단계'])
        name_list2 = list(df['2단계'])
        name_list = list(df['3단계'])
        gridX_list = list(df['격자 X'])
        gridY_list = list(df['격자 Y'])
    except:
        return '지역명 파일이 로드되지 않았습니다.'

    search_idx = -1
    search_word = str(area)
    print(f'/{search_word}/')
    for i in range(len(name_list)):
        print(i, name_list[i])
        if search_word == name_list[i]:
            print(f'{search_word} in {name_list[i]} : {search_word in name_list[i]}')
            search_idx = i
            print(i, search_idx)
            break
        elif search_word in name_list[i]:
            print(f'{search_word} in {name_list[i]} : {search_word in name_list[i]}')
            search_idx = i
            print(i, search_idx)
            break
    if search_idx < 0:
        print(search_idx)
        print(area)
        return area + '검색 샐패'

    key_A = 'a%2B7H%2F7cb7dz1qKQDM%2FqJd5vrqzHczNFWSKjq%2Fk2E3TtVHaBIDn%2FU5Fxz4Sw4%2Fd5Y0RCAfebvI%2FSreE4t5Eu42g%3D%3D'
    key_B = "a+7H/7cb7dz1qKQDM/qJd5vrqzHczNFWSKjq/k2E3TtVHaBIDn/U5Fxz4Sw4/d5Y0RCAfebvI/SreE4t5Eu42g=="

    callBackURL = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtNcst'
    
    basedate = datetime.datetime.today()
    basetime_hour = timeArrange()
    if basetime_hour == 0:
        basedate = datetime.datetime.date(basedate.year, basedate.month, basedate.day-1)

    queryParams = '?' + urlencode({
            quote_plus("serviceKey"): unquote(key_A),
            quote_plus("numOfRows"): "10",
            quote_plus("pageNo"): "1",
            quote_plus("dataType"): "JSON",
            quote_plus("base_date"): basedate.strftime('%Y%m%d'),
            quote_plus("base_time"): str(basetime_hour)+"00",
            quote_plus("nx"): gridX_list[search_idx],
            quote_plus("ny"): gridY_list[search_idx]
        })

    req = urllib.request.Request(callBackURL + queryParams)

    response_body = urlopen(req).read().decode("utf-8")

    try:
        data = json.loads(response_body)
    except:
        return response_body

    if data['response']['header']['resultCode'] == "00":
        res = pd.DataFrame(data['response']['body']['items']['item'])
        if name_list[search_idx][-1] == '면' or name_list[search_idx][-1] == '동':
            return datetime.datetime.today().strftime('%Y-%m-%d') + f" {basetime_hour}:00 {name_list3[search_idx]} {name_list2[search_idx]} {name_list[search_idx]} {data['response']['body']['items']['item'][3]['obsrValue']}℃"
        else:    
            return datetime.datetime.today().strftime('%Y-%m-%d') + f" {basetime_hour}:00 {name_list[search_idx]} {data['response']['body']['items']['item'][3]['obsrValue']}℃"

if not discord.opus.is_loaded:
    discord.opus.load_opus('opus')

token = 'OTM3NjIzOTgzODAzNzM2MTQ0.YfecYQ.fytBgLYBf6eOpdHvmEioDbb4XmE'
client = commands.Bot(command_prefix='응애야 ')

@client.event
async def on_ready():
    print('다음으로 로그인합니다: ')
    print(client.user.name)
    print(client.user.id)
    print('connection was succesful')
    await client.change_presence(status=discord.Status.online, activity=None)
    
@client.event
async def on_command_error(ctx, error):
    await ctx.send(f"뭐라는거야 {error}")

@client.command()
async def 들어와(ctx):
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send("채널에 안 들어가 있잖아")
        return
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
        await ctx.send('들어왔다 응애')

@client.command()
async def 안녕(ctx):
    user = ctx.author
    await ctx.send(f'안녕 {user.name}.')

@client.command()
async def 현정이(ctx):
    await ctx.send('바보')

@client.command()
async def 잘자(ctx):
    await ctx.send('응애 코낸내~')

@client.command()
async def 나잘게(ctx):
    user = ctx.author
    await ctx.send(f'{user.name} 코낸내~')

@client.command()
async def 사랑해(ctx):
    user = ctx.author
    await ctx.send(f'나도 {user.name} 사랑해')

@client.command()
async def 날씨(ctx, areaA='서울특별시', areaB=''):
    if areaB == '':
        await ctx.send(weather(areaA))
    else:
        await ctx.send(weather(areaA+' '+areaB))

@client.command()
async def play(ctx, url='https://www.youtube.com/watch?v=4gXmClk8rKI'):
    channel = ctx.message.author.voice.channel
    if ctx.voice_client is None:
        await channel.connect()
    if ctx.voice_client.is_playing() == True:
        return await ctx.send('이미 부르고 있어')
    async with ctx.typing():
        filename = await YTDLSource.from_url(url, loop=client.loop)
        ctx.voice_client.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=filename))
    await ctx.send('지금 {} 부르고 있어'.format(filename))

@client.command()
async def 노래(ctx, video_link):
    ydl_opts = {'format': 'bestaudio'}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_link, download=False)
        URL = info['formats'][0]['url']
    #voice = get(client.voice_clients, guild=ctx.guild)
    ctx.voice_client.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source=URL))
    #channel = ctx.message.author.voice.channel
    #if ctx.voice_client is None:
    #    await channel.connect()
    #if ctx.voice_client.is_playing() == True:
    #    return await ctx.send('이미 부르고 있어')
    #ctx.voice_client.play(discord.FFmpegPCMAudio(executable="C:/ffmpeg/bin/ffmpeg.exe", source="Music2.mp3"))

@client.command()
async def 그만불러(ctx):
    ctx.voice_client.pause()
    await ctx.send('웅')

@client.command()
async def 다시불러(ctx):
    ctx.voice_client.resume()
    await ctx.send('웅')

@client.command()
async def 나가(ctx):
    await ctx.voice_client.disconnect()
    await ctx.send('흥')

@client.command()
async def 어딨어(ctx):
    await ctx.send(ctx.guild)

@client.command()
async def 아침학식(ctx):
    menu = schoolMenu(1)
    messege = ''
    if menu == 0:
        await ctx.send('검색실패')
    else:
        for i in menu:
            messege += i + '\n'
    await ctx.send(messege)

@client.command()
async def 점심학식(ctx):
    menu = schoolMenu(2)
    messege = ''
    if menu == 0:
        await ctx.send('검색실패')
    else:
        for i in menu:
            messege += i + '\n'
    await ctx.send(messege)

@client.command()
async def 저녁학식(ctx):
    menu = schoolMenu(3)
    messege = ''
    if menu == 0:
        await ctx.send('검색실패')
    else:
        for i in menu:
            messege += i + '\n'
    await ctx.send(messege)

client.run(token)