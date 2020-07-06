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
                print(filename_bare)
                try:
                    lyric_string = find_lyric(os.path.join(root_dir,filename))
                    if lyric_string != '':
                        fout = codecs.open(os.path.join(root_dir,filename_bare+'.lrc'),'w','utf-8')
                        fout.write(lyric_string)
                        fout.close()
                except:
                    print('other error: ')
                    continue
            elif filename.endswith(".flac"):
                filename_bare = filename[:-5]
                print(filename_bare)
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
    lyrics_url = 'https://on.petitlyrics.com/api/GetPetitLyricsData.php'
    request_body = request_body_partial
    request_body['key_album'] = album
    request_body['key_artist'] = artist
    request_body['key_title'] = title
    response_body = requests.post(lyrics_url, data = request_body, headers = request_header)
    song_xml_tree = ET.fromstring(response_body.text)
    try:
        lyrics_type = song_xml_tree.find('songs').find('song').find('lyricsType').text
        lyrics_base64 = song_xml_tree.find('songs').find('song').find('lyricsData').text
        assert lyrics_type == '3'
    except AssertionError:
        print('lyric type not currently supported')
        return ''
    except AttributeError:
        print('lyric not found')
        return ''
    lyrics_petitlyricform = base64.b64decode(lyrics_base64).decode("UTF-8")
    lyrics_tree = ET.fromstring(lyrics_petitlyricform)
    lyric_string = ''
    for line in lyrics_tree.findall('line'):
        timepoint = line.find('word').find('starttime').text
        lyric_line = line.find('linestring').text
        if lyric_line is None:
            lyric_line = ''
        lyric_string += ms2mmss(timepoint) + lyric_line +'\n'
    return lyric_string
def convert_to_filename(titletext):
    import re
    return re.sub('[^\w_.)( -]', '',titletext)

def main():
    find_lyric_folder('Y:\media\Music\THE IDOLM@STER\THE iDOLM@STER Christmas for you!')

if __name__ == '__main__':
    main()