"""Construye el arte vectorial del perfil, sin dependencias ni llamadas de red.

python scripts/build_profile_art.py
Los bloques sincronizados de Discord y la decoración original se conservan.
"""
from html import escape
from pathlib import Path
import re
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'assets/svg'
FONT = 'Segoe UI,Inter,Arial,sans-serif'
MONO = 'Cascadia Code,Consolas,monospace'

DEFS = '''
<linearGradient id="bg" x2="1" y2="1"><stop stop-color="#081629"/><stop offset=".55" stop-color="#040a14"/><stop offset="1" stop-color="#020409"/></linearGradient>
<linearGradient id="blue" x2="1" y2=".5"><stop stop-color="#a6dcff"/><stop offset=".45" stop-color="#38a3ff"/><stop offset="1" stop-color="#2563eb"/></linearGradient>
<radialGradient id="halo"><stop stop-color="#2563eb" stop-opacity=".32"/><stop offset=".5" stop-color="#1061d6" stop-opacity=".12"/><stop offset="1" stop-color="#1061d6" stop-opacity="0"/></radialGradient>
<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#588ac3" stroke-opacity=".075"/></pattern>
'''
MOTION = '''
.orbit{animation:orbit 32s linear infinite;transform-origin:760px 205px}
.counter{animation:orbit 48s linear infinite reverse;transform-origin:760px 205px}
.signal{stroke-dasharray:8 140;animation:signal 7s linear infinite}
.breathe{animation:breathe 6s ease-in-out infinite alternate}
.cursor{animation:blink 1.4s steps(2,end) infinite}
.float{animation:float 8s ease-in-out infinite alternate}
@keyframes orbit{to{transform:rotate(360deg)}}
@keyframes signal{to{stroke-dashoffset:-296}}
@keyframes breathe{to{opacity:.45}}
@keyframes blink{50%{opacity:0}}
@keyframes float{to{transform:translateY(-7px)}}
@media(prefers-reduced-motion:reduce){*{animation:none!important}.avatar-decoration{display:none}}
'''


def svg(name, width, height, title, desc, body, defs='', css=''):
    document = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(desc)}</desc>
<defs>{DEFS}{defs}</defs>
<style>text{{font-family:{FONT}}}.mono{{font-family:{MONO}}}{MOTION}{css}</style>
{body}
</svg>
'''
    ET.fromstring(document)
    (OUT / name).write_text(document, encoding='utf-8', newline='\n')


def text(x, y, value, size=16, color='#a9bed8', extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" {extra}>{escape(value)}</text>'


def frame(w, h, radius=20):
    return f'<rect x="1" y="1" width="{w-2}" height="{h-2}" rx="{radius}" fill="url(#bg)" stroke="#1c3553"/>'


ICONS = {
    'shield': '<path d="M0-25 23-15v20C23 19 0 30 0 30S-23 19-23 5v-20Z"/><path d="m-10 2 7 7L12-7"/>',
    'cards': '<rect x="-25" y="-19" width="44" height="32" rx="5"/><rect x="-17" y="-11" width="44" height="32" rx="5"/><circle cx="-6" cy="1" r="5"/><path d="M5-1h13M5 7h9M-10 14h28"/>',
    'terminal': '<rect x="-27" y="-21" width="54" height="42" rx="6"/><path d="m-15-6 9 8-9 8M1 11h14M-27-11h54"/>',
    'bot': '<rect x="-24" y="-17" width="48" height="36" rx="10"/><path d="M0-17v-9M-24-2h-6v12h6M24-2h6v12h-6M-8 11H8"/><circle cx="0" cy="-29" r="3"/><circle cx="-10" cy="-1" r="3"/><circle cx="10" cy="-1" r="3"/>',
    'tools': '<path d="m-20 23 29-29a16 16 0 0 0 17-20L15-15 7-23l11-11A16 16 0 0 0-2-17L-31 12Z"/><circle cx="-20" cy="12" r="3"/>',
    'bolt': '<path d="M5-29-22 5H-3l-5 24L23-7H3Z"/>',
    'web': '<rect x="-27" y="-22" width="54" height="44" rx="5"/><path d="M-27-10h54m-13 8 8 7-8 7m-28-14-8 7 8 7m13-17-6 20"/>',
    'docker': '<path d="M-29 4h49c10 0 13-8 13-8l-9-2-3-8-6 9M-28 4c1 19 36 24 49 0"/><path d="M-24-7h9V3h-9ZM-13-7h9V3h-9ZM-2-7h9V3h-9ZM9-7h9V3H9ZM-13-19h9v10h-9ZM-2-19h9v10h-9Z"/>',
    'react': '<circle r="5" fill="#82c6ff"/><ellipse rx="31" ry="11"/><ellipse rx="31" ry="11" transform="rotate(60)"/><ellipse rx="31" ry="11" transform="rotate(120)"/>',
    'windows': '<path d="m-25-21 21-3V-2h-21Zm25-4 25-4V-2H0ZM-25 2h21v22l-21-3ZM0 2h25v27L0 25Z"/>',
    'database': '<ellipse cy="-19" rx="25" ry="9"/><path d="M-25-19v38c0 12 50 12 50 0v-38M-25-1c0 12 50 12 50 0M-25 10c0 12 50 12 50 0"/>',
}


def icon(kind, x, y, scale=1):
    return f'<g transform="translate({x} {y}) scale({scale})" fill="#091a30" stroke="#82c6ff" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[kind]}</g>'


def header():
    ticks = ''.join(f'<path d="M760 49v{10 if angle % 30 == 0 else 4}" transform="rotate({angle} 760 205)"/>' for angle in range(0, 360, 6))
    stars = ''.join(f'<circle cx="{x}" cy="{y}" r="{r}"/>' for x,y,r in [(615,66,1.5),(871,56,2),(921,179,1),(598,292,2),(890,334,1.5),(652,349,1),(809,29,1),(924,81,1)])
    body = frame(960,420,24) + '''
