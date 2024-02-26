import os

import gspread_asyncio
from google.oauth2.service_account import Credentials

# 定数一覧

######################
# ロール
######################

# Online Loopstation Exhibition Battle
ROLE_OLEB = 1171760161778581505

# ビト森杯 LOOP部門
ROLE_LOOP = 1036149651847524393

# ビト森杯 LOOP部門 キャンセル待ち
ROLE_LOOP_RESERVE = 1172542396597289093

# ビト森杯運営
ROLE_ADMIN = 904368977092964352

# in a vc
ROLE_VC = 935073171462307881

######################
# テキストチャンネル
######################

# 全体チャット
CHANNEL_GENERAL = 864475338340171791

# bot用チャット
CHANNEL_BOT = 897784178958008322

# ビト森杯問い合わせチャンネル
CHANNEL_CONTACT = 1035964918198960128

# ビト森杯お知らせチャンネル
CHANNEL_BITOMORI_ANNOUNCE = 1035965200341401600

# ビト森杯 進行botチャンネル
CHANNEL_BITOMORI_BOT = 1035946838487994449

######################
# ボイスチャンネル
######################

# リアタイ部屋
VC_REALTIME = 886099822770290748

######################
# ユーザー
######################

# tari_2 (tariサブアカウント)
TARI_2 = 518041950146920449

# tari
TARI3210 = 412082841829113877

# Yui
YUI_1 = 891228765022195723
YUI_2 = 886518627023613962

# 湯
NURUYU_1 = 887328590407032852
NURUYU_2 = 870434043810971659

# mayco
MAYCO_1 = 389427133099016193
MAYCO_2 = 735099594010132480
MAYCO_3 = 990630026275860540

######################
# 絵文字
######################

# 草
EMOJI_KUSA = 990222099744432198

# brez
EMOJI_BREZ = 889877286055198731

# oras
EMOJI_ORAS = 889920546408661032

# helium
EMOJI_HELIUM = 890506350868721664

# loop_button
EMOJI_LOOP_BUTTON = 885778461879320586

######################
# Google Sheets
######################

"""
row = 縦 1, 2, 3, ...
col = 横 A, B, C, ...
"""

# ビト森杯 LOOP部門
SHEET_LOOP = '1Bv9J7OohQHKI2qkYBMnIFNn7MHla8KyKTYTfghcmIRw'


def get_credits():
    credential = {
        "type": "service_account",
        "project_id": os.environ['SHEET_PROJECT_ID'],
        "private_key_id": os.environ['SHEET_PRIVATE_KEY_ID'],
        "private_key": os.environ['SHEET_PRIVATE_KEY'],
        "client_email": os.environ['SHEET_CLIENT_EMAIL'],
        "client_id": os.environ['SHEET_CLIENT_ID'],
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ['SHEET_CLIENT_X509_CERT_URL']
    }
    return Credentials.from_service_account_info(
        credential,
        scopes=['https://spreadsheets.google.com/feeds',
                'https://www.googleapis.com/auth/drive',
                'https://www.googleapis.com/auth/spreadsheets'])


async def get_worksheet(sheet_key: str, name: str):
    gc = gspread_asyncio.AsyncioGspreadClientManager(get_credits)
    agc = await gc.authorize()
    workbook = await agc.open_by_key(sheet_key)
    worksheet = await workbook.worksheet(name)

    return worksheet

