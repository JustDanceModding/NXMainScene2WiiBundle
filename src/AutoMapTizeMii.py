
import os, json, zlib, struct, random, shutil, hanzidentifier, pinyin, requests, time, zipfile
from unidecode import unidecode
from PIL import Image

with open('config.json', 'r') as f:
    config=json.load(f)
    
parseSettings = config['settings']
jdVersion = parseSettings[0]['JDVersion']
versionAuto = 2.0

if jdVersion >= 2017:
    moveFolder = 'wiiu'
elif jdVersion == 2016:
    moveFolder = 'wii'
    


# Credits for serializer: moonlight_17 (me) jacklsummer15
def make_id():
    crc = random.randint(100000000, 999999999)
    serialized_crc = struct.pack('<I', crc)
    return serialized_crc

def ambcutter(audiofile, musictrack, codename):
    codenamelow=codename.lower()

    mtrack=json.load(open(musictrack))
    startbeat=mtrack['COMPONENTS'][0]['trackData']['structure']['startBeat']
    startbeat=abs(startbeat)
    marker=mtrack['COMPONENTS'][0]['trackData']['structure']['markers'][startbeat]
    timestamp=marker/48+0
    os.system('bin\\ffmpeg -y -ss "'+str(timestamp)+'ms" -nostats -loglevel 0 -i '+audiofile+' output/temp/'+codename+'.ogg')

    try:
        cine=json.load(open('output/temp/serializableObjects/'+codenamelow+'_mainsequence.tape.ckd'))
        for clip in cine['Clips']:
            if '_intro.tpl' in clip['__class']=='SoundSetClip':
                ambname=clip['SoundSetPath'].split('/')[-1].split('.')[0]
                if clip['StartTime']<=0:
                    clip['StartTime']=abs(clip['StartTime'])
                    print('splitting '+ambname)
                    os.system('bin\\ffmpeg -y -ss "'+str(0)+'ms" -nostats -loglevel 0 -i '+audiofile+' -t '+str(timestamp/1000)+' output/temp/'+ambname+'.ogg')
    except:
        print('no cinematic for ambs...')

def serialize_cinematics(ckd, outpath, IntroAmb):
    path='world/maps'
    if ckd.endswith("tape.ckd"):
        with open('output/temp/serializableObjects/'+ckd,'r',encoding="utf-8") as a:
            tape=json.load(a)
        print('Function_Serialize: Active')
        print('serializing '+ckd)
        codename=tape["MapName"]
        codenamelow=codename.lower()
        cineClips = 0

        if ckd.endswith('_mainsequence.tape.ckd'):
            for clip in tape['Clips']:
                if clip['__class'] == 'SoundSetClip' and '_intro' in clip['SoundSetPath'] and IntroAmb:
                    cineClips += 1
                if clip['__class'] == 'HideUserInterfaceClip':
                    cineClips += 1
                if clip['__class'] == 'VibrationClip':
                    pass
                    

        tape_serialize=open(outpath+ckd,'ab')

        if ckd.endswith('_mainsequence.tape.ckd'):
            tape_len = cineClips

        #tape_len=len(tape["Clips"])
        tape_version=int((224*tape_len)+166)
        if tape_len > 0:
            tape_serialize.write(struct.pack(">I",1)+struct.pack(">I",tape_version)+b'\x9E\x84\x54\x60\x00\x00\x00\x9C')
        if tape_len == 0:
            tape_serialize.write(b'\x00\x00\x00\x01\x00\x00\x4E\x5B\x9E\x84\x54\x60\x00\x00\x00\x9C')
        clips=struct.pack(">I",tape_len)
        for clip in tape["Clips"]:
            if IntroAmb:
                if clip['__class']=='SoundSetClip' and '_intro' in clip['SoundSetPath']:
                    filename=clip['SoundSetPath'].split("/")[-1]
                    pathname=clip['SoundSetPath'].replace(filename,"").replace("world/maps",path)
                    clips+=b'\x2D\x8C\x88\x5B\x00\x00\x00\x40'
                    clips+=struct.pack(">I",clip["Id"])
                    clips+=struct.pack(">I",clip["TrackId"])
                    clips+=struct.pack(">I",clip["IsActive"])
                    clips+=struct.pack(">i",clip["StartTime"])
                    clips+=struct.pack(">i",clip["Duration"])
                    clips+=struct.pack(">I",len(filename))+filename.encode()+struct.pack(">I",len(pathname))+pathname.encode()+struct.pack("<I",zlib.crc32(filename.encode()))
                    clips+=struct.pack(">i",clip['SoundChannel'])
                    clips+=struct.pack(">i",clip['StopsOnEnd'])
                    clips+=struct.pack(">i",clip['AccountedForDuration'])
                    clips+=b'\x00\x00\x00\x00'

            elif clip['__class']=='HideUserInterfaceClip':
                clips+=b'\x52\xE0\x6A\x9A\x00\x00\x00\x48'
                clips+=struct.pack(">I",clip["Id"])
                clips+=struct.pack(">I",clip["TrackId"])
                clips+=struct.pack(">I",clip["IsActive"])
                clips+=struct.pack(">i",clip["StartTime"])
                clips+=struct.pack(">i",clip["Duration"])
                clips+=b'\x00\x00\x00\x00\x00\x00\x00\x00'
                clips+=struct.pack(">I",clip['EventType'])
                clips+=b'\x00\x00\x00\x00'

        tape_serialize.write(clips)
        tape_serialize.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'+struct.pack(">I",tape['TapeClock'])+struct.pack(">I",tape['TapeBarCount'])+struct.pack(">I",tape['FreeResourcesAfterPlay'])+struct.pack(">I",len(tape["MapName"]))+tape["MapName"].encode())
        tape_serialize.close()