<rect x="2" y="2" width="956" height="416" rx="24" fill="url(#grid)"/>
<ellipse cx="760" cy="205" rx="258" ry="235" fill="url(#halo)"/>
<path d="M25 1H935" stroke="url(#blue)" stroke-width="2"/>
<path d="M34 43h14m-7-7v14M912 43h14m-7-7v14" stroke="#477aaa"/>
<path d="M40 350H490M40 350v-6M490 350v-6" stroke="#24415e"/>
''' + text(64,48,'Oscar-Dev0 / software developer',13,extra='class="mono"') + text(40,107,'Desde Costa Rica, para tus ideas.',17,'#83bbef') + text(36,190,'Oscar Dev.',78,'#f4f9ff','font-weight="750" letter-spacing="-4"') + text(40,239,'Del código al servidor.',29,'#deebff','font-weight="500"') + text(40,271,'Web, bots, herramientas e infraestructura.',17) + '''
<g class="mono" font-size="12" fill="#c4dcf7">
<rect x="40" y="298" width="141" height="29" rx="14.5" fill="#0b203a" stroke="#234b76"/><text x="58" y="317">React / SvelteKit</text>
<rect x="191" y="298" width="134" height="29" rx="14.5" fill="#0b203a" stroke="#234b76"/><text x="209" y="317">Linux / Docker</text>
<rect x="335" y="298" width="113" height="29" rx="14.5" fill="#0b203a" stroke="#234b76"/><text x="353" y="317">FiveM / Lua</text>
</g>
''' + text(40,383,'oscar@linux',13,'#89c7ff','class="mono"') + text(135,383,':~/projects $ git status',13,'#b8cfe9','class="mono"') + '<rect class="cursor" x="334" y="369" width="7" height="15" fill="#38a3ff"/>' + f'''
<g fill="#a6dcff" class="breathe">{stars}</g>
<g fill="none" stroke="#3b689a" stroke-width="1">{ticks}</g>
<circle cx="760" cy="205" r="141" fill="none" stroke="#193b65"/>
<g class="orbit" fill="none"><circle cx="760" cy="205" r="128" stroke="#38a3ff" stroke-width="2" stroke-dasharray="164 35 12 593"/><circle cx="760" cy="77" r="5" fill="#b8e8ff" stroke="#38a3ff"/><circle cx="760" cy="77" r="10" fill="#38a3ff" opacity=".18"/></g>
<g class="counter" fill="none"><circle cx="760" cy="205" r="110" stroke="#3865bc" stroke-dasharray="2 9"/><path d="M650 205a110 110 0 0 1 110-110" stroke="#89c7ff" stroke-width="2"/></g>
<path d="M603 205h46M871 205h46M760 48v30M760 334v28" stroke="#27466a"/>
<g class="float"><path d="m760 124 70 40v82l-70 40-70-40v-82Z" fill="#071327" stroke="#286bb0"/>
<path d="m760 139 57 33v66l-57 33-57-33v-66Z" fill="#081b35" stroke="#38a3ff" stroke-opacity=".4"/>
<path d="m732 187-17 18 17 18m56-36 17 18-17 18m-22-44-13 48" fill="none" stroke="#bcE6ff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>
<path d="m760 124 70 40-13 8m-127 74 13-8 57 33v15" fill="none" stroke="#70baff" stroke-width="2"/></g>
''' + text(760,389,'Pura vida. Puro código.',13,'#94b9e0','text-anchor="middle"')
    svg('header.svg',960,420,'Oscar Dev · Del código al servidor', 'Programador de Costa Rica. React, SvelteKit, Linux, Docker, Windows Server, Discord y FiveM. Núcleo orbital y prompt de Linux ilustrado.',body)
    body = frame(480,430) + '<ellipse cx="420" cy="60" rx="230" ry="160" fill="url(#halo)"/><rect x="2" y="2" width="476" height="426" rx="20" fill="url(#grid)"/>'
    body += '<g class="mobile-orbit" fill="none" stroke="#38a3ff" stroke-opacity=".35"><circle cx="408" cy="63" r="46" stroke-dasharray="65 15 3 206"/><circle cx="408" cy="17" r="3" fill="#91caff"/></g>'
    body += icon('terminal',408,63,.85) + text(28,49,'Oscar-Dev0',14,'#a9bed8','class="mono"') + text(28,119,'Oscar Dev.',61,'#f4f9ff','font-weight="750" letter-spacing="-3"')
    body += text(30,164,'Del código al servidor.',29,'#dcecff','font-weight="500"') + text(30,208,'Web, bots, herramientas e infraestructura.',18) + text(30,240,'Desde Costa Rica. Pura vida.',18)
    body += '<path d="M30 274H450" stroke="#23466c"/><g fill="#0c213a" stroke="#274d76"><rect x="30" y="298" width="128" height="34" rx="17"/><rect x="170" y="298" width="128" height="34" rx="17"/><rect x="310" y="298" width="140" height="34" rx="17"/></g>'
    body += text(94,320,'React',16,'#cde6ff','text-anchor="middle"') + text(234,320,'SvelteKit',16,'#cde6ff','text-anchor="middle"') + text(380,320,'Linux / Docker',16,'#cde6ff','text-anchor="middle"')
    body += text(30,385,'oscar@linux:~/projects $',17,'#9ecbff','class="mono"') + '<rect class="cursor" x="277" y="369" width="8" height="20" fill="#38a3ff"/>'
    svg('header-mobile.svg',480,430,'Oscar Dev · Del código al servidor','Programador desde Costa Rica. React, SvelteKit, Linux, Docker y Windows Server.',body,css='.mobile-orbit{animation:orbit 32s linear infinite;transform-origin:408px 63px}')


AREAS = [
    ('web','Desarrollo web','Interfaces y aplicaciones.','React / SvelteKit / TypeScript'),
    ('bot','Comunidades','Bots modulares y tarjetas.','Discord / Seyfert / Canvas'),
    ('terminal','Herramientas','Utilidades, librerías y recursos.','Node.js / Python / Go / Lua'),
    ('docker','Infraestructura','Terminales, contenedores y servidores.','Linux / Docker / Windows Server'),
]


def workbench():
    body = frame(960,370) + '<path d="M480 24v322M24 185H936" stroke="#1c3553"/>'
    for i,(kind,title,detail,stack) in enumerate(AREAS):
        x,y=(i%2)*480,(i//2)*185
        body += icon(kind,x+424,y+52,.65) + text(x+26,y+48,title,26,'#edf6ff','font-weight="650"')
        body += text(x+26,y+91,detail,18,'#bedcff') + text(x+26,y+131,stack,14,'#8fb9e3','class="mono"')
        body += f'<path d="M{x+26} {y+157}H{x+454}" stroke="#20436d"/><path class="signal" d="M{x+26} {y+157}H{x+454}" stroke="#60b6ff" stroke-width="1.5" style="animation-delay:-{i*2}s"/>'
    svg('workbench.svg',960,370,'Lo que me gusta construir','Desarrollo web, comunidades de Discord, herramientas e infraestructura con Linux, Docker y Windows Server.',body)


def terminal():
    css = '.terminal-scan{animation:scan 12s ease-in-out infinite alternate}@keyframes scan{to{transform:translateY(270px)}}'
    body = frame(960,390) + '<path d="M1 45H959M607 45V389" stroke="#1c3553"/>'
    body += '<g fill="#416da0"><circle cx="25" cy="24" r="4"/><circle cx="41" cy="24" r="4"/><circle cx="57" cy="24" r="4"/></g>' + text(80,29,'oscar@linux: ~/workspace',13,'#a5c8e9','class="mono"')
    body += text(933,29,'bash / stack.yml',12,'#8eb6df','class="mono" text-anchor="end"')
    body += '<rect x="2" y="46" width="603" height="342" fill="url(#grid)"/><path class="terminal-scan" d="M25 65H580" stroke="#4aaeff" stroke-opacity=".1" stroke-width="12"/>'
    body += text(26,85,'$ cat stack.yml',18,'#9fd4ff','class="mono"')
    rows = [('developer:','Oscar Dev'),('web:','[SvelteKit, React]'),('runtime:','[Node.js, Bun]'),('containers:','[Docker, Compose]'),('systems:','[Linux, Windows Server]'),('community:','[Discord, FiveM]')]
    for i,(key,value) in enumerate(rows):
        y=126+i*34
        body += text(26,y,key,17,'#90b2d6','class="mono"') + text(166,y,value,17,'#d4e8ff','class="mono"')
    body += text(26,355,'$',18,'#9fd4ff','class="mono"') + '<rect class="cursor" x="47" y="339" width="10" height="21" fill="#38a3ff"/>'
    for y,kind,title,sub in [(91,'web','Interfaces','SvelteKit / React'),(192,'docker','Contenedores','Docker / Compose'),(293,'windows','Sistemas','Linux / Windows Server')]:
        body += icon(kind,902,y+10,.66) + text(638,y,title,23,'#e4f2ff','font-weight="650"') + text(638,y+31,sub,16)
        body += f'<path d="M638 {y+52}H930" stroke="#1c3553"/>'
    svg('terminal.svg',960,390,'Mi stack desde la terminal','Terminal Linux ilustrada con mis tecnologías: SvelteKit, React, Node.js, Bun, Docker, Compose, Linux, Windows Server, Discord y FiveM. No ejecuta comandos.',body,css=css)
    body = frame(480,446) + '<path d="M1 47H479" stroke="#1c3553"/>' + text(26,31,'oscar@linux: ~/workspace',16,'#a5c8e9','class="mono"')
    body += '<rect x="2" y="48" width="476" height="396" fill="url(#grid)"/>' + text(26,89,'$ cat stack.yml',23,'#9fd4ff','class="mono"')
    for i,(key,value) in enumerate(rows):
        y=133+i*43
        body += text(26,y,key,18,'#90b2d6','class="mono"') + text(166,y,value,18,'#d4e8ff','class="mono"')
    body += text(26,410,'$',23,'#9fd4ff','class="mono"') + '<rect class="cursor" x="53" y="390" width="10" height="25" fill="#38a3ff"/>'
    svg('terminal-mobile.svg',480,446,'Mi stack desde la terminal','Terminal ilustrada. React, SvelteKit, Node.js, Bun, Docker, Compose, Linux, Windows Server, Discord y FiveM.',body)


def platforms():
    entries=[('react','React'),('web','SvelteKit'),('terminal','Linux'),('docker','Docker'),('windows','Windows Server'),('terminal','Node.js'),('bolt','Bun'),('database','MySQL')]
    body=frame(960,300) + text(28,43,'Del navegador al servidor',24,'#e8f3ff','font-weight="650"')
    for i,(kind,label) in enumerate(entries):
        x,y=28+(i%4)*234,64+(i//4)*112
        body += f'<rect x="{x}" y="{y}" width="202" height="100" rx="12" fill="#09182a" stroke="#223f60"/>'
        body += icon(kind,x+35,y+48,.62) + text(x+67,y+55,label,17 if len(label)>12 else 19,'#d5e7fa','font-weight="600"')
    svg('platforms.svg',960,300,'Frameworks, plataformas y sistemas','React, SvelteKit, Linux, Docker, Windows Server, Node.js, Bun y MySQL.',body)
    body=frame(480,542) + text(26,43,'Del navegador al servidor',27,'#e8f3ff','font-weight="650"')
    for i,(kind,label) in enumerate(entries):
        x,y=26+(i%2)*220,66+(i//2)*116
        body += f'<rect x="{x}" y="{y}" width="208" height="102" rx="12" fill="#09182a" stroke="#223f60"/>'
        body += icon(kind,x+104,y+35,.65) + text(x+104,y+82,label,21,'#d5e7fa','font-weight="600" text-anchor="middle"')
    svg('platforms-mobile.svg',480,542,'Frameworks, plataformas y sistemas','React, SvelteKit, Linux, Docker, Windows Server, Node.js, Bun y MySQL.',body)


def lab():
    body = frame(960,330) + '<rect x="2" y="2" width="956" height="326" rx="20" fill="url(#grid)"/><path d="M1 49H959M566 49V329" stroke="#1c3553"/><g fill="#416da0"><circle cx="26" cy="25" r="4"/><circle cx="42" cy="25" r="4"/><circle cx="58" cy="25" r="4"/></g>' + text(80,30,'ideas / oscar.config.ts',13,extra='class="mono"')
    for x,y,s,color in [(29,92,'const oscar = {','#9dcaff'),(49,133,"web: ['SvelteKit', 'React'],",'#c9ddf6'),(49,174,"sistemas: ['Linux', 'Windows Server'],",'#c9ddf6'),(49,215,"contenedores: 'Docker / Compose',",'#c9ddf6'),(49,256,"comunidad: 'Discord / FiveM'",'#c9ddf6'),(29,298,'};','#9dcaff')]:
        body += text(x,y,s,18,color,'class="mono"')
    body += '<rect class="cursor" x="62" y="282" width="9" height="21" fill="#38a3ff"/>' + text(598,91,'De la idea al proyecto',23,'#e7f2ff','font-weight="650"')
    body += '<path d="M611 133V283" stroke="#234f7c"/><path class="signal" d="M611 133V283" stroke="#78c5ff" stroke-width="2"/>'
    for y,title,sub in [(143,'Pensar','Entender el problema.'),(207,'Construir','Probar, ajustar y experimentar.'),(271,'Compartir','Dejar algo que pueda servir.')]:
        body += f'<circle cx="611" cy="{y-6}" r="6" fill="#0c223b" stroke="#63b6ff"/>' + text(631,y,title,20,'#e4f2ff','font-weight="600"') + text(631,y+23,sub,14)
    svg('code-lab.svg',960,330,'Pensar, construir y compartir','Configuración ilustrada de Oscar y su proceso: entender, experimentar y compartir lo aprendido.',body)


def country():
    body = frame(480,180) + '<ellipse cx="410" cy="80" rx="190" ry="130" fill="url(#halo)"/>'
    body += '<g clip-path="url(#flag)"><path d="M26 40h150v100H26Z" fill="#002b7f"/><path d="M26 56.6667h150v66.6666H26Z" fill="#fff"/><path d="M26 73.3333h150v33.3334H26Z" fill="#ce1126"/><rect x="26" y="40" width="150" height="100" fill="url(#silk)"/><rect class="silk" x="-125" y="40" width="140" height="100" fill="url(#sheen)"/></g><rect x="26" y="40" width="150" height="100" rx="9" fill="none" stroke="#91b5dd" stroke-opacity=".2"/>'
    body += text(202,51,'Mi rincón del mundo',13,'#97bde5') + text(200,88,'Costa Rica',32,'#eef7ff','font-weight="700" letter-spacing="-1"') + text(202,117,'Pura vida, puro código.',17) + text(202,147,'Centroamérica / UTC−6',12,'#9cc9f1','class="mono"')
    defs = '<clipPath id="flag"><rect x="26" y="40" width="150" height="100" rx="9"/></clipPath><linearGradient id="silk"><stop stop-color="#fff" stop-opacity=".03"/><stop offset=".4" stop-color="#fff" stop-opacity=".17"/><stop offset=".8" stop-color="#000" stop-opacity=".13"/><stop offset="1" stop-color="#fff" stop-opacity=".06"/></linearGradient><linearGradient id="sheen"><stop stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".15"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    svg('costa-rica.svg',480,180,'Costa Rica · Pura vida','Bandera de Costa Rica con cinco franjas en proporción 1:1:2:1:1 y reflejo suave.',body,defs,'.silk{animation:silk 9s ease-in-out infinite}@keyframes silk{to{transform:translateX(330px)}}')


PROJECTS = [
    ('project-safezone.svg','shield','os_safezone','FiveM / sistemas','Zonas seguras, reglas por zona,','editor visual y persistencia en MySQL.','Lua · JavaScript · MySQL'),
    ('project-rebalancer.svg','tools','weapon_rebalancer','FiveM / herramientas','Auditoría y ajustes de archivos META','con previsualización y validaciones.','Python'),
    ('project-cards.svg','cards','discord_cards','Discord / diseño','Tarjetas de bienvenida, niveles','y rankings generados con Canvas.','TypeScript · Canvas'),
    ('project-console.svg','terminal','console','Developer tooling','Colores, texto centrado y recuadros','para la consola de Node.js.','TypeScript · Node.js'),
    ('project-seyfert.svg','bot','Base modular Seyfert','Discord / arquitectura','Una estructura modular para empezar','a construir tu bot de Discord.','TypeScript · Seyfert'),
    ('project-bun.svg','bolt','Plantilla-bot-bun','Discord / runtime','Un punto de partida para bots','con discord.js y el runtime Bun.','TypeScript · Bun'),
    ('project-linux.svg','docker','LinuxConteiner','Linux / laboratorio','Ubuntu y OpenSSH en un contenedor','definido con Docker y Compose.','Ubuntu · Docker · Compose'),
    ('project-react.svg','react','Todo','Web / React','Proyecto de práctica con React,','rutas y estilos por componentes.','React · Router · styled-components'),
]


def projects():
    for i,(filename,kind,name,category,line1,line2,stack) in enumerate(PROJECTS):
        body = frame(460,240,16) + '<ellipse cx="410" cy="60" rx="140" ry="120" fill="url(#halo)"/>' + icon(kind,406,53,.58)
        body += text(24,39,category,13,'#8fbce7') + text(23,88,name,27 if len(name)<21 else 24,'#edf6ff','font-weight="700" letter-spacing="-.6"')
        body += text(24,126,line1,16) + text(24,151,line2,16) + '<path d="M24 174H436" stroke="#203d5e"/><path class="signal" d="M24 174H436" stroke="#63b8ff" stroke-width="1.5"/>'
        body += text(24,212,stack,13,'#acd4ff','class="mono"') + text(431,213,'↗',21,'#91caff','text-anchor="end"')
        svg(filename,460,240,name,f'{name}. {line1} {line2} {stack}. Abrir repositorio.',body)
        short = ['Zonas','Archivos META','Tarjetas','Consola','Seyfert','Bun','Linux + Docker','React'][i]
        body = frame(240,164,14) + '<rect x="2" y="2" width="236" height="160" rx="14" fill="url(#grid)"/><ellipse cx="120" cy="72" rx="130" ry="88" fill="url(#halo)"/>'
        body += icon(kind,120,63,1.1) + text(120,129,short,24,'#d7eaff','font-weight="650" text-anchor="middle"')
        body += '<path class="signal" d="M26 146H214" stroke="#38a3ff" stroke-width="1.5"/>'
        svg(filename.replace('.svg','-mobile.svg'),240,164,name,f'{short}. Abrir repositorio de {name}.',body)


def toolkit():
    body = frame(960,190) + text(28,42,'Lenguajes con los que construyo',23,'#e8f3ff','font-weight="650"')
    for i,(short,name) in enumerate([('TS','TypeScript'),('JS','JavaScript'),('Lua','Lua'),('Py','Python'),('Go','Go'),('C#','C#')]):
        x = 28+i*155
        body += f'<rect x="{x}" y="66" width="130" height="96" rx="12" fill="#09182a" stroke="#223f60"/>'
        body += text(x+65,108,short,27,'#91caff','font-weight="700" text-anchor="middle" class="mono"') + text(x+65,141,name,15,'#d5e7fa','text-anchor="middle"')
    svg('toolkit.svg',960,190,'Mi caja de herramientas','TypeScript, JavaScript, Lua, Python, Go y C#.',body)


def mobile():
    body = frame(480,656) + '<path d="M24 164H456M24 328H456M24 492H456" stroke="#1c3553"/>'
    for i,(kind,title,detail,stack) in enumerate(AREAS):
        y=i*164
        body += icon(kind,422,y+44,.65) + text(26,y+46,title,30,'#edf6ff','font-weight="650"')
        body += text(26,y+90,detail,21,'#bedcff') + text(26,y+130,stack,17,'#8fb9e3','class="mono"')
    svg('workbench-mobile.svg',480,656,'Lo que me gusta construir','Web, comunidades, herramientas e infraestructura.',body)
    body = frame(480,332) + text(26,47,'Lenguajes con los que construyo',25,'#e8f3ff','font-weight="650"')
    for i,(short,name) in enumerate([('TS','TypeScript'),('JS','JavaScript'),('Lua','Lua'),('Py','Python'),('Go','Go'),('C#','C#')]):
        x,y = 26+(i%3)*146,73+(i//3)*124
        body += f'<rect x="{x}" y="{y}" width="136" height="110" rx="12" fill="#09182a" stroke="#223f60"/>'
        body += text(x+68,y+47,short,32,'#91caff','font-weight="700" text-anchor="middle" class="mono"') + text(x+68,y+84,name,19,'#d5e7fa','text-anchor="middle"')
    svg('toolkit-mobile.svg',480,332,'Mi caja de herramientas','TypeScript, JavaScript, Lua, Python, Go y C#.',body)
    body = frame(480,326) + text(27,48,'De la idea al proyecto',29,'#e7f2ff','font-weight="650"') + '<path d="M42 98V280" stroke="#234f7c"/><path class="signal" d="M42 98V280" stroke="#78c5ff" stroke-width="2"/>'
    for y,title,sub in [(104,'Pensar','Entender el problema.'),(184,'Construir','Probar, ajustar y experimentar.'),(264,'Compartir','Dejar algo que pueda servir.')]:
        body += f'<circle cx="42" cy="{y-6}" r="7" fill="#0c223b" stroke="#63b6ff"/>' + text(64,y,title,26,'#e4f2ff','font-weight="600"') + text(64,y+29,sub,19)
    svg('code-lab-mobile.svg',480,326,'Pensar, construir y compartir','Entender el problema, experimentar y compartir lo aprendido.',body)


def finishing():
    body = '<path d="M0 24H419m122 0h419" stroke="url(#blue)" stroke-opacity=".25"/><path class="signal" d="M0 24H419m122 0h419" stroke="#38a3ff"/><path d="m460 16-9 8 9 8m40-16 9 8-9 8m-15-21-10 26" fill="none" stroke="#81c7ff" stroke-width="1.5"/><circle cx="428" cy="24" r="2" fill="#38a3ff"/><circle cx="532" cy="24" r="2" fill="#38a3ff"/>'
    svg('divider.svg',960,48,'Separador','Línea de circuito decorativa.',body)
    body = frame(960,156) + '<g fill="none" stroke="#2563eb" opacity=".2"><path d="M0 146Q240 66 480 146T960 146"/><path d="M0 160Q240 80 480 160T960 160"/><path d="M0 174Q240 94 480 174T960 174"/></g><path class="signal" d="M0 146Q240 66 480 146T960 146" fill="none" stroke="#65baff" stroke-opacity=".65"/>'
    body += text(480,64,'La próxima idea empieza con una conversación.',25,'#e5f2ff','text-anchor="middle" font-weight="600"') + text(480,99,'Hecho con curiosidad y café desde Costa Rica. Pura vida.',15,'#a5c9ee','text-anchor="middle"')
    svg('footer.svg',960,156,'Pura vida · Sigamos construyendo','La próxima idea empieza con una conversación. Hecho con curiosidad y café desde Costa Rica.',body)
    body = frame(480,170) + text(240,51,'La próxima idea empieza',27,'#e5f2ff','text-anchor="middle" font-weight="600"') + text(240,87,'con una conversación.',27,'#e5f2ff','text-anchor="middle" font-weight="600"') + text(240,128,'Curiosidad, café y código. Pura vida.',18,'#a5c9ee','text-anchor="middle"')
    body += '<path class="signal" d="M24 150H456" stroke="#38a3ff" stroke-width="1.5"/>'
    svg('footer-mobile.svg',480,170,'Pura vida · Sigamos construyendo','La próxima idea empieza con una conversación.',body)
    for filename,label,sub,kind in [('link-projects.svg','Explorá mis proyectos','Código, ideas y documentación','terminal'),('link-discord.svg','Conectemos en Discord','Bots, código y buenas ideas','bot')]:
        body = frame(460,90,14) + icon(kind,37,44,.45) + text(72,39,label,20,'#e1f0ff','font-weight="650"') + text(72,65,sub,14,'#9ebfe4') + text(432,53,'↗',23,'#83c3ff','text-anchor="end"')
        svg(filename,460,90,label,sub,body)
        short = 'Proyectos ↗' if kind=='terminal' else 'Discord ↗'
        body = frame(240,72,12) + icon(kind,30,36,.42) + text(58,44,short,24,'#dceeff','font-weight="650"')
        svg(filename.replace('.svg','-mobile.svg'),240,72,label,sub,body)


def discord():
    """Conserva identidad, avatar, banner y APNG durante el rediseño."""
    path = OUT / 'discord-profile.svg'
    old = path.read_text(encoding='utf-8')
    blocks = {}
    for key in ('PROFILE_TITLE','AVATAR','BANNER','NAME','USERNAME'):
        pattern = rf'<!-- {key}:START -->.*?<!-- {key}:END -->'
        matches = re.findall(pattern,old,re.S)
        if len(matches) != 1:
            raise ValueError(f'Bloque {key} ausente o duplicado')
        blocks[key] = matches[0]
    decoration = re.search(r'<image class="avatar-decoration"[^>]*/>',old)
    if decoration is None:
        raise ValueError('No se encontró la decoración original del avatar')
    discord_mark = re.search(r'<path fill="#[a-fA-F0-9]+" d="([^"]+)"', (OUT/'discord.svg').read_text(encoding='utf-8')).group(1)
    body = '''<g clip-path="url(#card)"><rect width="640" height="340" fill="url(#bg)"/><ellipse cx="530" cy="100" rx="240" ry="210" fill="url(#halo)"/>
