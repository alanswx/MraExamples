import sys
import re
import zipfile
import os

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
   zip1p = re.compile('set zip1=(.*)')
   zip2p = re.compile('set zip2=(.*)')
   ifilesp = re.compile('set ifiles=(.*)')
   md5p= re.compile('set md5valid=(.*)')
   ofilep= re.compile('set *ofile=(.*)')
   fullnamep= re.compile('set fullname=(.*)')
   while line:
       #print("Line {}: {}".format(cnt, line.strip()))
       ar1=zip1p.findall(line)
       zip1=''
       if (ar1):
           zip1=ar1[0]
           if (zip1):
               if (current_entry):
                romlist.append(current_entry)
               current_entry={}
               current_entry['zip1']=zip1.strip().replace('\\','/')
       ar1=zip2p.findall(line)
       if (ar1):
          current_entry['zip2']=ar1[0].strip().replace('\\','/')
       ar1=ifilesp.findall(line)
       if (ar1):

          current_entry['ifiles']=ar1[0].strip().replace('\\','/').split('+')
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

def process_roms(romlist):
    print(romlist[0]['ofile'].split('.'))
    rbfname=romlist[0]['ofile'].split('.')[1]
    rbfname=rbfname.capitalize()
    if (rbfname=="Dkong"):
        rbfname="DonkeyKong"
    elif (rbfname=="Alibbt"):
        rbfname="Alibaba"
    elif (rbfname=="Asteroid"):
        rbfname="Asteroids"
    elif (rbfname=="Astdelux"):
        rbfname="AsteroidsDeluxe"
    elif (rbfname=="Azurn"):
        rbfname="AzurianAttack"
    elif (rbfname=="Blckhl"):
        rbfname="BlackHole"
    elif (rbfname=="Bmbjck"):
        rbfname="BombJack"
    elif (rbfname=="Brubbr"):
        rbfname="BurningRubber"
    elif (rbfname=="Btime"):
        rbfname="BurgerTime"
    elif (rbfname=="Bwidow"):
        rbfname="BlackWidow"
    elif (rbfname=="Canyon"):
        rbfname="CanyonBomber"
    elif (rbfname=="Centiped"):
        rbfname="Centipede"
    elif (rbfname=="Cclimb"):
        rbfname="CrazyClimber"
    elif (rbfname=="Ckong"):
        rbfname="CrazyKong"
    elif (rbfname=="Crush"):
        rbfname="CrushRoller"
    elif (rbfname=="Csmvng"):
        rbfname="CosmicAvenger"
    elif (rbfname=="Ctcomb"):
        rbfname="Catacomb"
    elif (rbfname=="Dorodn"):
        rbfname="Dorodon"
    elif (rbfname=="Drmshp"):
        rbfname="DreamShopper"
    elif (rbfname=="Frggr"):
        rbfname="Frogger"
    elif (rbfname=="Galaxn"):
        rbfname="Galaxian"
    elif (rbfname=="Gorkns"):
        rbfname="Gorkans"
    elif (rbfname=="Ladybg"):
        rbfname="LadyBug"
    elif (rbfname=="Lizwiz"):
        rbfname="LizardWizard"
    elif (rbfname=="Llander"):
        rbfname="LunarLander"
    elif (rbfname=="Mspcmn"):
        rbfname="MsPacman"
    elif (rbfname=="Orbtrn"):
        rbfname="Orbitron"
    elif (rbfname=="Pacclb"):
        rbfname="PacmanClub"
    elif (rbfname=="Pacpls"):
        rbfname="PacmanPlus"
    elif (rbfname=="Phnx"):
        rbfname="Phoenix"
    elif (rbfname=="Ponpok"):
        rbfname="Ponpoko"
    elif (rbfname=="Scrmbl"):
        rbfname="Scramble"
    elif (rbfname=="Snpjck"):
        rbfname="SnapJack"
    elif (rbfname=="Sprglb"):
        rbfname="SuperGlob"
    elif (rbfname=="Sbrkout"):
        rbfname="SuperBreakout"
    elif (rbfname=="Tmplt"):
        rbfname="TimePilot"
    elif (rbfname=="Travrusa"):
        rbfname="TraverseUSA"
    elif (rbfname=="Vvcar"):
        rbfname="VanVanCar"
    elif (rbfname=="Warbug"):
        rbfname="WarOfTheBugs"
    elif (rbfname=="Wdpckr"):
        rbfname="Woodpecker"
    elif (rbfname=="Xevs"):
        rbfname="Xevious"
    count = 0
    for rom in romlist:
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
            zf1= zipfile.ZipFile(rom['zip1'], 'r')
            try:
              zf2= zipfile.ZipFile(rom['zip2'], 'r')
              mrazip2=lreplace('MAME/','',rom['zip2'])
            except KeyError:
              print ('ERROR: Did not find zip2')

            mrazip1=lreplace('MAME/','',rom['zip1'])

            fp.write('<misterromdescription>\n')
            fp.write('  <rbf>{}</rbf>\n'.format(rbfname))
            fp.write('  <rom index="0" zip="{}" md5="{}">\n'.format(mrazip1,rom['md5']))
            for part in rom['ifiles']:

               if part[0]=='"':
                   part=part.strip('"')
               if part[0]=='.' and part[1]=='.':
                   rfname=part.replace('../','')
                   print('GOT REAL FILE {}'.format(rfname))
                   with open(rfname,'rb') as rfp:
                       fp.write('      <part dt:dt="bin.hex">\n')
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
            fp.write('  </rom>')
            fp.write('  </misterromdescription>')
        print(rom)
        count=count+1


if __name__ == "__main__":
    for arg in sys.argv:
        if (arg!=sys.argv[0]):
            romlist=load_file(arg)
            process_roms(romlist)
