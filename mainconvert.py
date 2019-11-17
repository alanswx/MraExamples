import sys
import re
import zipfile
import os
import hashlib

def lreplace(pattern, sub, string):
    """
    Replaces 'pattern' in 'string' with 'sub' if 'pattern' starts 'string'.
    """
    return re.sub('^%s' % pattern, sub, string)

def load_file(filename):
  with open(filename) as fp:

   # create a list
   romlist=[]
   current_entry=None
   # do stuff with fp   
   line = fp.readline()
   cnt = 1
   zip1p = re.compile('zip=(.*)')
   zipsp = re.compile('zips=(.*)')
   zip2p = re.compile('zip2=(.*)')
   ifilesp = re.compile('ifiles=(.*)')
   md5p= re.compile('ofileMd5sumValid=(.*)')
   ofilep= re.compile('ofile=(.*)')
   fullnamep= re.compile('fullname=(.*)')
   while line:
       print("Line {}: {}".format(cnt, line.strip()))
       ar1=zip1p.findall(line)
       zip1=''
       if (ar1):
           zip1=ar1[0]
           if (zip1):
               if (current_entry):
                romlist.append(current_entry)
               current_entry={}
               current_entry['zip1']=zip1.strip().replace('\\','/')
       ar1=zipsp.findall(line)
       if (ar1):
           zip1=ar1[0]
           if (zip1):
               if (current_entry):
                romlist.append(current_entry)
               current_entry={}
               zips=zip1.strip('(').strip(')').split(' ')
               current_entry['zip1']=zips[0]
               current_entry['zip2']=zips[1]
       ar1=zip2p.findall(line)
       if (ar1):
          current_entry['zip2']=ar1[0].strip().replace('\\','/')
       ar1=ifilesp.findall(line)
       if (ar1):
           print(ar1[0])
           current_entry['ifiles']=ar1[0].strip().strip('(').strip(')').replace('\\','/').split(' ')
       ar1=md5p.findall(line)
       if (ar1):
          current_entry['md5']=ar1[0].strip()
       ar1=ofilep.findall(line)
       if (ar1):
          current_entry['ofile']=ar1[0].strip()
       ar1=fullnamep.findall(line)
       if (ar1):
          current_entry['fullname']=ar1[0].strip()
               

           
       cnt += 1
       line = fp.readline()
   if (current_entry):
      romlist.append(current_entry)


   return romlist


#
# given a non-merged part, file the merged one
#
def find_merged_file(zipfile,part,zipfilem,prefix):
    print('find_merged_file')
    print('prefix:'+prefix)
    try:
       data= zipfile.read(part)
       result = hashlib.md5(data)
       rr = result.digest()
       print("The byte equivalent of hash is : ", end ="")
       print('---')
       print(result.digest())
       print('---')
    except KeyError:
          print ('ERROR: Did not find %s in zip file' % part )

    # try reading the file from the normal filename
    rrm=""
    try:
       data= zipfilem.read(part)
       resultm = hashlib.md5(data)
       rrm = resultm.digest()
       print("The byte equivalent of hash is : ", end ="")
       print(result.digest())
    except KeyError:
          print ('ERROR: Did not find %s in zip file' % part )

    if (rr==rrm):
        print('matches normal file')
        return part



    try:
       data= zipfilem.read(prefix+'/'+part)
       resultm = hashlib.md5(data)
       rrm = result.digest()
       print("The byte equivalent of hash is : ", end ="")
       print(result.digest())
    except KeyError:
          print ('ERROR: Did not find %s in zip file' % part )

    if (rr==rrm):
        print('matches prefix')
        return prefix+'/'+part

    #
    #  HERE?
    #

    print('AJS HERE AJS HERE')
    for info in zipfilem.infolist():
        print(info)
        print(info.filename)
        data= zipfilem.read(info.filename)
        resultm = hashlib.md5(data)
        rrm = resultm.digest()
        if (rrm==rr):
           print('SUPERMATCH:'+info.filename)
           return info.filename

    return part

def create_rom_part(fp,mrazip1,mrazip2,zf1,zf2,rom,path,mergeprefix,origzf):
            fp.write('  <rom index="0" zip="{}" md5="{}">\n'.format(mrazip1,rom['md5']))
            for part in rom['ifiles']:
             if len(part):
               if part[0]=='"':
                   part=part.strip('"')
               if part[0]=='.' and part[1]=='.':
                   rfname=part.replace('../','')
                   print('GOT REAL FILE {}'.format(rfname))
                   rfname=path+'/releases/'+rfname
                   with open(rfname,'rb') as rfp:
                       fp.write('      <part>\n')
                       hexcount=1
                       byte = rfp.read(1)
                       while byte:
                        fp.write(byte.hex()+' ')
                        if (not (hexcount %16)):
                          fp.write('\n')
                        byte=rfp.read(1)
                        hexcount=hexcount+1
                       fp.write('      </part>\n')
               else:
                if mergeprefix:
                       part=find_merged_file(origzf,part,zf1,mergeprefix)
                try:
                 info = zf1.getinfo(part)
                except KeyError:
                 print ('ERROR: Did not find %s in zip file' % part )
                 try:
                   info = zf2.getinfo(part)
                 except KeyError:
                   print ('ERROR: Did not find %s in zip file ' % part )
                 else:
                   print ('%s is %d bytes' % (info.filename, info.file_size))
                   fp.write('        <part zip="{}" name="{}"/>\n'.format(mrazip2,part))
                else:
                 print ('%s is %d bytes' % (info.filename, info.file_size))
                 fp.write('        <part name="{}"/>\n'.format(part))
            fp.write('  </rom>\n')

