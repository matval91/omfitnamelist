#!/usr/bin/env python3

"""
Routine to read an omfit-like namelist and produce an AUG-like namelist

This must be done because in OMFIT too many variables are defined and the simulation gets weird

Note:
    Variables needed in the AUG-like namelist: shot, tinit, ftime, sedit, stedit, tgrid1, tgrid2, inputdir, dtbeam, dtmaxg
"""
import sys
import numpy as np

if len(sys.argv) == 3:
    omfit_fname = sys.argv[1]
    aug_fname = sys.argv[2]
else:
    print("Please give as input also the two names needed (name of omfit namelist and name of output namelist)")
    print('\n e.g. \n postproc_namelist.py 62124_omfitnamelist_wbeam.dat 62124_augnamelist.dat \n')
    exit()

def _readomfitnamelist(omfit_fname):
    """ read omfit namelist
    Private method to read the namelist produced by omfit
    
    Arguments:
        omfit_fname (str): name of file to read
    Params:
        outdict (dict): dictionary with needed values
    """
    aug_vars = ['nshot', 'tinit', 'ftime', 'sedit', 'stedit', 'tgrid1', 'tgrid2', 'INPUTDIR', 'dtbeam', 'dtmaxg']
    outdict = dict.fromkeys(aug_vars)
    omf_vars = ['NSHOT', 'TINIT', 'FTIME', 'SEDIT', 'STEDIT', 'TGRID1', 'TGRID2', 'INPUTDIR', 'DTBEAM', 'DTMAXG']
    with open(omfit_fname, 'r') as f:
        ll=f.readlines()
        
    for line in ll:
        line = line.split()
        if line[0]=='!': continue
        for ind, j in enumerate(omf_vars):
            if j not in line: continue
            outdict[aug_vars[ind]]=line[-1]

    for el in outdict:
        if el == 'INPUTDIR':
            outdict[el]='./'+outdict[el][1:-1]+'/'
        elif el == 'nshot' :
            outdict[el] = int(outdict[el])
        else:
            outdict[el] = float(outdict[el])

    return outdict

def _readlines(omfit_fname):
    """
    """
    lines=[]
    lines+=_readbeamnamelist(omfit_fname)
    lines+=_readacnamelist(omfit_fname)
    lines+=_readecnamelist(omfit_fname)
    return lines

def _readblocknamelist(omfit_fname, firstline, endline):
    """ read beam namelist
    Private method to read the BEAM namelist produced by omfit
    
    Arguments:
        omfit_fname (str): name of file to read
    Params:
        beam_lines (dict): dictionary with needed values
    Notes:

    """

    with open(omfit_fname, 'r') as f:
        ll=f.readlines()
    keylines=dict.fromkeys([firstline, endline])

    for indl,line in enumerate(ll):
        if line[0]=='!': continue
        for ind, j in enumerate(keylines):
            if j not in line: continue
            keylines[j] = int(indl)
  
    lines = ll[keylines[firstline]:keylines[endline]]
    return lines    

def _readbeamnamelist(omfit_fname):
    """ read beam namelist
    Private method to read the BEAM namelist produced by omfit
    
    Arguments:
        omfit_fname (str): name of file to read
    Params:
        beam_lines (dict): dictionary with needed values
    Notes:

    """
    beam_lines = _readblocknamelist(omfit_fname, '&NEUTRAL_BEAMS', '&FUSION_PRODUCTS')
    if 'False' in beam_lines[10]:
        beam_lines=[]
    if beam_lines!=[]:
        print("Beam read!")
    return beam_lines

def _readacnamelist(omfit_fname):
    """ read beam namelist
    Private method to read the BEAM namelist produced by omfit
    
    Arguments:
        omfit_fname (str): name of file to read
    Params:
        beam_lines (dict): dictionary with needed values
    Notes:

    """
    ac_lines = _readblocknamelist(omfit_fname, '&ACFILE', '&SHOT_NUMBER')
    if np.size(ac_lines)>3:
        print('AC File production read!')
    return ac_lines

def _readecnamelist(omfit_fname):
    """ read beam namelist
    Private method to read the BEAM namelist produced by omfit
    
    Arguments:
        omfit_fname (str): name of file to read
    Params:
        beam_lines (dict): dictionary with needed values
    Notes:

    """
    ec_lines = _readblocknamelist(omfit_fname, '&ELECTRON_CYCLOTRON_RESONANCE_HEATING_TORAY', '&ELECTRON_CYCLOTRON_RESONANCE_HEATING_GENRAY')
    if np.size(ec_lines)>3: 
        print('EC heating read!')
    return ec_lines

def _writeaugnamelist(aug_fname, outdict, lines):
    """ write aug namelist
    Private method to write the namelist in an aug-like format
    
    Arguments:
        out_fname (str): name of file to write
        outdict  (dict): dictionary with needed values
    Params:
        outfile (dict): printed file
    """
    keylines = ['nshot=$SHOT',
             'tinit=$TBEG',
             'ftime=$TEND',
             'sedit=$0.01',
             'stedit=$0.01',
             'tgrid1=$0.01',
             'tgrid2=$0.01',
             "INPUTDIR='$SHOT'",
             'dtbeam=$0.01'  ,
             'dtmaxg=$0.01']
    replacelines=['nshot='+str(outdict['nshot'])+'\n',
             'tinit='+str(outdict['tinit'])+'\n',
             'ftime='+str(outdict['ftime'])+'\n',
             'sedit='+str(outdict['sedit'])+'\n',
             'stedit='+str(outdict['stedit'])+'\n',
             'tgrid1='+str(outdict['tgrid1'])+'\n',
             'tgrid2='+str(outdict['tgrid2'])+'\n',
             "INPUTDIR='"+str(outdict['INPUTDIR'])+"'\n",
             'dtbeam='+str(outdict['dtbeam'])+'\n',
                  'dtmaxg='+str(outdict['dtmaxg'])+'\n'
    ]
    
    with open('/home/vallar/WORK/omfitnamelist/namelist_template.DAT', 'r') as f:
        ll=f.readlines()
    
    for indl,line in enumerate(ll):
        if line[0]=='!': continue
        for ind, j in enumerate(keylines):
            if j not in line: continue
            ll[indl] = replacelines[ind]

    with open(aug_fname, 'w') as fout:
        fout.writelines(ll)
        if lines!=[]:
            fout.writelines(lines)
    return ll

"""convert namelists
Uses the hidden methods to convert the namelist from omfit to the namelist aug-like.
You should have set all the correct parameters in OMFIT, then it will use those values

Arguments:
    omfit_fname (str): name of file to read
    aug_fname (str): name of file to write
Params:
    None
"""
d         = _readomfitnamelist(omfit_fname)
lines     = _readlines(omfit_fname)
outfile   = _writeaugnamelist(aug_fname,d, lines)
print("Conversion made between "+str(omfit_fname)+' and '+str(aug_fname))