<rect width="640" height="145" fill="url(#grid)"/>
<g fill="none" stroke="#347dce" stroke-opacity=".45"><ellipse cx="470" cy="79" rx="166" ry="56" transform="rotate(-24 470 79)"/><ellipse cx="470" cy="79" rx="122" ry="42" transform="rotate(-24 470 79)"/><circle cx="470" cy="79" r="64" stroke-dasharray="3 8"/></g>
<path class="signal" d="M306 145Q420-3 633 44" fill="none" stroke="#8bcaff" stroke-width="2"/>
''' + blocks['BANNER'] + '<path d="M0 145H640V340H0Z" fill="#050c17"/><path d="M150 145H640" stroke="#2b527b"/><path d="M480 169v146m16-146v146m16-146v146m16-146v146m16-146v146m16-146v146m16-146v146m16-146v146m16-146v146" stroke="#142842" stroke-opacity=".35"/></g>'
    body += '<rect x="1" y="1" width="638" height="338" rx="22" fill="none" stroke="#254669"/><path d="M23 1H617" stroke="url(#blue)" stroke-width="2"/>'
    body += '<rect x="19" y="18" width="170" height="28" rx="14" fill="#050c17" fill-opacity=".9" stroke="#264361"/>' + text(104,37,'Conectemos en Discord',12,'#d0e6ff','text-anchor="middle"')
    body += '<circle cx="83" cy="127" r="57" fill="#050c17" stroke="#2f5a87"/><circle cx="83" cy="127" r="51" fill="#03060b"/>' + blocks['AVATAR'] + decoration[0]
    body += text(160,187,'Bots, código y buenas ideas.',16,'#b9d5f4') + '<g>' + blocks['NAME'] + blocks['USERNAME'] + '</g>'
    body += '<rect x="30" y="278" width="165" height="36" rx="10" fill="#2563eb" stroke="#599bff"/>' + text(112,302,'Abrir mi perfil ↗',14,'#fff','text-anchor="middle" font-weight="600"') + text(215,301,'Nos vemos por Discord.',14)
    body += f'<g transform="translate(567 276) scale(1.55)"><path fill="#82c6ff" d="{discord_mark}"/></g>'
    defs = '<clipPath id="avatar-clip"><circle cx="83" cy="127" r="50"/></clipPath><clipPath id="card"><rect x="1" y="1" width="638" height="338" rx="22"/></clipPath>'
    svg('discord-profile.svg',640,340,'Discord','Perfil de Discord con avatar y decoración originales. Abrir perfil. La decoración no indica estado de conexión.',body,defs)
    document = path.read_text(encoding='utf-8').replace('<title id="title">Discord</title>',f'<title id="title">{blocks["PROFILE_TITLE"]}</title>')
    ET.fromstring(document)
    path.write_text(document,encoding='utf-8',newline='\n')


def main():
    header()
    workbench()
    terminal()
    platforms()
    lab()
    country()
    projects()
    toolkit()
    mobile()
    finishing()
    discord()
    print('Arte del perfil construido; identidad de Discord conservada.')


if __name__ == '__main__':
    main()
