import requests
request_body_partial = {
    'lyricsType': '3',
    'sdkVer': '1.3.4',
    'userId': '642bbdc6-128a-4b67-a10b-bc09191b0cfe',
    'appName': 'HF Player',
    'pkgName': 'com.onkyo.jp.musicplayer',
    'clientAppId': 'on354007',
    'index': '0',
    'logFlag': '0',
    'verCode': '212',
    'verName': '2.7.0',
    'maxcount': '1',
    'terminalType': '0'
}
request_header = {
    'Content-Type': 'application/x-www-form-urlencoded; charset=utf-8',
    'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; LM-G820UM Build/LMY48Z)'
}
def find_lyric_folder(directory):
    import os
    import codecs
    for (root_dir,sub_dir,filenames) in os.walk(directory):
        for filename in filenames:
            if filename.endswith(".m4a") or filename.endswith(".mp3"):
                filename_bare = filename[:-4]
            elif filename.endswith(".flac"):
                filename_bare = filename[:-5]
            else:
                continue
            print(filename_bare)
            if os.path.isfile(os.path.join(root_dir,filename_bare+'.lrc')):
                print('lyric file already exists.')
                continue
            try:
                lyric_string = find_lyric(os.path.join(root_dir,filename))
                if lyric_string != '':
                    fout = codecs.open(os.path.join(root_dir,filename_bare+'.lrc'),'w','utf-8')
                    fout.write(lyric_string)
                    fout.close()
            except:
                print('other error: ')
                continue
    return
def ms2mmss(ms):
    ms = int(ms)
    hs = (ms//10)%100
    seconds=(ms//1000)%60
    minutes=(ms//(1000*60))%60
    return '['+f'{minutes:02}'+':'+f'{seconds:02}'+'.'+f'{hs:02}'+']'
def get_lyric_base64(album,artist,title,lyricsType_request = 3):
    import xml.etree.ElementTree as ET
    lyrics_url = 'https://on.petitlyrics.com/api/GetPetitLyricsData.php'
    request_body = request_body_partial
    request_body['key_album'] = album
    request_body['key_artist'] = artist
    request_body['key_title'] = title
    request_body['lyricsType'] = lyricsType_request
    response_body = requests.post(lyrics_url, data = request_body, headers = request_header)
    song_xml_tree = ET.fromstring(response_body.text)
    try:
        lyrics_type = song_xml_tree.find('songs').find('song').find('lyricsType').text
        lyrics_base64 = song_xml_tree.find('songs').find('song').find('lyricsData').text
        if lyricsType_request == 3:
            assert lyrics_type == '3' or lyrics_type == '2'
        elif lyricsType_request == 1:
            assert lyrics_type == '1'
    except AssertionError:
        print('lyric type not currently supported')
        return [0,'']
    except AttributeError:
        print('lyric not found')
        return [0,'']
    return [lyrics_type, lyrics_base64]
def find_lyric(path_to_music_file):
    from tinytag import TinyTag as ttag
    import xml.etree.ElementTree as ET
    import base64
    try:
        tag = ttag.get(path_to_music_file)
    except:
        print('Tag read error')
        return ''
    album = tag.album
    artist = tag.artist
    title = tag.title
    [lyrics_type,lyrics_base64] = get_lyric_base64(album,artist,title,3)
    
    if lyrics_type == '2':
        [lyrics_type,lyrics_text_base64] = get_lyric_base64(album,artist,title,1)
        print('lyric added from line sync source')
        return lsy_decoder(lyrics_base64,lyrics_text_base64)
    elif lyrics_type == '3':
        lyrics_petitlyricform = base64.b64decode(lyrics_base64).decode("UTF-8")
        lyrics_tree = ET.fromstring(lyrics_petitlyricform)
        lyric_string = ''
        for line in lyrics_tree.findall('line'):
            timepoint = line.find('word').find('starttime').text
            lyric_line = line.find('linestring').text
            if lyric_line is None:
                lyric_line = ''
            lyric_string += ms2mmss(timepoint) + ' ' + lyric_line +'\n'
        print('lyric added from word sync source')
        return lyric_string
    return ''
def convert_to_filename(titletext):
    import re
    return re.sub('[^\w_.)( -]', '',titletext)
def lsy_decoder(lsy_base64_lyric,lyrics_text_base64):#Assumes running on little endian system
    import binascii
    import struct
    import base64
    import numpy as np
    import io
    lyric_unsynced = base64.b64decode(lyrics_text_base64).decode("UTF-8")
    lyric_line_reader = io.StringIO(lyric_unsynced)
    lyric_string = '[00:00.00] ...\n'
    lyrics_encrypted = base64.b64decode(lsy_base64_lyric)
    protection_id = np.uint16(int.from_bytes(lyrics_encrypted[0x1a:0x1a+2],byteorder='little',signed=False))
    protection_key_switch_flag = bool(lyrics_encrypted[0x19])
    protection_key = protection_id
    if (protection_key_switch_flag):
        A = np.uint16(0x3   )#1100 0000 0000 0000
        B = np.uint16(0xc   )#0011 0000 0000 0000
        C = np.uint16(0x30  )#0000 1100 0000 0000
        D = np.uint16(0xc0  )#0000 0011 0000 0000
        E = np.uint16(0x300 )#0000 0000 1100 0000
        F = np.uint16(0xc00 )#0000 0000 0011 0000
        G = np.uint16(0x3000)#0000 0000 0000 1100
        H = np.uint16(0xc000)#0000 0000 0000 0011
        protection_key = (protection_key & A) | (protection_key & B) << 2 | (protection_key & C) >> 2 | (protection_key & D) << 2 |\
            (protection_key & E) >> 2 | (protection_key & F) << 2 | (protection_key & G) >> 2 | (protection_key & H)
            #Note << always increase value in python, independent of endian
    line_count = int.from_bytes(lyrics_encrypted[0x38:0x38+4],byteorder='little',signed=False)
    line_length = int.from_bytes(lyrics_encrypted[0x42:0x42+2],byteorder='little',signed=False)#Seems to be 64 for all tested files
    elapsed_time = 0
    for line_idx in range(line_count):
        #Parsing time:
        time_begin_byteindex = line_idx * 2 + 0xcc
        time_raw = np.uint16(int.from_bytes(lyrics_encrypted[time_begin_byteindex:time_begin_byteindex+2],byteorder='little',signed=False))
        time_cs = time_raw ^ protection_key#cs means centisecond
        time_cs = time_cs % 65536 + 65536 * (elapsed_time // 65536)
        time_string = ms2mmss(10*time_cs)
        elapsed_time = time_cs
        #Parsing lyric:
        lyric_line = lyric_line_reader.readline()
        lyric_string = lyric_string + time_string + ' ' + lyric_line
    return lyric_string

def main():
    find_lyric_folder('Y:\media\Music\THE IDOLM@STER\ANIMATION MASTER SPECIAL')

if __name__ == '__main__':
    main()