def process_rom(path,filename,name):
    rom=load_file(filename)
    rom=rom[0]
    print(rom)
    rbfname=name
    count = 0
    if 1:
        ofilename=rom['ofile'].replace('.rom','.mra')
        if count==0:
            ofiledir='_newarcade/'
            os.makedirs(ofiledir,exist_ok=True)
            ofilename=ofiledir+rbfname+'.mra'
        else:
            ofiledir='_newarcade/_hacks/_'+rbfname+'/'
            os.makedirs(ofiledir,exist_ok=True)
            ofilename=ofiledir+ofilename

        with open(ofilename,"w") as fp:
            zipname="non-merged/"+rom['zip1']
            zipname="non-merged/"+rom['zip1']
            mergeprefx=''
            if (rom['zip1']=="rpatroln.zip"):
              zipnamem="merged/rpatrol.zip"
              mergeprefx='rpatroln'
            elif (rom['zip1']=="omegab.zip"):
              zipnamem="merged/theend.zip"
              mergeprefx='omegab'
            elif (rom['zip1']=="victorycb.zip"):
              zipnamem="merged/victoryc.zip"
              mergeprefx='victorycb'
            elif (rom['zip1']=="1943u.zip"):
              zipnamem="merged/1943.zip"
              mergeprefx='1943u'
            elif (rom['zip1']=="sprglbpg.zip"):
              zipnamem="merged/suprglob.zip"
              mergeprefx='sprglbpg'
            elif (rom['zip1']=="silvland.zip"):
              zipnamem="merged/rpatrol.zip"
              mergeprefx='silvland'
            elif (rom['zip1']=="mooncrgx.zip"):
              zipnamem="merged/mooncrst.zip"
              mergeprefx='mooncrgx'
            elif (rom['zip1']=="amidars.zip"):
              zipnamem="merged/amidar.zip"
              mergeprefx='amidars'
            elif (rom['zip1']=="froggers2.zip"):
              zipnamem="merged/frogger.zip"
              mergeprefx='frogger'
            elif (rom['zip1']=="galagamw.zip"):
              zipnamem="merged/galaga.zip"
              mergeprefx='galagamw'
            elif (rom['zip1']=="crush2.zip"):
              zipnamem="merged/crush.zip"
              mergeprefx='crush2'
            elif (rom['zip1']=="scrambles.zip"):
              zipnamem="merged/scramble.zip"
              mergeprefx='scramble'
            elif (rom['zip1']=="puckmanb.zip"):
              zipnamem="merged/puckman.zip"
              mergeprefx='puckman'
            elif (rom['zip1']=="gorkans.zip"):
              zipnamem="merged/mrtnt.zip"
              mergeprefx='gorkans'
            elif (rom['zip1']=="capitol.zip"):
              zipnamem="merged/pleiads.zip"
              mergeprefx='capitol'
            elif (rom['zip1']=="sprint2.zip"):
              zipnamem="merged/sprint1.zip"
              mergeprefx='sprint2'
            elif (rom['zip1']=="devilfsg.zip"):
              zipnamem="merged/devilfsh.zip"
              mergeprefx='devilfsg'
            else:
              zipnamem="merged/"+rom['zip1']
            zf1= zipfile.ZipFile(zipname, 'r')
            zf1m= zipfile.ZipFile(zipnamem, 'r')
            mrazip2=""
            zf2=None
            try:
              zipname="non-merged/"+rom['zip2']
              zf2= zipfile.ZipFile(zipname, 'r')
              mrazip2=lreplace('MAME/','',rom['zip2'])
            except KeyError:
              print ('ERROR: Did not find zip2')

            mrazip1=lreplace('MAME/','',rom['zip1'])

            fp.write('<misterromdescription>\n')
            fp.write('  <rbf>{}</rbf>\n'.format(rbfname))


            #
            #  Let's create the non-merged section
            #
            
            create_rom_part(fp,mrazip1,mrazip2,zf1,zf2,rom,path,None,None)

            if (len(mergeprefx)):
                newzipname=zipnamem.split('/')[1]
                if (rbfname!='Galaga'):
                  create_rom_part(fp,newzipname,"",zf1m,None,rom,path,mergeprefx,zf1)
            #    #       result=find_merged_file(zf1,part,zf1m,mergeprefx)
            #    #       print('new filename:'+result)

            #
            #  check on creating a merged rom
            #



            fp.write('</misterromdescription>')
        print(rom)
        count=count+1


if __name__ == "__main__":
    for file in os.listdir("."):
        if file.startswith("Arcade-"):
            p1=file.split('-')
            p2=p1[1].split('_')
            print(file)
            print(p2[0])
            filename=file+'/releases/build_rom.ini'
            if os.path.exists(filename) and p2[0]!='RallyX':
               process_rom(file,file+'/releases/build_rom.ini',p2[0])
            else:
               print(file+' no rom')

    #for arg in sys.argv:
    #    if (arg!=sys.argv[0]):
    #        romlist=load_file(arg)
    #        process_roms(romlist)
