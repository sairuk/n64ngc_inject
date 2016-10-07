#!/usr/bin/env python
#
# n64ngc_inject.py - @sairukau
# rom injector for n64 roms into 
#
import os, sys, argparse

### standard settings
CHUNK = 8
MAX_SIZE = 33554432
titlelocation = [0x20,0x49]
romlocation = [0x1C39FC0,0x2C39FC0]
checks = []
VER = "0.0.2"
APP = "n64ngc_inject.py %s - @sairukau" % VER

def chunkBin(infile, outfile):
    # chunk binary file into gcm
    with open(infile, "rb") as f:
        byte = f.read(CHUNK)
        while byte != "":
            outfile.write(byte)
            byte = f.read(CHUNK)
    return


def checkErrors(errlist):
    # if errlist evaluates to false we exit
    for b in errlist:
        if not b:
            checks = []
            exit()       
    return

def jmp(infile, isofile, b):
    # jump ahead in file
    infile.seek(b)
    isofile.seek(b)

def main(args):

    print "%s" % APP

    ### ARGS
    romfilename = args.romfile
    outpath = args.outpath
    gcmfile = args.gcmfile
       
       
    ### OUTPUT PATH
    #
    #
    if not os.path.exists(outpath):
        print " [OUTFILE] NOT FOUND: %s" % outpath
        checks.append(False)
    ### ROM FILE
    #
    # rom file exists
    if not os.path.exists(romfilename):
        print " [ROMFILE] NOT FOUND: %s" % romfilename
        checks.append(False)
    else:
        # get rom filesize
        romsize = os.stat(romfilename).st_size
        # clean up rom name for titles
        gamename = "%s" % os.path.splitext(os.path.basename(romfilename))[0]
        romlocation[1] = romsize + romlocation[0]
        # skip roms that are too big
        if romsize > MAX_SIZE:
            print "Game too big: %s at %s bytes" % ( gamename, romsize )
            checks.append(False)
    #       
    #### 


    ### GCM FILE
    #
    # gcm file exists
    if not os.path.exists(gcmfile):
        print " [GCMFILE] NOT FOUND: %s" % gcmfile
        checks.append(False)
    else:
        # setup output file name
        outfile = "%s.gcm" % os.path.join(outpath,gamename)
        # don't convert titles we already have
        if os.path.exists(outfile):
            print " [GCMFILE] EXISTS: %s" % gamename
            checks.append(False)
        else:
            print " [GCMFILE] NEW: %s" % gamename
    #
    ###

    # evaluate errors
    if len(checks):
        checkErrors(checks)

    # file to be patched
    isofile = open(outfile, "wb")

    print "Processing: %s" % gamename
    ### read gcmfile as binary
    with open(gcmfile, "rb") as infile:
        isobyte = infile.read(CHUNK)
        while isobyte != "":
            # write existing byte
            isofile.write(isobyte)
                       
            # write gamename
            if isofile.tell() == titlelocation[0]:
                print "  Writing title bytes into gcm at position %s" % hex(titlelocation[0])
                for char in gamename:
                    isofile.write(char)
                    
                # jump ahead in both files
                jmp(infile, isofile, titlelocation[1])

            # if we chunk over where we want to be, return
            if isofile.tell() > romlocation[0] and isofile.tell() < romlocation[1]:
                isofile.seek(romlocation[0])            
                
            # write romfile                
            if isofile.tell() == romlocation[0]:
                print "  Injecting rom file into gcm at position %s" % hex(romlocation[0])
                chunkBin(romfilename, isofile)
                
                # jump ahead in both files
                jmp(infile, isofile, romlocation[1])
                
            # continue reading gcmfile    
            isobyte = infile.read(CHUNK)
    return
    
if __name__ == "__main__":
    # PARSER
    parser = argparse.ArgumentParser(description='A Gamecube N64 rom injector for use with the EXPerience N64 Emulator 2.0')
    parser.add_argument('--romfile', nargs='?', help='ROM name to inject')
    parser.add_argument('--gcmfile', nargs='?', help='GCM to use as base')
    parser.add_argument('--outpath', nargs='?', help='Output path for patched GCM')  

    if len(sys.argv) != 7:
        parser.print_help()
    else:    
        # MAIN
        main(parser.parse_args())
    exit() 