def serializer(ckd, outpath):
    path='world/maps'
    if ckd.endswith("tape.ckd"):
        with open('output/temp/serializableObjects/'+ckd,'r',encoding="utf-8") as a:
            tape=json.load(a)
        print('Function_Serialize: Active')
        print('serializing '+ckd)
        codename=tape["MapName"]
        codenamelow=codename.lower()
        dtapeClips = 0
        ktapeClips = 0

        if ckd.endswith('_dance.dtape.ckd'):
            for clip in tape['Clips']:
                if clip['__class'] == 'MotionClip' and 'msm' in clip['ClassifierPath']:
                    dtapeClips += 1
                if clip['__class'] == 'PictogramClip':
                    dtapeClips += 1
                if clip['__class'] == 'GoldEffectClip':
                    dtapeClips += 1
        if ckd.endswith('_karaoke.ktape.ckd'):
            for clip in tape['Clips']:
                if clip['__class'] == 'KaraokeClip':
                    ktapeClips += 1

        try:
            for lyrictext in tape["Clips"]:
                if hanzidentifier.has_chinese(lyrictext["Lyrics"]):
                    lyrictext["Lyrics"]=pinyin.get(lyrictext['Lyrics'],format="strip",delimiter=" ")+" "
        except:
            pass

        tape_serialize=open(outpath+ckd,'ab')

        if ckd.endswith('_dance.dtape.ckd'):
            tape_len = dtapeClips
        if ckd.endswith('_karaoke.ktape.ckd'):
            tape_len = ktapeClips

        #tape_len=len(tape["Clips"])
        tape_version=int((224*tape_len)+166)
        if tape_len > 0:
            tape_serialize.write(struct.pack(">I",1)+struct.pack(">I",tape_version)+b'\x9E\x84\x54\x60\x00\x00\x00\x9C')
        if tape_len == 0:
            tape_serialize.write(b'\x00\x00\x00\x01\x00\x00\x4E\x5B\x9E\x84\x54\x60\x00\x00\x00\x9C')
        clips=struct.pack(">I",tape_len)
        for clip in tape["Clips"]:
            #ktape
            if clip['__class']=='KaraokeClip':
                lyrics=unidecode(clip["Lyrics"])
                clips+=b'\x68\x55\x2A\x41\x00\x00\x00\x50'
                clips+=struct.pack(">I",clip["Id"])
                clips+=struct.pack(">I",clip["TrackId"])
                clips+=struct.pack(">I",clip["IsActive"])
                clips+=struct.pack(">i",clip["StartTime"])
                clips+=struct.pack(">i",clip["Duration"])
                clips+=struct.pack(">f",clip["Pitch"])
                clips+=struct.pack(">I",len(lyrics))+lyrics.encode()
                clips+=struct.pack(">I",clip["IsEndOfLine"])
                clips+=struct.pack(">I",clip["ContentType"])
                clips+=struct.pack(">I",clip["StartTimeTolerance"])
                clips+=struct.pack(">I",clip["EndTimeTolerance"])
                clips+=struct.pack(">f",clip["SemitoneTolerance"])

            #dtape
            elif clip['__class']=='MotionClip' and 'msm' in clip['ClassifierPath']:
                filename=clip['ClassifierPath'].split("/")[-1]
                pathname=clip['ClassifierPath'].replace(filename,"").replace("world/maps",path)
                clips+=b'\x95\x53\x84\xA1\x00\x00\x00\x70'
                clips+=struct.pack(">I",clip["Id"])
                clips+=struct.pack(">I",clip["TrackId"])
                clips+=struct.pack(">I",clip["IsActive"])
                clips+=struct.pack(">i",clip["StartTime"])
                clips+=struct.pack(">i",clip["Duration"])
                clips+=struct.pack(">I",len(filename))+filename.encode()+struct.pack(">I",len(pathname))+pathname.encode()+struct.pack("<I",zlib.crc32(filename.encode()))
                clips+=struct.pack(">I",0)
                clips+=struct.pack(">I",clip["GoldMove"])
                clips+=struct.pack(">I",clip["CoachId"])
                clips+=struct.pack(">I",clip["MoveType"])
                clips+=struct.pack(">f",clip["Color"][3])
                clips+=struct.pack(">f",clip["Color"][2])
                clips+=struct.pack(">f",clip["Color"][1])
                clips+=struct.pack(">f",clip["Color"][0])
                #MotionPlatformSpecifics
                clips+=b'\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

            elif clip['__class']=='PictogramClip':
                filename=clip['PictoPath'].split("/")[-1]
                pathname=clip['PictoPath'].replace(filename,"").replace("world/maps",path)
                clips+=b'\x52\xEC\x89\x62\x00\x00\x00\x38'
                clips+=struct.pack(">I",clip["Id"])
                clips+=struct.pack(">I",clip["TrackId"])
                clips+=struct.pack(">I",clip["IsActive"])
                clips+=struct.pack(">i",clip["StartTime"])
                clips+=struct.pack(">i",clip["Duration"])
                clips+=struct.pack(">I",len(filename))+filename.encode()+struct.pack(">I",len(pathname))+pathname.encode()+struct.pack("<I",zlib.crc32(filename.encode()))
                clips+=b'\x00\x00\x00\x00\xFF\xFF\xFF\xFF'

            elif clip['__class']=='GoldEffectClip':
                clips+=b'\xFD\x69\xB1\x10\x00\x00\x00\x1C'
                clips+=struct.pack(">I",clip["Id"])
                clips+=struct.pack(">I",clip["TrackId"])
                clips+=struct.pack(">I",clip["IsActive"])
                clips+=struct.pack(">i",clip["StartTime"])
                clips+=struct.pack(">i",clip["Duration"])
                clips+=struct.pack(">I",clip["EffectType"])

        tape_serialize.write(clips)
        tape_serialize.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'+struct.pack(">I",tape['TapeClock'])+struct.pack(">I",tape['TapeBarCount'])+struct.pack(">I",tape['FreeResourcesAfterPlay'])+struct.pack(">I",len(tape["MapName"]))+tape["MapName"].encode())
        tape_serialize.close()

    if ckd.endswith("_musictrack.tpl.ckd"):
        with open('output/temp/serializableObjects/'+ckd) as b:
            mtrack=json.load(b)
        audiofile=mtrack['COMPONENTS'][0]['trackData']['path'].split('/')[-1]
        audiopath=mtrack['COMPONENTS'][0]['trackData']['path'].replace(audiofile,'').replace("world/maps",path)
        print('serializing '+ckd)
        codename=audiofile.replace(".wav","")
        codenamelow=codename.lower()

        mtversion=jdVersion

        beats=mtrack['COMPONENTS'][0]['trackData']['structure']['markers']
        try:
            signatures=mtrack['COMPONENTS'][0]['trackData']['structure']['signatures']
        except:
            signatures=0
        try:
            sections=mtrack['COMPONENTS'][0]['trackData']['structure']['sections']
        except:
            sections=0
        startbeat=mtrack['COMPONENTS'][0]['trackData']['structure']['startBeat']
        endbeat=mtrack['COMPONENTS'][0]['trackData']['structure']['endBeat']
        videostarttime=mtrack['COMPONENTS'][0]['trackData']['structure']['videoStartTime']

        mt_serializer=open('output/temp/serializedObjects/'+codenamelow+'_musictrack.main_legacy.tpl.ckd','wb')
        mt_serializer.write(b'\x00\x00\x00\x01'+struct.pack('>I',int((166*len(beats))+166))+b'\x1B\x85\x7B\xCE\x00\x00\x00\x6C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x88\x3A\x7E\x00\x00\x00\xA0\x00\x00\x00\x90\x00\x00\x00\x6C')

        #markers
        mt_serializer.write(struct.pack('>I',len(beats)))
        for marker in beats:
            mt_serializer.write(struct.pack('>I',marker))

        #signatures
        try:
            mt_serializer.write(struct.pack('>I',len(signatures)))
            for signature in signatures:
                mt_serializer.write(b'\x00\x00\x00\x08')
                mt_serializer.write(struct.pack('>i',signature['marker']))
                mt_serializer.write(struct.pack('>i',signature['beats']))
        except:
            mt_serializer.write(struct.pack('>I',0))

        #sections
        try:
            mt_serializer.write(struct.pack('>I',len(sections)))
            for section in sections:
                mt_serializer.write(b'\x00\x00\x00\x14')
                mt_serializer.write(struct.pack('>i',section['marker']))
                mt_serializer.write(struct.pack('>i',section['sectionType']))
                mt_serializer.write(struct.pack('>i',len(section['comment']))+section['comment'].encode())
        except:
            mt_serializer.write(struct.pack('>I',0))

        # beats and path
        if mtversion>=2018:
            mt_serializer.write(struct.pack('>i',startbeat)+struct.pack('>I',endbeat)+b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'+struct.pack('>f',videostarttime))
        else:
            mt_serializer.write(struct.pack('>i',startbeat)+struct.pack('>I',endbeat)+struct.pack('>f',videostarttime))

        if mtversion<=2017:
            mt_serializer.write(b'\x00\x00\x00\x00')

        elif mtversion>=2018:
            mt_serializer.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

        mt_serializer.write(struct.pack('>I',len(audiofile))+audiofile.encode()+struct.pack('>I',len(audiopath))+audiopath.encode()+struct.pack('<I',zlib.crc32(audiofile.encode())))

        mt_serializer.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
        mt_serializer.close()

def mainscenemaker(codename):

    #Credits: JackLSummer15 and RyanL181095
    codenamelow=codename.lower()
    os.makedirs('output/temp/'+codename+'_Wii_Mainscene/', exist_ok=True)
    outputpath='output/temp/'+codename+'_Wii_Mainscene/'
    # making directories
    os.makedirs(outputpath+'cache/itf_cooked/wii/cache/legacyconverteddata/'+codenamelow+'/audio', exist_ok=True)
    os.makedirs(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/audio', exist_ok=True)
    os.makedirs(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/cinematics', exist_ok=True)
    os.makedirs(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/graph', exist_ok=True)
    os.makedirs(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/actors', exist_ok=True)
    os.makedirs(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/textures/', exist_ok=True)
    os.makedirs(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/pictos', exist_ok=True)
    os.makedirs(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/videoscoach', exist_ok=True)
    os.makedirs(outputpath+'world/maps/'+codenamelow+'/timeline/moves/'+moveFolder+'/', exist_ok=True)
    os.makedirs(outputpath+'world/maps/'+codenamelow+'/videoscoach', exist_ok=True)

    emptytape=b'\x00\x00\x00\x01\x00\x00\x4E\x5B\x9E\x84\x54\x60\x00\x00\x00\x9C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00'+struct.pack(">I",len(codename))+codename.encode()

    # to bytes length: (len(input).to_bytes(4, 'big'))
    # struct length: struct.pack(">I",len(input))

    # audio

    cacheaudiopath='cache/legacyconverteddata/'+codenamelow+'/audio/'
    worldaudiopath='world/maps/'+codenamelow+'/audio/'
    sequencename=codename+'_sequence'
    sequencefilename=codenamelow+'_sequence.tpl'
    musictrackfilename=codenamelow+'_musictrack.main_legacy.tpl'
    stapename=codenamelow+'.stape'

    stape=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/audio/'+codenamelow+'.stape.ckd','wb')
    stape.write(emptytape)
    stape.close()

    sequencetpl=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/audio/'+codenamelow+'_sequence.tpl.ckd','wb')
    sequencetpl.write(b'\x00\x00\x00\x01\x00\x00\x00\xF8\x1B\x85\x7B\xCE\x00\x00\x00\x6C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x82\x29\xAB\xC3\x00\x00\x00\x40\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x28\xD5\xB5\x45\x97')
    sequencetpl.write(struct.pack(">I",len(stapename))+stapename.encode())
    sequencetpl.write(struct.pack(">I",len(worldaudiopath))+worldaudiopath.encode()+struct.pack("<I",zlib.crc32(stapename.encode())))
    sequencetpl.write(b'\x00\x00\x00\x00')
    sequencetpl.close()

    audioisc=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/audio/'+codenamelow+'_audio.isc.ckd','wb')
    audioisc.write(b'\x00\x00\x00\x01\x00\x03\x3E\x9E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x97\xCA\x62\x8B\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0A\x4D\x75\x73\x69\x63\x54\x72\x61\x63\x6B\xFF\xFF\xFF\xFF\x3F\x90\x1F\x86\xBE\xD6\x58\x1D\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00')
    audioisc.write(struct.pack(">I",len(musictrackfilename))+musictrackfilename.encode())
    audioisc.write(struct.pack(">I",len(cacheaudiopath))+cacheaudiopath.encode()+struct.pack("<I",zlib.crc32(musictrackfilename.encode())))
    audioisc.write(b'\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\x7A\x7C\x23\x5B\x97\xCA\x62\x8B\x35\x86\x37\xBD\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00')
    audioisc.write(struct.pack(">I",len(sequencename))+sequencename.encode())
    audioisc.write(b'\xFF\xFF\xFF\xFF\xBB\xC9\xC9\x0C\xBB\xC9\xC9\x0C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00')
    audioisc.write(struct.pack(">I",len(sequencefilename))+sequencefilename.encode())
    audioisc.write(struct.pack(">I",len(worldaudiopath))+worldaudiopath.encode()+struct.pack("<I",zlib.crc32(sequencefilename.encode())))
    audioisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x23\x1F\x27\xDE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    audioisc.close()

    # cinematics

    mainsequencename=codename+'_MainSequence'
    cinetapename=codenamelow+'_mainsequence.tape'
    cinetplname=codenamelow+'_mainsequence.tpl'
    cinepath='world/maps/'+codenamelow+'/cinematics/'

    cinetape=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/cinematics/'+codenamelow+'_mainsequence.tape.ckd','wb')
    cinetape.write(emptytape)
    cinetape.close()

    cineact=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/cinematics/'+codenamelow+'_mainsequence.act.ckd','wb')
    cineact.write(b'\x00\x00\x00\x01\x00\x00\x01\x04\x1B\x85\x7B\xCE\x00\x00\x00\x6C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x0C\x73\x64\x97\x00\x00\x00\x40\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x28\xAB\xF3\x77\x3E')
    cineact.write(struct.pack(">I",len(cinetapename))+cinetapename.encode())
    cineact.write(struct.pack(">I",len(cinepath))+cinepath.encode()+struct.pack("<I",zlib.crc32(cinetapename.encode())))
    cineact.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x67\x7B\x26\x9B')
    cineact.close()

    cinetpl=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/cinematics/'+codenamelow+'_mainsequence.tpl.ckd','wb')
    cinetpl.write(b'\x00\x00\x00\x01\x00\x00\x01\x05\x1B\x85\x7B\xCE\x00\x00\x00\x6C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x0C\x73\x64\x97\x00\x00\x00\x40\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x28\xAB\xF3\x77\x3E')
    cinetpl.write(struct.pack(">I",len(cinetapename))+cinetapename.encode())
    cinetpl.write(struct.pack(">I",len(cinepath))+cinepath.encode()+struct.pack("<I",zlib.crc32(cinetapename.encode())))
    cinetpl.write(b'\x00\x00\x00\x00')
    cinetpl.close()

    cineisc=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/cinematics/'+codenamelow+'_cine.isc.ckd','wb')
    cineisc.write(b'\x00\x00\x00\x01\x00\x04\x26\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x97\xCA\x62\x8B\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00')
    cineisc.write(struct.pack(">I",len(mainsequencename))+mainsequencename.encode())
    cineisc.write(b'\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00')
    cineisc.write(struct.pack(">I",len(cinetplname))+cinetplname.encode())
    cineisc.write(struct.pack(">I",len(cinepath))+cinepath.encode()+struct.pack("<I",zlib.crc32(cinetplname.encode())))
    cineisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x67\x7B\x26\x9B\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    cineisc.close()

    # graph
    graphpath='world/maps/'+codenamelow+'/graph/'

    graphisc=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/graph/'+codenamelow+'_graph.isc.ckd','wb')
    graphisc.write(b'\x00\x00\x00\x01\x00\x03\x3E\x9E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x97\xCA\x62\x8B\x41\x20\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0F\x43\x61\x6D\x65\x72\x61\x5F\x4A\x44\x5F\x44\x75\x6D\x6D\x79\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x12\x74\x70\x6C\x5F\x65\x6D\x70\x74\x79\x61\x63\x74\x6F\x72\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\x59\xDA\xF9\xC2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    graphisc.close()

    # menuart

    menuartpath='world/maps/'+codenamelow+'/menuart/textures/'
    generictganame=codenamelow+'_cover_generic.tga'
    onlinetganame=codenamelow+'_cover_online.tga'
    albumbkgtganame=codenamelow+'_cover_albumbkg.tga'
    albumcoachtganame=codenamelow+'_cover_albumcoach.tga'
    coach1tganame=codenamelow+'_coach_1.tga'
    coach2tganame=codenamelow+'_coach_2.tga'
    coach3tganame=codenamelow+'_coach_3.tga'
    coach4tganame=codenamelow+'_coach_4.tga'

    genericname=codename+'_cover_generic'
    onlinename=codename+'_cover_online'
    albumbkgname=codename+'_cover_albumbkg'
    albumcoachname=codename+'_cover_albumcoach'
    coach1name=codename+'_coach_1'
    coach2name=codename+'_coach_2'
    coach3name=codename+'_coach_3'
    coach4name=codename+'_coach_4'

    menuarttop=b'\x00\x00\x00\x01\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x22\x74\x70\x6C\x5F\x6D\x61\x74\x65\x72\x69\x61\x6C\x67\x72\x61\x70\x68\x69\x63\x63\x6F\x6D\x70\x6F\x6E\x65\x6E\x74\x32\x64\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\xB4\xA8\x17\xA8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x72\xB6\x1F\xC5\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00'
    menuartbottom=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x17\x6D\x75\x6C\x74\x69\x74\x65\x78\x74\x75\x72\x65\x5F\x31\x6C\x61\x79\x65\x72\x2E\x6D\x73\x68\x00\x00\x00\x18\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x6D\x61\x74\x73\x68\x61\x64\x65\x72\x2F\xD7\xE7\xD9\xC7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'

    coach1act=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/actors/'+codenamelow+'_coach_1.act.ckd','wb')
    coach1act.write(menuarttop)
    coach1act.write(struct.pack(">I",len(coach1tganame))+coach1tganame.encode())
    coach1act.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(coach1tganame.encode())))
    coach1act.write(menuartbottom)
    coach1act.close()

    coach2act=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/actors/'+codenamelow+'_coach_2.act.ckd','wb')
    coach2act.write(menuarttop)
    coach2act.write(struct.pack(">I",len(coach2tganame))+coach2tganame.encode())
    coach2act.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(coach2tganame.encode())))
    coach2act.write(menuartbottom)
    coach2act.close()

    coach3act=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/actors/'+codenamelow+'_coach_3.act.ckd','wb')
    coach3act.write(menuarttop)
    coach3act.write(struct.pack(">I",len(coach3tganame))+coach3tganame.encode())
    coach3act.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(coach3tganame.encode())))
    coach3act.write(menuartbottom)
    coach3act.close()

    coach4act=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/actors/'+codenamelow+'_coach_4.act.ckd','wb')
    coach4act.write(menuarttop)
    coach4act.write(struct.pack(">I",len(coach4tganame))+coach4tganame.encode())
    coach4act.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(coach4tganame.encode())))
    coach4act.write(menuartbottom)
    coach4act.close()

    albumbkgact=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/actors/'+codenamelow+'_cover_albumbkg.act.ckd','wb')
    albumbkgact.write(menuarttop)
    albumbkgact.write(struct.pack(">I",len(albumbkgtganame))+albumbkgtganame.encode())
    albumbkgact.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(albumbkgtganame.encode())))
    albumbkgact.write(menuartbottom)
    albumbkgact.close()

    albumcoachact=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/actors/'+codenamelow+'_cover_albumcoach.act.ckd','wb')
    albumcoachact.write(menuarttop)
    albumcoachact.write(struct.pack(">I",len(albumcoachtganame))+albumcoachtganame.encode())
    albumcoachact.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(albumcoachtganame.encode())))
    albumcoachact.write(menuartbottom)
    albumcoachact.close()

    genericact=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/actors/'+codenamelow+'_cover_generic.act.ckd','wb')
    genericact.write(menuarttop)
    genericact.write(struct.pack(">I",len(generictganame))+generictganame.encode())
    genericact.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(generictganame.encode())))
    genericact.write(menuartbottom)
    genericact.close()

    onlineact=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/actors/'+codenamelow+'_cover_online.act.ckd','wb')
    onlineact.write(menuarttop)
    onlineact.write(struct.pack(">I",len(onlinetganame))+onlinetganame.encode())
    onlineact.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(onlinetganame.encode())))
    onlineact.write(menuartbottom)
    onlineact.close()

    menuartisc=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/'+codenamelow+'_menuart.isc.ckd','wb')
    menuartisc.write(b'\x00\x00\x00\x01\x00\x04\x26\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x08\x97\xCA\x62\x8B\x00\x00\x00\x00\x3E\x99\x99\x9A\x3E\x99\x99\x9A\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(genericname))+genericname.encode())
    menuartisc.write(b'\xFF\xFF\xFF\xFF\x43\x85\x0B\x35\x43\x45\xA1\x45\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x22\x74\x70\x6C\x5F\x6D\x61\x74\x65\x72\x69\x61\x6C\x67\x72\x61\x70\x68\x69\x63\x63\x6F\x6D\x70\x6F\x6E\x65\x6E\x74\x32\x64\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\xB4\xA8\x17\xA8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x72\xB6\x1F\xC5\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(generictganame))+generictganame.encode())
    menuartisc.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(generictganame.encode())))
    menuartisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x17\x6D\x75\x6C\x74\x69\x74\x65\x78\x74\x75\x72\x65\x5F\x31\x6C\x61\x79\x65\x72\x2E\x6D\x73\x68\x00\x00\x00\x18\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x6D\x61\x74\x73\x68\x61\x64\x65\x72\x2F\xD7\xE7\xD9\xC7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x97\xCA\x62\x8B\x00\x00\x00\x00\x3E\x99\x99\x9A\x3E\x99\x99\x9A\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(onlinename))+onlinename.encode())
    menuartisc.write(b'\xFF\xFF\xFF\xFF\xC3\x16\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x22\x74\x70\x6C\x5F\x6D\x61\x74\x65\x72\x69\x61\x6C\x67\x72\x61\x70\x68\x69\x63\x63\x6F\x6D\x70\x6F\x6E\x65\x6E\x74\x32\x64\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\xB4\xA8\x17\xA8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x72\xB6\x1F\xC5\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(onlinetganame))+onlinetganame.encode())
    menuartisc.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(onlinetganame.encode())))
    menuartisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x17\x6D\x75\x6C\x74\x69\x74\x65\x78\x74\x75\x72\x65\x5F\x31\x6C\x61\x79\x65\x72\x2E\x6D\x73\x68\x00\x00\x00\x18\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x6D\x61\x74\x73\x68\x61\x64\x65\x72\x2F\xD7\xE7\xD9\xC7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x97\xCA\x62\x8B\x00\x00\x00\x00\x3E\x99\x99\x9A\x3E\x99\x99\x9A\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(albumcoachname))+albumcoachname.encode())
    menuartisc.write(b'\xFF\xFF\xFF\xFF\x44\x38\x86\xCE\x43\xB3\xCE\x57\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x22\x74\x70\x6C\x5F\x6D\x61\x74\x65\x72\x69\x61\x6C\x67\x72\x61\x70\x68\x69\x63\x63\x6F\x6D\x70\x6F\x6E\x65\x6E\x74\x32\x64\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\xB4\xA8\x17\xA8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x72\xB6\x1F\xC5\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(albumcoachtganame))+albumcoachtganame.encode())
    menuartisc.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(albumcoachtganame.encode())))
    menuartisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x17\x6D\x75\x6C\x74\x69\x74\x65\x78\x74\x75\x72\x65\x5F\x31\x6C\x61\x79\x65\x72\x2E\x6D\x73\x68\x00\x00\x00\x18\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x6D\x61\x74\x73\x68\x61\x64\x65\x72\x2F\xD7\xE7\xD9\xC7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x97\xCA\x62\x8B\x00\x00\x00\x00\x3E\x99\x99\x9A\x3E\x99\x99\x9A\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(albumbkgname))+albumbkgname.encode())
    menuartisc.write(b'\xFF\xFF\xFF\xFF\x44\x38\x86\xCE\x43\xB3\xCE\x57\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x22\x74\x70\x6C\x5F\x6D\x61\x74\x65\x72\x69\x61\x6C\x67\x72\x61\x70\x68\x69\x63\x63\x6F\x6D\x70\x6F\x6E\x65\x6E\x74\x32\x64\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\xB4\xA8\x17\xA8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x72\xB6\x1F\xC5\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(albumbkgtganame))+albumbkgtganame.encode())
    menuartisc.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(albumbkgtganame.encode())))
    menuartisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x17\x6D\x75\x6C\x74\x69\x74\x65\x78\x74\x75\x72\x65\x5F\x31\x6C\x61\x79\x65\x72\x2E\x6D\x73\x68\x00\x00\x00\x18\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x6D\x61\x74\x73\x68\x61\x64\x65\x72\x2F\xD7\xE7\xD9\xC7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x97\xCA\x62\x8B\x00\x00\x00\x00\x3E\x99\x99\x9A\x3E\x99\x99\x9A\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(coach1name))+coach1name.encode())
    menuartisc.write(b'\xFF\xFF\xFF\xFF\x44\x38\x86\xCE\x43\xB3\xCE\x57\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x22\x74\x70\x6C\x5F\x6D\x61\x74\x65\x72\x69\x61\x6C\x67\x72\x61\x70\x68\x69\x63\x63\x6F\x6D\x70\x6F\x6E\x65\x6E\x74\x32\x64\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\xB4\xA8\x17\xA8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x72\xB6\x1F\xC5\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(coach1tganame))+coach1tganame.encode())
    menuartisc.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(coach1tganame.encode())))
    menuartisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x17\x6D\x75\x6C\x74\x69\x74\x65\x78\x74\x75\x72\x65\x5F\x31\x6C\x61\x79\x65\x72\x2E\x6D\x73\x68\x00\x00\x00\x18\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x6D\x61\x74\x73\x68\x61\x64\x65\x72\x2F\xD7\xE7\xD9\xC7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x97\xCA\x62\x8B\x00\x00\x00\x00\x3E\x99\x99\x9A\x3E\x99\x99\x9A\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(coach2name))+coach2name.encode())
    menuartisc.write(b'\xFF\xFF\xFF\xFF\x44\x38\x86\xCE\x43\xB3\xCE\x57\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x22\x74\x70\x6C\x5F\x6D\x61\x74\x65\x72\x69\x61\x6C\x67\x72\x61\x70\x68\x69\x63\x63\x6F\x6D\x70\x6F\x6E\x65\x6E\x74\x32\x64\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\xB4\xA8\x17\xA8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x72\xB6\x1F\xC5\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(coach2tganame))+coach2tganame.encode())
    menuartisc.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(coach2tganame.encode())))
    menuartisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x17\x6D\x75\x6C\x74\x69\x74\x65\x78\x74\x75\x72\x65\x5F\x31\x6C\x61\x79\x65\x72\x2E\x6D\x73\x68\x00\x00\x00\x18\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x6D\x61\x74\x73\x68\x61\x64\x65\x72\x2F\xD7\xE7\xD9\xC7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x97\xCA\x62\x8B\x00\x00\x00\x00\x3E\x99\x99\x9A\x3E\x99\x99\x9A\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(coach3name))+coach3name.encode())
    menuartisc.write(b'\xFF\xFF\xFF\xFF\x44\x38\x86\xCE\x43\xB3\xCE\x57\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x22\x74\x70\x6C\x5F\x6D\x61\x74\x65\x72\x69\x61\x6C\x67\x72\x61\x70\x68\x69\x63\x63\x6F\x6D\x70\x6F\x6E\x65\x6E\x74\x32\x64\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\xB4\xA8\x17\xA8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x72\xB6\x1F\xC5\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(coach3tganame))+coach3tganame.encode())
    menuartisc.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(coach3tganame.encode())))
    menuartisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x17\x6D\x75\x6C\x74\x69\x74\x65\x78\x74\x75\x72\x65\x5F\x31\x6C\x61\x79\x65\x72\x2E\x6D\x73\x68\x00\x00\x00\x18\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x6D\x61\x74\x73\x68\x61\x64\x65\x72\x2F\xD7\xE7\xD9\xC7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x97\xCA\x62\x8B\x00\x00\x00\x00\x3E\x99\x99\x9A\x3E\x99\x99\x9A\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(coach4name))+coach4name.encode())
    menuartisc.write(b'\xFF\xFF\xFF\xFF\x44\x38\x86\xCE\x43\xB3\xCE\x57\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x22\x74\x70\x6C\x5F\x6D\x61\x74\x65\x72\x69\x61\x6C\x67\x72\x61\x70\x68\x69\x63\x63\x6F\x6D\x70\x6F\x6E\x65\x6E\x74\x32\x64\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\xB4\xA8\x17\xA8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x72\xB6\x1F\xC5\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00')
    menuartisc.write(struct.pack(">I",len(coach4tganame))+coach4tganame.encode())
    menuartisc.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(coach4tganame.encode())))
    menuartisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x17\x6D\x75\x6C\x74\x69\x74\x65\x78\x74\x75\x72\x65\x5F\x31\x6C\x61\x79\x65\x72\x2E\x6D\x73\x68\x00\x00\x00\x18\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x6D\x61\x74\x73\x68\x61\x64\x65\x72\x2F\xD7\xE7\xD9\xC7\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01')
    menuartisc.close()

    # timeline

    tmlpath='world/maps/'+codenamelow+'/timeline/'
    tmldancename=codename+'_tml_dance'
    tmlkaraokename=codename+'_tml_karaoke'
    tmldancetape=codenamelow+'_tml_dance.dtape'
    tmlkaraoketape=codenamelow+'_tml_karaoke.ktape'
    tmldancetpl=codenamelow+'_tml_dance.tpl'
    tmlkaraoketpl=codenamelow+'_tml_karaoke.tpl'

    dtape=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_dance.dtape.ckd','wb')
    dtape.write(emptytape)
    dtape.close()

    ktape=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_karaoke.ktape.ckd','wb')
    ktape.write(emptytape)
    ktape.close()

    tmlisc=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml.isc.ckd','wb')
    tmlisc.write(b'\x00\x00\x00\x01\x00\x03\x3E\x9E\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x97\xCA\x62\x8B\x35\x86\x37\xBD\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00')
    tmlisc.write(struct.pack(">I",len(tmldancename))+tmldancename.encode())
    tmlisc.write(b'\xFF\xFF\xFF\xFF\xBF\x94\x30\xD3\x3B\xC9\xC9\x0C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00')
    tmlisc.write(struct.pack(">I",len(tmldancetpl))+tmldancetpl.encode())
    tmlisc.write(struct.pack(">I",len(tmlpath))+tmlpath.encode()+struct.pack("<I",zlib.crc32(tmldancetpl.encode())))
    tmlisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x23\x1F\x27\xDE\x97\xCA\x62\x8B\x35\x86\x37\xBD\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00')
    tmlisc.write(struct.pack(">I",len(tmlkaraokename))+tmlkaraokename.encode())
    tmlisc.write(b'\xFF\xFF\xFF\xFF\xBF\x94\x30\xD3\x3B\xC9\xC9\x0C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00')
    tmlisc.write(struct.pack(">I",len(tmlkaraoketpl))+tmlkaraoketpl.encode())
    tmlisc.write(struct.pack(">I",len(tmlpath))+tmlpath.encode()+struct.pack("<I",zlib.crc32(tmlkaraoketpl.encode())))
    tmlisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x23\x1F\x27\xDE\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    tmlisc.close()

    danceact=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_dance.act.ckd','wb')
    danceact.write(b'\x00\x00\x00\x01\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00')
    danceact.write(struct.pack(">I",len(tmldancetpl))+tmldancetpl.encode())
    danceact.write(struct.pack(">I",len(tmlpath))+tmlpath.encode()+struct.pack("<I",zlib.crc32(tmldancetpl.encode())))
    danceact.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x23\x1F\x27\xDE')
    danceact.close()

    karaokeact=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_karaoke.act.ckd','wb')
    karaokeact.write(b'\x00\x00\x00\x01\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00')
    karaokeact.write(struct.pack(">I",len(tmlkaraoketpl))+tmlkaraoketpl.encode())
    karaokeact.write(struct.pack(">I",len(tmlpath))+tmlpath.encode()+struct.pack("<I",zlib.crc32(tmlkaraoketpl.encode())))
    karaokeact.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x23\x1F\x27\xDE')
    karaokeact.close()

    dancetpl=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_dance.tpl.ckd','wb')
    dancetpl.write(b'\x00\x00\x00\x01\x00\x00\x01\x02\x1B\x85\x7B\xCE\x00\x00\x00\x6C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x82\x29\xAB\xC3\x00\x00\x00\x40\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x28\x24\xA3\x7B\xF0')
    dancetpl.write(struct.pack(">I",len(tmldancetape))+tmldancetape.encode())
    dancetpl.write(struct.pack(">I",len(tmlpath))+tmlpath.encode()+struct.pack("<I",zlib.crc32(tmldancetape.encode())))
    dancetpl.write(b'\x00\x00\x00\x00')
    dancetpl.close()

    karaoketpl=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_karaoke.tpl.ckd','wb')
    karaoketpl.write(b'\x00\x00\x00\x01\x00\x00\x01\x05\x1B\x85\x7B\xCE\x00\x00\x00\x6C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x82\x29\xAB\xC3\x00\x00\x00\x40\x00\x00\x00\x01\x00\x00\x00\x10\x00\x00\x00\x01\x00\x00\x00\x28\xFD\x45\x47\xAC')
    karaoketpl.write(struct.pack(">I",len(tmlkaraoketape))+tmlkaraoketape.encode())
    karaoketpl.write(struct.pack(">I",len(tmlpath))+tmlpath.encode()+struct.pack("<I",zlib.crc32(tmlkaraoketape.encode())))
    karaoketpl.write(b'\x00\x00\x00\x00')
    karaoketpl.close()

    # videoscoach

    webmname=codenamelow+'.webm'
    videoscoachpath='world/maps/'+codenamelow+'/videoscoach/'

    videoplayermainact=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/videoscoach/video_player_main.act.ckd','wb')
    videoplayermainact.write(b'\x00\x00\x00\x01\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x15\x76\x69\x64\x65\x6F\x5F\x70\x6C\x61\x79\x65\x72\x5F\x6D\x61\x69\x6E\x2E\x74\x70\x6C\x00\x00\x00\x1A\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x76\x69\x64\x65\x6F\x73\x63\x72\x65\x65\x6E\x2F\xF5\xD5\xE8\xF2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x12\x63\xDA\xD9')
    videoplayermainact.write(struct.pack(">I",len(webmname))+webmname.encode())
    videoplayermainact.write(struct.pack(">I",len(videoscoachpath))+videoscoachpath.encode()+struct.pack("<I",zlib.crc32(webmname.encode())))
    videoplayermainact.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    videoplayermainact.close()

    videoisc=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/videoscoach/'+codenamelow+'_video.isc.ckd','wb')
    videoisc.write(b'\x00\x00\x00\x01\x00\x04\x26\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\x97\xCA\x62\x8B\xBF\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0B\x56\x69\x64\x65\x6F\x53\x63\x72\x65\x65\x6E\xFF\xFF\xFF\xFF\x00\x00\x00\x00\xC0\x90\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x15\x76\x69\x64\x65\x6F\x5F\x70\x6C\x61\x79\x65\x72\x5F\x6D\x61\x69\x6E\x2E\x74\x70\x6C\x00\x00\x00\x1A\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x76\x69\x64\x65\x6F\x73\x63\x72\x65\x65\x6E\x2F\xF5\xD5\xE8\xF2\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x12\x63\xDA\xD9')
    videoisc.write(struct.pack(">I",len(webmname))+webmname.encode())
    videoisc.write(struct.pack(">I",len(videoscoachpath))+videoscoachpath.encode()+struct.pack("<I",zlib.crc32(webmname.encode())))
    videoisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x97\xCA\x62\x8B\x00\x00\x00\x00\x40\x7C\x3D\x3E\x40\x0E\x14\x7B\x00\x00\x00\x00\x00\x00\x00\x0B\x56\x69\x64\x65\x6F\x4F\x75\x74\x70\x75\x74\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x15\x76\x69\x64\x65\x6F\x5F\x6F\x75\x74\x70\x75\x74\x5F\x6D\x61\x69\x6E\x2E\x74\x70\x6C\x00\x00\x00\x1A\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x76\x69\x64\x65\x6F\x73\x63\x72\x65\x65\x6E\x2F\xB5\x67\xD0\x71\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x05\x79\xE8\x1B\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x12\x70\x6C\x65\x6F\x66\x75\x6C\x6C\x73\x63\x72\x65\x65\x6E\x2E\x6D\x73\x68\x00\x00\x00\x18\x77\x6F\x72\x6C\x64\x2F\x5F\x63\x6F\x6D\x6D\x6F\x6E\x2F\x6D\x61\x74\x73\x68\x61\x64\x65\x72\x2F\x6A\x06\xE8\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    videoisc.close()

    # songdesc

    songdesctpl='songdesc.main_legacy.tpl'
    songdescpath='cache/legacyconverteddata/'+codenamelow+'/'

    descact=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/songdesc.act.ckd','wb')
    descact.write(b'\x00\x00\x00\x01\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00')
    descact.write(struct.pack(">I",len(songdesctpl))+songdesctpl.encode())
    descact.write(struct.pack(">I",len(songdescpath))+songdescpath.encode()+struct.pack("<I",zlib.crc32(songdescpath.encode())))
    descact.write(b'\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\xE0\x7F\xCC\x3F')
    descact.close()

    #making a placeholder songdesc.tpl
    songdescenc=open(outputpath+'cache/itf_cooked/wii/cache/legacyconverteddata/'+codenamelow+'/songdesc.main_legacy.tpl.ckd','wb')
    songdescenc.write(b'\x00\x00\x00\x01\x00\x00\x15\xA5\x1B\x85\x7B\xCE\x00\x00\x00\x6C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x8A\xC2\xB5\xC6\x00\x00\x00\xF4')
    songdescenc.write(struct.pack('>i',len(codename))+codename.encode())
    songdescenc.write(b'\x00\x00\x07\xE0\x00\x00\x07\xE0\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x58\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\xFF\xFF\xFF\xFF\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x01')
    songdescenc.write(struct.pack('>i',len(codename))+codename.encode())
    songdescenc.write(b'\x00\x00\x00\x0E\x55\x6E\x6B\x6E\x6F\x77\x6E\x20\x44\x61\x6E\x63\x65\x72')
    songdescenc.write(struct.pack('>i',len(codename))+codename.encode())
    songdescenc.write(b'\x00\x00\x00\x01')#coachcount
    songdescenc.write(b'\xFF\xFF\xFF\xFF\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x3F\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x10\x6F\x40\x37\xD0\x00\x00\x00\xC6\x00\x00\x00\x00\x00\x00\x00\x10\xB1\x1F\xC1\xB6\x00\x00\x00\x64\x00\x00\x01\xB8\x00\x00\x00\x02\x31\xD3\xB3\x47\x3F\x80\x00\x00\x3D\xE0\xE0\xEB\x3F\x26\xA6\xA0\x3F\x46\xC6\xCE\x9C\xD9\x0B\xCB\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    # mainscene isc and sgs

    audioiscfilename=codenamelow+'_audio.isc'
    cineiscfilename=codenamelow+'_cine.isc'
    graphiscfilename=codenamelow+'_graph.isc'
    menuartiscfilename=codenamelow+'_menuart.isc'
    tmliscfilename=codenamelow+'_tml.isc'
    videoiscfilename=codenamelow+'_video.isc'

    audioiscname=codename+'_AUDIO'
    cineiscname=codename+'_CINE'
    graphiscname=codename+'_GRAPH'
    menuartiscname=codename+'_menuart'
    tmliscname=codename+'_TML'
    videoiscname=codename+'_VIDEO'

    mainscenesgs=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/'+codenamelow+'_main_scene.sgs.ckd','wb')
    mainscenesgs.write(b'\x00\x00\x00\x01\xCE\x01\x8E\xDB\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    mainscenesgs.close()

    mainsceneisc=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/'+codenamelow+'_main_scene.isc.ckd','wb')

    mainsceneisc.write(b'\x00\x00\x00\x01\x00\x04\x26\xDD\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07\x4F\xA4\x0F\x09\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00')

    #read audioisc
    mainsceneisc.write(struct.pack(">I",len(audioiscname))+audioiscname.encode())
    mainsceneisc.write(b'\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x0C\x73\x75\x62\x73\x63\x65\x6E\x65\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\x69\x93\x4B\xE0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(audioiscfilename))+audioiscfilename.encode())
    mainsceneisc.write(struct.pack(">I",len(worldaudiopath))+worldaudiopath.encode()+struct.pack("<I",zlib.crc32(audioiscfilename.encode())))
    mainsceneisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02')

    audiocontent=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/audio/'+codenamelow+'_audio.isc.ckd','rb')
    mainsceneisc.write(audiocontent.read())

    #read cineisc
    mainsceneisc.write(b'\x4F\xA4\x0F\x09\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(cineiscname))+cineiscname.encode())
    mainsceneisc.write(b'\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x0C\x73\x75\x62\x73\x63\x65\x6E\x65\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\x69\x93\x4B\xE0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(cineiscfilename))+cineiscfilename.encode())
    mainsceneisc.write(struct.pack(">I",len(cinepath))+cinepath.encode()+struct.pack("<I",zlib.crc32(cineiscfilename.encode())))
    mainsceneisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02')

    cinecontent=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/cinematics/'+codenamelow+'_cine.isc.ckd','rb')
    mainsceneisc.write(cinecontent.read())

    #read graphisc
    mainsceneisc.write(b'\x4F\xA4\x0F\x09\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(graphiscname))+graphiscname.encode())
    mainsceneisc.write(b'\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x0C\x73\x75\x62\x73\x63\x65\x6E\x65\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\x69\x93\x4B\xE0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(graphiscfilename))+graphiscfilename.encode())
    mainsceneisc.write(struct.pack(">I",len(graphpath))+graphpath.encode()+struct.pack("<I",zlib.crc32(graphiscfilename.encode())))
    mainsceneisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02')

    graphcontent=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/graph/'+codenamelow+'_graph.isc.ckd','rb')
    mainsceneisc.write(graphcontent.read())

    #read tmlisc
    mainsceneisc.write(b'\x4F\xA4\x0F\x09\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(tmliscname))+tmliscname.encode())
    mainsceneisc.write(b'\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x0C\x73\x75\x62\x73\x63\x65\x6E\x65\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\x69\x93\x4B\xE0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(tmliscfilename))+tmliscfilename.encode())
    mainsceneisc.write(struct.pack(">I",len(tmlpath))+tmlpath.encode()+struct.pack("<I",zlib.crc32(tmliscfilename.encode())))
    mainsceneisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02')

    tmlcontent=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml.isc.ckd','rb')
    mainsceneisc.write(tmlcontent.read())

    #read videoisc
    mainsceneisc.write(b'\x4F\xA4\x0F\x09\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(videoiscname))+videoiscname.encode())
    mainsceneisc.write(b'\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x0C\x73\x75\x62\x73\x63\x65\x6E\x65\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\x69\x93\x4B\xE0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(videoiscfilename))+videoiscfilename.encode())
    mainsceneisc.write(struct.pack(">I",len(videoscoachpath))+videoscoachpath.encode()+struct.pack("<I",zlib.crc32(videoiscfilename.encode())))
    mainsceneisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x02')

    videocontent=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/videoscoach/'+codenamelow+'_video.isc.ckd','rb')
    mainsceneisc.write(videocontent.read())

    #read songdesc
    descplaceholder=codename+' : Template Artist - Template Title.JDVer = 5, ID = 842776738, Type = 1 (Flags 0x00000000), NbCoach = 2, Difficulty = 2'

    mainsceneisc.write(b'\x97\xCA\x62\x8B\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(descplaceholder))+descplaceholder.encode())
    mainsceneisc.write(b'\xFF\xFF\xFF\xFF\xC0\x62\x0B\xE5\xBF\xBE\x1F\x08\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    songdesccontent=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/songdesc.act.ckd','rb')
    uselessheader=songdesccontent.read(48)
    songdescpathdata=songdesccontent.read()

    mainsceneisc.write(songdescpathdata)

    #read menuartisc
    mainsceneisc.write(b'\x4F\xA4\x0F\x09\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(menuartiscname))+menuartiscname.encode())
    mainsceneisc.write(b'\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x0C\x73\x75\x62\x73\x63\x65\x6E\x65\x2E\x74\x70\x6C\x00\x00\x00\x1A\x65\x6E\x67\x69\x6E\x65\x64\x61\x74\x61\x2F\x61\x63\x74\x6F\x72\x74\x65\x6D\x70\x6C\x61\x74\x65\x73\x2F\x69\x93\x4B\xE0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    mainsceneisc.write(struct.pack(">I",len(menuartiscfilename))+menuartiscfilename.encode())
    mainsceneisc.write(struct.pack(">I",len(menuartpath))+menuartpath.encode()+struct.pack("<I",zlib.crc32(menuartiscfilename.encode())))
    mainsceneisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x03')

    menuartcontent=open(outputpath+'cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/'+codenamelow+'_menuart.isc.ckd','rb')

    mainsceneisc.write(menuartcontent.read())
    mainsceneisc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xCE\x01\x8E\xDB\x00\x00\x00\x00\x00\x00\x00\x06\x00\x00\x00\x01\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
    mainsceneisc.close()

def textureExtractorNX(texture, path, outpath):
    if texture.endswith('.png.ckd'):
        with open(path+texture, 'rb') as jdudds:
            jdudds.read(44)
            newddspng=jdudds.read()
            with open(outpath+texture.split('.')[0]+'.xtx', 'wb') as newdds2:
                newdds2.write(newddspng)

    elif texture.endswith('.tga.ckd'):
        with open(path+texture, 'rb') as jdudds:
            jdudds.read(44)
            newddstga=jdudds.read()
            with open(outpath+texture.split('.')[0]+'.xtx', 'wb') as newdds2:
                newdds2.write(newddstga)
    
    os.system('bin\\xtx_extract -o "'+outpath+texture.split('.')[0]+'.dds" "'+outpath+texture.split('.')[0]+'.xtx"')
    os.remove(outpath+texture.split('.')[0]+'.xtx')

def textureExtractorDDS(texture, path, outpath):
    if texture.endswith('.png.ckd'):
        with open(path+texture, 'rb') as jdudds:
            jdudds.read(44)
            newddspng=jdudds.read()
            with open(outpath+texture.split('.')[0]+'.dds', 'wb') as newdds2:
                newdds2.write(newddspng)

    elif texture.endswith('.tga.ckd'):
        with open(path+texture, 'rb') as jdudds:
            jdudds.read(44)
            newddstga=jdudds.read()
            with open(outpath+texture.split('.')[0]+'.dds', 'wb') as newdds2:
                newdds2.write(newddstga)

def serialize_sd(jdversion, songdesc, musictrack, output):
    with open(songdesc) as f:
        songdescjson=json.load(f)
    with open(musictrack) as g:
        musictrackjson=json.load(g)

    Codename=songdescjson['COMPONENTS'][0]['MapName']
    CodenameLow=Codename.lower()
    preventry=musictrackjson['COMPONENTS'][0]['trackData']['structure']['previewEntry']
    prevloopstart=musictrackjson['COMPONENTS'][0]['trackData']['structure']['previewLoopStart']
    prevloopend=musictrackjson['COMPONENTS'][0]['trackData']['structure']['previewLoopEnd']
    Artist=songdescjson['COMPONENTS'][0]['Artist']
    Title=songdescjson['COMPONENTS'][0]['Title']
    JDVersion=songdescjson['COMPONENTS'][0]['JDVersion']
    OriginalJDVersion=songdescjson['COMPONENTS'][0]['OriginalJDVersion']
    DancerName=songdescjson['COMPONENTS'][0]['DancerName']
    NumCoach=songdescjson['COMPONENTS'][0]['NumCoach']
    Difficulty=songdescjson['COMPONENTS'][0]['Difficulty']
    bgtype=songdescjson['COMPONENTS'][0]['backgroundType']
    lyrictype=songdescjson['COMPONENTS'][0]['LyricsType']
    lyriccolor0=songdescjson['COMPONENTS'][0]['DefaultColors']['lyrics'][0]
    lyriccolor1=songdescjson['COMPONENTS'][0]['DefaultColors']['lyrics'][1]
    lyriccolor2=songdescjson['COMPONENTS'][0]['DefaultColors']['lyrics'][2]
    lyriccolor3=songdescjson['COMPONENTS'][0]['DefaultColors']['lyrics'][3]
    songcolor_1b=[1.0, 0.266667, 0.266667, 0.266667]
    songcolor_1a=[1.0, 0.266667, 0.266667, 0.266667]
    songcolor_2b=[1.0, 0.266667, 0.266667, 0.266667]
    songcolor_2a=[1.0, 0.266667, 0.266667, 0.266667]
    theme=songdescjson['COMPONENTS'][0]['DefaultColors']['theme']
    if songdescjson['COMPONENTS'][0]['LocaleID'] == 4294967295:
        LocaleID=4294967295
        TitleMode=0
        if songdescjson['COMPONENTS'][0]['Tags'] == 'alternate' or songdescjson['COMPONENTS'][0]['Tags'] == 'Alternate' or songdescjson['COMPONENTS'][0]['Tags'] == 'ALTERNATE':
            AltMode=1
        elif songdescjson['COMPONENTS'][0]['Tags'] == 'extreme' or songdescjson['COMPONENTS'][0]['Tags'] == 'Extreme' or songdescjson['COMPONENTS'][0]['Tags'] == 'EXTREME':
            AltMode=1
        elif songdescjson['COMPONENTS'][0]['Tags'] == 'mashup' or songdescjson['COMPONENTS'][0]['Tags'] == 'Mashup' or songdescjson['COMPONENTS'][0]['Tags'] == 'MASHUP':
            AltMode=1
        else:
            AltMode=0

    else:
        LocaleID=songdescjson['COMPONENTS'][0]['LocaleID']
        TitleMode=1
        if songdescjson['COMPONENTS'][0]['Tags'] == 'alternate' or songdescjson['COMPONENTS'][0]['Tags'] == 'Alternate' or songdescjson['COMPONENTS'][0]['Tags'] == 'ALTERNATE':
            AltMode=1
        elif songdescjson['COMPONENTS'][0]['Tags'] == 'extreme' or songdescjson['COMPONENTS'][0]['Tags'] == 'Extreme' or songdescjson['COMPONENTS'][0]['Tags'] == 'EXTREME':
            AltMode=1
        elif songdescjson['COMPONENTS'][0]['Tags'] == 'mashup' or songdescjson['COMPONENTS'][0]['Tags'] == 'Mashup' or songdescjson['COMPONENTS'][0]['Tags'] == 'MASHUP':
            AltMode=1
        else:
            AltMode=0
        
    desc_enc=open(output, 'wb')
    desc_enc.write(b'\x00\x00\x00\x01\x00\x00\x02\xFC\x1B\x85\x7B\xCE\x00\x00\x00\x6C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x8A\xC2\xB5\xC6\x00\x00\x00\xF4')
    CodenameENC=Codename.encode('utf-8')
    CodenameLEN=len(Codename).to_bytes(4, 'big')
    desc_enc.write(CodenameLEN)
    desc_enc.write(CodenameENC)
    desc_enc.write(jdversion.to_bytes(4, 'big'))
    desc_enc.write(OriginalJDVersion.to_bytes(4, 'big'))

    try:
        relatedalbums=songdescjson['COMPONENTS'][0]['RelatedAlbums']
        for altmap in relatedalbums:
            desc_enc.write(b'\x00\x00\x00\x01')
            desc_enc.write(struct.pack('>i',len(altmap))+altmap.encode())
    except KeyError:
        desc_enc.write(b'\x00\x00\x00\x00')

    if AltMode==0 and TitleMode==1:
        desc_enc.write(b'\x00\x00\x00\x01\x00\x00\x00\x58\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x07')
    elif AltMode==1 and TitleMode==1:
        desc_enc.write(b'\x00\x00\x00\x01\x00\x00\x00\x58\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x07')
    elif AltMode==0 and TitleMode==0:
        desc_enc.write(b'\x00\x00\x00\x01\x00\x00\x00\x58\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x07')

    desc_enc.write(LocaleID.to_bytes(4, 'big'))

    if AltMode==0 and TitleMode==1:
        desc_enc.write(b'\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x01')
    elif AltMode==1 and TitleMode==1:
        desc_enc.write(b'\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x01')
    elif AltMode==0 and TitleMode==0:
        desc_enc.write(b'\x00\x00\x00\x03\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x01')

    desc_enc.write(struct.pack('>i',len(Artist))+Artist.encode())
    desc_enc.write(struct.pack('>i',len(DancerName))+DancerName.encode())
    desc_enc.write(struct.pack('>i',len(Title))+Title.encode())
    desc_enc.write(struct.pack('>I',NumCoach))
    desc_enc.write(b'\xFF\xFF\xFF\xFF')
    desc_enc.write(struct.pack('>I',Difficulty))
    desc_enc.write(struct.pack('>I',bgtype))
    desc_enc.write(struct.pack('>I',0))
    desc_enc.write(b'\x00\x00\x00\x01\x3F\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00\x10\x6F\x40\x37\xD0')
    desc_enc.write(preventry.to_bytes(4, 'big'))
    desc_enc.write(b'\x00\x00\x00\x00\x00\x00\x00\x10\xB1\x1F\xC1\xB6')
    desc_enc.write(prevloopstart.to_bytes(4, 'big'))
    desc_enc.write(prevloopend.to_bytes(4, 'big'))
    desc_enc.write(b'\x00\x00\x00\x06')
    desc_enc.write(b'\x24\xA8\x08\xD7') #songcolor_2a
    desc_enc.write(struct.pack('>f', songcolor_2a[3]))
    desc_enc.write(struct.pack('>f', songcolor_2a[2]))
    desc_enc.write(struct.pack('>f', songcolor_2a[1]))
    desc_enc.write(struct.pack('>f', songcolor_2a[0]))
    desc_enc.write(b'\x31\xD3\xB3\x47') #lyrics
    desc_enc.write(struct.pack('>f', lyriccolor3))
    desc_enc.write(struct.pack('>f', lyriccolor2))
    desc_enc.write(struct.pack('>f', lyriccolor1))
    desc_enc.write(struct.pack('>f', lyriccolor0))
    desc_enc.write(b'\x9C\xD9\x0B\xCB') #theme
    desc_enc.write(struct.pack('>f', theme[3]))
    desc_enc.write(struct.pack('>f', theme[2]))
    desc_enc.write(struct.pack('>f', theme[1]))
    desc_enc.write(struct.pack('>f', theme[0]))
    desc_enc.write(b'\xA2\x92\xC8\xC4') #songcolor_1a
    desc_enc.write(struct.pack('>f', songcolor_1a[3]))
    desc_enc.write(struct.pack('>f', songcolor_1a[2]))
    desc_enc.write(struct.pack('>f', songcolor_1a[1]))
    desc_enc.write(struct.pack('>f', songcolor_1a[0]))
    desc_enc.write(b'\xBE\x0B\x99\x23') #songcolor_2b
    desc_enc.write(struct.pack('>f', songcolor_2b[3]))
    desc_enc.write(struct.pack('>f', songcolor_2b[2]))
    desc_enc.write(struct.pack('>f', songcolor_2b[1]))
    desc_enc.write(struct.pack('>f', songcolor_2b[0]))
    desc_enc.write(b'\xF5\x82\x5C\x67') #songcolor_1b
    desc_enc.write(struct.pack('>f', songcolor_1b[3]))
    desc_enc.write(struct.pack('>f', songcolor_1b[2]))
    desc_enc.write(struct.pack('>f', songcolor_1b[1]))
    desc_enc.write(struct.pack('>f', songcolor_1b[0]))
    desc_enc.write(b'\x00\x00\x00\x00\x00\x00\x00\x00')
    desc_enc.close()

def menuartresizer(texture, path, outpath):
    picto=Image.open(path + texture)
    if ('_albumbkg') in texture:
        result=picto.resize((64,64))
    elif ('_albumcoach') in texture:
        result=picto.resize((256,256))
    else:
        result=picto.resize((256,256))
    result.save(outpath + texture.split(".")[0] + ".png")

def pictoresizer(texture, path, outpath):
    picto=Image.open(path + texture)
    result=picto.resize((128,128))
    result.save(outpath + texture.split(".")[0] + ".png")

def ambtpl(codename, pathReq):
      codenamelow=codename.lower()

      ambname='amb_'+codenamelow+'_intro'.lower()


      header=b'\x00\x00\x00\x01\x00\x00\x02\xB5\x1B\x85\x7B\xCE\x00\x00\x00\x6C\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\xD9\x4D\x6C\x53\x00\x00\x01\x18\x00\x00\x00\x01\x00\x00\x00\xF8\x28\xB8\x81\xEC\x00\x00\x00\x00\xEB\x53\x7A\x60\xFF\xFF\xFF\xFF\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01'
      path='world/maps/'+codenamelow+'/audio/amb/'
      ambwav=ambname+'.wav'
      ambtpl=ambname+'.tpl.ckd'

      amb=open(pathReq, "wb")

      #header

      amb.write(header)
      #making path

      amb.write(struct.pack(">I",len(ambwav))+ambwav.encode('utf-8')+struct.pack(">I",len(path))+path.encode('utf-8')+struct.pack("<I",zlib.crc32(ambwav.encode('utf-8'))))

      #ending
      amb.write(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x60\x00\x00\x00\x02\x00\x00\x00\x00\x00\x00\x00\x01\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x3F\x80\x00\x00\x3F\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x02\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xFF\xFF\xFF\xFF\x00\x00\x00\x00')

      amb.close()

def main():
    os.system('cls')
    print('''\nAutoMapTizeMii - Version Final - by sun\n''')


    
    for codename in os.listdir('input/'):
        os.makedirs('input/'+codename+'/menuart', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        os.makedirs('input/'+codename+'/temp/temp/ipkJDU', exist_ok=True)
        for ipk in os.listdir('input/'+codename):
            if ipk.endswith('.ipk'):
                os.makedirs('input/'+codename+'/temp/ipkJDU', exist_ok=True)
                os.system('bin\\quickbms.exe bin\\ipkJD.bms "input\\'+codename+'\\'+ipk+'" "input\\'+codename+'\\temp\\ipkJDU"')
            if ipk.endswith('.zip'):
                with zipfile.ZipFile('input/'+codename+'/'+ipk, 'r') as mainsceneipkinput:
                    os.makedirs('input/'+codename+'/zip', exist_ok=True)
                    os.makedirs('input/'+codename+'/temp/ipkJDU', exist_ok=True)
                    mainsceneipkinput.extractall('input/'+codename+'/zip')   
                    for files in os.listdir('input/'+codename+'/zip'):
                        if "main_scene" in files:
                            os.rename('input/'+codename+'/zip/'+files, 'input/'+codename+'/'+files)
                            os.system('bin\\quickbms.exe bin\\ipkJD.bms "input\\'+codename+'\\'+ipk.split('_')[0]+'_main_scene_nx.ipk" "input\\'+codename+'\\temp\\ipkJDU"')
                os.remove(f'input/{codename}/{ipk}')    
                shutil.rmtree('input/'+codename+'/zip')
                continue
            else:
                pass
            
        os.makedirs('output/temp/pictosDDS', exist_ok=True)
        os.makedirs('output/temp/pictosPNGCKD', exist_ok=True)
        os.makedirs('output/temp/pictosWII', exist_ok=True)
        os.makedirs('output/temp/pictosWIICKD', exist_ok=True)
        
        codenamelow = codename.lower()
        for pictoCKD in os.listdir('input/'+codename+'/temp/ipkJDU/cache/itf_cooked/nx/world/maps/'+codenamelow+'/timeline/pictos/'):
            shutil.copy('input/'+codename+'/temp/ipkJDU/cache/itf_cooked/nx/world/maps/'+codenamelow+'/timeline/pictos/'+pictoCKD, 'output/temp/pictosPNGCKD/')

        for pictosCKD in os.listdir('output/temp/pictosPNGCKD/'):
            textureExtractorNX(pictosCKD, 'output/temp/pictosPNGCKD/', 'output/temp/pictosDDS/')
        
        for pictosToConv in os.listdir('output/temp/pictosDDS/'):
            pictoresizer(pictosToConv, 'output/temp/pictosDDS/', 'output/temp/pictosWII/')

        for pictosWIItoCKD in os.listdir('output/temp/pictosWII/'):
            os.system('bin\\kuro.py -i output/temp/pictosWII/'+pictosWIItoCKD+' -o output/temp/pictosWIICKD/ -m -e png')
        
        mainscenemaker(codename)

        for pictos in os.listdir('output/temp/pictosWIICKD/'):
            shutil.move('output/temp/pictosWIICKD/'+pictos, 'output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/pictos/')
        os.rmdir('output/temp/pictosWIICKD')

        os.makedirs('output/temp/serializableObjects', exist_ok=True)
        shutil.copy('input/'+codename+'/temp/ipkJDU/cache/itf_cooked/nx/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_dance.dtape.ckd', 'output/temp/serializableObjects/')
        shutil.copy('input/'+codename+'/temp/ipkJDU/cache/itf_cooked/nx/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_karaoke.ktape.ckd', 'output/temp/serializableObjects/')
        shutil.copy('input/'+codename+'/temp/ipkJDU/cache/itf_cooked/nx/world/maps/'+codenamelow+'/audio/'+codenamelow+'_musictrack.tpl.ckd', 'output/temp/serializableObjects/')
        shutil.copy('input/'+codename+'/temp/ipkJDU/cache/itf_cooked/nx/world/maps/'+codenamelow+'/songdesc.tpl.ckd', 'output/temp/serializableObjects/')
        shutil.copy('input/'+codename+'/temp/ipkJDU/cache/itf_cooked/nx/world/maps/'+codenamelow+'/cinematics/'+codenamelow+'_mainsequence.tape.ckd', 'output/temp/serializableObjects/')

        #################################################################################################

        with open('output/temp/serializableObjects/songdesc.tpl.ckd', 'rb') as f:
            dataSongdesc=f.read()

        dataSongdesc=dataSongdesc.replace(b'\x00', b'')

        with open('output/temp/serializableObjects/songdesc_ready.tpl.ckd', 'wb') as readysd:
            readysd.write(dataSongdesc)

        #################################################################################################

        with open('output/temp/serializableObjects/'+codenamelow+'_mainsequence.tape.ckd', 'rb') as q:
            dataCine=q.read()

        dataCine=dataCine.replace(b'\x00', b'')

        with open('output/temp/serializableObjects/'+codenamelow+'_mainsequence_ready.tape.ckd', 'wb') as readycine:
            readycine.write(dataCine)

        #################################################################################################

        with open('output/temp/serializableObjects/'+codenamelow+'_musictrack.tpl.ckd', 'rb') as h:
            dataMusictrack=h.read()
        
        dataMusictrack=dataMusictrack.replace(b'\x00', b'')

        with open('output/temp/serializableObjects/'+codenamelow+'_musictrack_ready.tpl.ckd', 'wb') as readymt:
            readymt.write(dataMusictrack)

        #################################################################################################

        with open('output/temp/serializableObjects/'+codenamelow+'_tml_dance.dtape.ckd', 'rb') as j:
            dataDtape=j.read()
        
        dataDtape=dataDtape.replace(b'\x00', b'')

        with open('output/temp/serializableObjects/'+codenamelow+'_tml_dance_ready.dtape.ckd', 'wb') as readydtape:
            readydtape.write(dataDtape)

        #################################################################################################

        with open('output/temp/serializableObjects/'+codenamelow+'_tml_karaoke.ktape.ckd', 'rb') as k:
            dataKtape=k.read()
        
        dataKtape=dataKtape.replace(b'\x00', b'')

        with open('output/temp/serializableObjects/'+codenamelow+'_tml_karaoke_ready.ktape.ckd', 'wb') as readyktape:
            readyktape.write(dataKtape)

        #################################################################################################

        os.remove('output/temp/serializableObjects/'+codenamelow+'_musictrack.tpl.ckd')
        os.remove('output/temp/serializableObjects/songdesc.tpl.ckd')
        os.remove('output/temp/serializableObjects/'+codenamelow+'_tml_dance.dtape.ckd')
        os.remove('output/temp/serializableObjects/'+codenamelow+'_tml_karaoke.ktape.ckd')
        os.remove('output/temp/serializableObjects/'+codenamelow+'_mainsequence.tape.ckd')

        #################################################################################################

        os.rename('output/temp/serializableObjects/'+codenamelow+'_musictrack_ready.tpl.ckd', 'output/temp/serializableObjects/'+codenamelow+'_musictrack.tpl.ckd')
        os.rename('output/temp/serializableObjects/songdesc_ready.tpl.ckd', 'output/temp/serializableObjects/songdesc.tpl.ckd')
        os.rename('output/temp/serializableObjects/'+codenamelow+'_tml_dance_ready.dtape.ckd', 'output/temp/serializableObjects/'+codenamelow+'_tml_dance.dtape.ckd')
        os.rename('output/temp/serializableObjects/'+codenamelow+'_tml_karaoke_ready.ktape.ckd', 'output/temp/serializableObjects/'+codenamelow+'_tml_karaoke.ktape.ckd')
        os.rename('output/temp/serializableObjects/'+codenamelow+'_mainsequence_ready.tape.ckd', 'output/temp/serializableObjects/'+codenamelow+'_mainsequence.tape.ckd')

        # Hey moonlight here!
        # B.T.W. this serialization part was taken from JackLSummer15
        # And tape serialization for songdesc i remade it myself for alternates!
        # Thanks for listening!

        os.makedirs('output/temp/serializedObjects/', exist_ok=True)

        # Checking if we have Ambs:
            
        ktapeFile = open('output/temp/serializableObjects/'+codenamelow+'_tml_karaoke.ktape.ckd', 'r')
        ktapeJson = json.load(ktapeFile)

        try:
            Clips = ktapeJson['Clips']
        except KeyError:
            EmptyTapeEnabled = True
            ktapeFile.close()
            os.remove('output/temp/serializableObjects/'+codenamelow+'_tml_karaoke.ktape.ckd')

            with open('output/temp/serializableObjects/emptytape.ckd', 'w') as emptytape:
                emptytape.write('{"__class":"Tape","Clips":[],"TapeClock":0,"TapeBarCount":1,"FreeResourcesAfterPlay":0,"MapName":"'+codename+'"}')

            os.rename('output/temp/serializableObjects/emptytape.ckd', 'output/temp/serializableObjects/'+codenamelow+'_tml_karaoke.ktape.ckd')
            serializer(''+codenamelow+'_tml_karaoke.ktape.ckd','output/temp/serializedObjects/')
        ktapeFile.close()
        serializer(''+codenamelow+'_tml_karaoke.ktape.ckd','output/temp/serializedObjects/')
        serializer(''+codenamelow+'_tml_dance.dtape.ckd','output/temp/serializedObjects/')
        serializer(''+codenamelow+'_musictrack.tpl.ckd','output/temp/serializedObjects/')
        serialize_sd(jdVersion, 'output/temp/serializableObjects/songdesc.tpl.ckd', 'output/temp/serializableObjects/'+codenamelow+'_musictrack.tpl.ckd', 'output/temp/serializedObjects/songdesc.main_legacy.tpl.ckd')
        
        os.remove('output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/cache/legacyconverteddata/'+codenamelow+'/songdesc.main_legacy.tpl.ckd')
        os.remove('output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_dance.dtape.ckd')
        os.remove('output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_karaoke.ktape.ckd')
        os.remove('output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/cinematics/'+codenamelow+'_mainsequence.tape.ckd')
        os.rename('output/temp/serializedObjects/songdesc.main_legacy.tpl.ckd', 'output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/cache/legacyconverteddata/'+codenamelow+'/songdesc.main_legacy.tpl.ckd')
        os.rename('output/temp/serializedObjects/'+codenamelow+'_musictrack.main_legacy.tpl.ckd', 'output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/cache/legacyconverteddata/'+codenamelow+'/audio/'+codenamelow+'_musictrack.main_legacy.tpl.ckd')
        os.rename('output/temp/serializedObjects/'+codenamelow+'_tml_dance.dtape.ckd', 'output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_dance.dtape.ckd')
        os.rename('output/temp/serializedObjects/'+codenamelow+'_tml_karaoke.ktape.ckd', 'output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/timeline/'+codenamelow+'_tml_karaoke.ktape.ckd')
        
        for msm in os.listdir('input/'+codename+'/temp/ipkJDU/world/maps/'+codenamelow+'/timeline/moves/wiiu'):
            shutil.copy('input/'+codename+'/temp/ipkJDU/world/maps/'+codenamelow+'/timeline/moves/wiiu/'+msm, 'output/temp/'+codename+'_Wii_Mainscene/world/maps/'+codenamelow+'/timeline/moves/'+moveFolder+'/')

        #with open('output/temp/mainsequence_empty.tape.ckd', 'w') as feef:
            #feef.write('{"__class":"Tape","Clips":[],"TapeClock":0,"TapeBarCount":1,"FreeResourcesAfterPlay":0,"MapName":"'+codename+'","SoundwichEvent":""}')

        for ogg in os.listdir('input/'+codename+'/'):
            if ogg.endswith('.ogg'):
                ambcutter('input/'+codename+'/'+ogg, 'output/temp/serializableObjects/'+codenamelow+'_musictrack.tpl.ckd', codename)

        # System for detecting intro ambs was where i was serializing the cinematics so i can see if there are any and serialize them :D

        with open('output/temp/serializableObjects/'+codenamelow+'_musictrack.tpl.ckd', 'r') as musictrackFile:
                musictrackFileJson = json.load(musictrackFile)
                cineFile = open('output/temp/serializableObjects/'+codenamelow+'_mainsequence.tape.ckd', 'r')
                cineTape = json.load(cineFile)
                cineClipsCheck = []
                try:
                    for clip in cineTape['Clips']:
                        if clip['__class'] == 'SoundSetClip' and '_intro' in clip['SoundSetPath']:
                            IntroAmbCine = True
                            cineClipsCheck.append('SoundSetClip')
                        if clip['__class'] == 'HideUserInterfaceClip':
                            cineClipsCheck.append('HideUserInterfaceClip')
                        else:
                            IntroAmbCine = False
                            if 'HideUserInterfaceClip' in cineClipsCheck and IntroAmbCine == False:
                                TriggerETape = False
                            if 'HideUserInterfaceClip' in cineClipsCheck and IntroAmbCine == True:
                                TriggerETape = False
                            if 'HideUserInterfaceClip' not in cineClipsCheck and IntroAmbCine == False:
                                TriggerETape = True
                            if 'HideUserInterfaceClip' not in cineClipsCheck and IntroAmbCine == True:
                                TriggerETape = False    
                    if musictrackFileJson['COMPONENTS'][0]['trackData']['structure']['startBeat'] != 0 and IntroAmbCine: #False
                        IntroAmb = True
                    if musictrackFileJson['COMPONENTS'][0]['trackData']['structure']['startBeat'] == 0 and IntroAmbCine: #False
                        IntroAmb = False
                    else:
                        IntroAmb = False
                    cineFile.close()
                    #serialize_cinematics(''+codenamelow+'_mainsequence.tape.ckd','output/temp/serializedObjects/', IntroAmb)
                except KeyError:
                    TriggerETape = True
                
                if TriggerETape:
                    with open('output/temp/serializableObjects/emptytape.ckd', 'w') as emptytape:
                        emptytape.write('{"__class":"Tape","Clips":[],"TapeClock":0,"TapeBarCount":1,"FreeResourcesAfterPlay":0,"MapName":"'+codename+'"}')
                    IntroAmb = False
                    cineFile.close()
                    os.remove('output/temp/serializableObjects/'+codenamelow+'_mainsequence.tape.ckd')
                    os.rename('output/temp/serializableObjects/emptytape.ckd', 'output/temp/serializableObjects/'+codenamelow+'_mainsequence.tape.ckd')
                    print('Done!')
                    #serialize_cinematics(''+codenamelow+'_mainsequence.tape.ckd','output/temp/serializedObjects/', IntroAmb)

                serialize_cinematics(''+codenamelow+'_mainsequence.tape.ckd','output/temp/serializedObjects/', IntroAmb)

        with open('output/temp/serializableObjects/'+codenamelow+'_musictrack.tpl.ckd', 'r') as musictrackFile:
            musictrackFileJson = json.load(musictrackFile) 

        os.rename('output/temp/serializedObjects/'+codenamelow+'_mainsequence.tape.ckd', 'output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/cinematics/'+codenamelow+'_mainsequence.tape.ckd')
        
        if IntroAmb:
            os.makedirs('output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/audio/amb/', exist_ok=True)
            os.system('bin\\sora.py -i output/temp/amb_'+codenamelow+'_intro.ogg -o output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/audio/amb/amb_'+codenamelow+'_intro.wav.ckd -s')
            ambtpl(codename, 'output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/audio/amb/amb_'+codenamelow+'_intro.tpl.ckd')
        
        os.system('bin\\sora.py -i output/temp/'+codename+'.ogg -o output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/audio/'+codenamelow+'.wav.ckd')

        for webm in os.listdir('input/'+codename+''):
            if webm.endswith('.webm'):
                os.system('bin\\ffmpeg.exe -i "input/'+codename+'/'+webm+'" -hide_banner -loglevel error -threads:v 4 -sws_flags bicubic -codec:v libvpx  -r:v 25  -b:v 277k -bufsize 1000k -g 120 -rc_lookahead 16 -profile:v 1 -qmax 51 -qmin 11 -slices 4 -an -vol 0 -b:v 277k  -aspect 16:9 -b:v 277k -filter:v scale=512:384 output/temp/'+codename+'_Wii_Mainscene/world/maps/'+codenamelow+'/videoscoach/'+codenamelow+'.wii.webm')

        os.makedirs('output/temp/menuartDDS', exist_ok=True)

        for ddsckd in os.listdir('input/'+codename+'/menuart'):
            textureExtractorDDS(ddsckd.lower(), 'input/'+codename+'/menuart/', 'output/temp/menuartDDS/')

        os.makedirs('output/temp/menuartWII', exist_ok=True)

        for dds in os.listdir('output/temp/menuartDDS'):
            menuartresizer(dds.lower(), 'output/temp/menuartDDS/', 'output/temp/menuartWII/')

        os.makedirs('output/temp/TestWII', exist_ok=True)

        """shutil.move('output/temp/menuartWII/'+codenamelow+'_coach_1.png', 'output/temp/TestWII')

        try:
            shutil.move('output/temp/menuartWII/'+codenamelow+'_coach_2.png', 'output/temp/TestWII')
        except FileNotFoundError:
            pass

        try:
            shutil.move('output/temp/menuartWII/'+codenamelow+'_coach_3.png', 'output/temp/TestWII')
        except FileNotFoundError:
            pass

        try:
            shutil.move('output/temp/menuartWII/'+codenamelow+'_coach_4.png', 'output/temp/TestWII')
        except FileNotFoundError:
            pass

        shutil.move('output/temp/menuartWII/'+codenamelow+'_cover_generic.png', 'output/temp/TestWII')
        shutil.move('output/temp/menuartWII/'+codenamelow+'_cover_albumcoach.png', 'output/temp/TestWII')
        shutil.move('output/temp/menuartWII/'+codenamelow+'_cover_albumbkg.png', 'output/temp/TestWII')"""

        for menuart in os.listdir('output/temp/menuartWII/'):
            shutil.copy('output/temp/menuartWII//'+menuart.lower(), 'output/temp/TestWII')

        for Test2 in os.listdir('output/temp/TestWII'):
            os.makedirs('output/temp/menuWII', exist_ok=True)
            os.system('bin\\kuro.py -i output/temp/TestWII/'+Test2.lower()+' -o output/temp/menuWII -m -e tga')
            os.rename('output/temp/menuWII/'+Test2.lower().split('.')[0]+'.tga.ckd', 'output/temp/'+codename+'_Wii_Mainscene/cache/itf_cooked/wii/world/maps/'+codenamelow+'/menuart/textures/'+Test2.lower().split('.')[0]+'.tga.ckd')
        shutil.move('output/temp/'+codename+'_Wii_Mainscene', 'output/')
        shutil.rmtree('output/temp/')
        shutil.rmtree('input/'+codename+'/temp')
main()
