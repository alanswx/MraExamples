import sys
import re
import zipfile

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
   ofilep= re.compile('set ofile=(.*)')
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
    for rom in romlist:
        ofilename=rom['ofile'].replace('.rom','.mra')
        with open(ofilename,"w") as fp:
            zf1= zipfile.ZipFile(rom['zip1'], 'r')
            try:
              zf2= zipfile.ZipFile(rom['zip2'], 'r')
              mrazip2=lreplace('MAME/','',rom['zip2'])
            except KeyError:
              print 'ERROR: Did not find zip2'

            mrazip1=lreplace('MAME/','',rom['zip1'])

            fp.write('<misterromdescription>\n')
            fp.write('  <rbf>{}</rbf>\n'.format(rbfname))
            fp.write('  <rom index="0" zip="{}" md5="{}">\n'.format(mrazip1,rom['md5']))
            for part in rom['ifiles']:
               try:
                 info = zf1.getinfo(part)
               except KeyError:
                 print 'ERROR: Did not find %s in zip file' % part 
                 try:
                   info = zf2.getinfo(part)
                 except KeyError:
                   print 'ERROR: Did not find %s in zip file' % part 
                 else:
                   print '%s is %d bytes' % (info.filename, info.file_size)
                   fp.write('        <part zip="{}" name="{}"/>\n'.format(mrazip2,part))
               else:
                 print '%s is %d bytes' % (info.filename, info.file_size)
                 fp.write('        <part name="{}"/>\n'.format(part))
            fp.write('  </rom>')
            fp.write('  </misterromdescription>')
        print(rom)


if __name__ == "__main__":
    romlist=load_file(sys.argv[1])
    process_roms(romlist)
