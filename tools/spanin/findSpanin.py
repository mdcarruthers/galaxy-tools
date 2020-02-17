##### findSpanin.pl --> findSpanin.py
######### Incooperated from the findSpanin.pl script, but better and more snakey.

import argparse
from cpt import OrfFinder
from Bio import SeqIO
from Bio import Seq
#from lipory import find_lipoprotein
import os

### Requirement Inputs
#### INPUT : Genomic FASTA
#### PARAMETERS :
######## strand : +, -, both
######## start codons: ATG, GTG and TTG
######## isp_min: minimal length of the ORF, measured in AAs
######## isp_nterm_mindist: minimal distance to first AA of TMD, measured in AA
######## isp_nterm_maxdist: maximum distance to first AA of TMD, measured in AA
######## osp_min: minimal length of the ORF, measured in AAs
######## osp_signal_mindist: minimal distance to first AA of Lipobox, measured in AA
######## osp_signal_maxdist: maximum distance to first AA of Lipobox, measured in AA
######## Use LipoRy (?)
######## max_isp_osp_distance: maximum distance between the END of the isp, 
########                       and the beginning of the osp, measured in AA

###############################################################################
############:::::::::::::        PART I           :::::::::::::################
###############::::: Parse the FASTA for potential ORFs :::::::################
###############################################################################

###############################################################################
############:::::::::::::        PART II           :::::::::::::###############
###############:::::::        Find best candidate       :::::::################
###############################################################################

###############################################################################
############:::::::::::::        PART III           :::::::::::::##############
###############::::: Output FASTA files, and best candidate :::::::############
###############################################################################

#if __name__ == '__main__':
    #pass
###############################################################################

if __name__ == '__main__':

    # Common parameters for both ISP / OSP portion of script

    parser = argparse.ArgumentParser(description='Get putative protein candidates for spanins')

    parser.add_argument('fasta_file', type=argparse.FileType("r"), 
                        help='Fasta file') # the "input" argument

    #parser.add_argument('fasta_file_2', type=argparse.FileType("r"), 
    #                    help='Fasta file 2') # duplicate to make sure I understand this

    parser.add_argument('-f', '--format', dest='seq_format', default='fasta',
                        help='Sequence format (e.g. fasta, fastq, sff)') # optional formats for input, currently just going to do ntFASTA

    parser.add_argument('--strand', dest='strand', choices=('both', 'forward', 'reverse'), default='both', 
                        help='select strand') # Selection of +, -, or both strands

    parser.add_argument('--table', dest='table', default=1, 
                        help='NCBI Translation table',type=int) # Uses "default" NCBI codon table. This should always (afaik) be what we want...

    parser.add_argument('-t', '--ftype', dest='ftype', choices=('CDS', 'ORF'), default='ORF', 
                        help='Find ORF or CDSs') # "functional type(?)" --> Finds ORF or CDS, for this we want just the ORF

    parser.add_argument('-e', '--ends', dest='ends', choices=('open', 'closed'), default='closed',
                        help='Open or closed. Closed ensures start/stop codons are present') # includes the start and stop codon

    parser.add_argument('-m', '--mode', dest='mode', choices=('all', 'top', 'one'), default='all', # I think we want this to JUST be all...nearly always
                        help='Output all ORFs/CDSs from sequence, all ORFs/CDSs with max length, or first with maximum length')

    #parser.add_arugment('--max_isp_osp', dest='max_isp_osp', default=10, help='Maximum distance between the end of the i-spanin and start of the o-spanin. This is done after the putative list of proteins is built.', type=int)
    
    # isp parameters
    parser.add_argument('--isp_min_len', dest='isp_min_len', default=60, help='Minimum ORF length, measured in codons', type=int)
    parser.add_argument('--isp_on', dest='out_isp_nuc', type=argparse.FileType('w'), default='out_isp.fna', help='Output nucleotide sequences, FASTA')
    parser.add_argument('--isp_op', dest='out_isp_prot', type=argparse.FileType('w'), default='out_isp.fa', help='Output protein sequences, FASTA')
    parser.add_argument('--isp_ob', dest='out_isp_bed', type=argparse.FileType('w'), default='out_isp.bed', help='Output BED file')
    parser.add_argument('--isp_og', dest='out_isp_gff3', type=argparse.FileType('w'), default='out_isp.gff3', help='Output GFF3 file')

    # osp parameters
    parser.add_argument('--osp_min_len', dest='osp_min_len', default=30, help='Minimum ORF length, measured in codons', type=int)
    parser.add_argument('--osp_on', dest='out_osp_nuc', type=argparse.FileType('w'), default='out_osp.fna', help='Output nucleotide sequences, FASTA')
    parser.add_argument('--osp_op', dest='out_osp_prot', type=argparse.FileType('w'), default='out_osp.fa', help='Output protein sequences, FASTA')
    parser.add_argument('--osp_ob', dest='out_osp_bed', type=argparse.FileType('w'), default='out_osp.bed', help='Output BED file')
    parser.add_argument('--osp_og', dest='out_osp_gff3', type=argparse.FileType('w'), default='out_osp.gff3', help='Output GFF3 file')
    
    parser.add_argument('-v', action='version', version='0.3.0') # Is this manually updated?
    args = parser.parse_args()

    ### isp output, naive ORF finding:
    
    isps = OrfFinder(args.table, args.ftype, args.ends, args.isp_min_len, args.strand)
    isps.locate(args.fasta_file, args.out_isp_nuc, args.out_isp_prot, args.out_isp_bed, args.out_isp_gff3)

    ### osp output, naive ORF finding:
    osps = OrfFinder(args.table, args.ftype, args.ends, args.osp_min_len, args.strand)
    osps.locate(args.fasta_file, args.out_osp_nuc, args.out_osp_prot, args.out_osp_bed, args.out_osp_gff3)
    '''
    ### Putative isp output file
    ##### With the naive ORF finding's gff3 output, test to see if there is a TMD within the input parameters
    parser.add_argument('--isp_min_dist', dest='isp_min_dist', default=10, help='Minimal distance to first AA of TMD, measured in AA', type=int)
    parser.add_argument('--isp_max_dist', dest='isp_max_dist', default=30, help='Maximum distance to first AA of TMD, measured in AA', type=int)
    parser.add_argument('gff3_file', type=argparse.FileType("r"), help='Naive ORF Calls')
    parser.add_argument('fasta_genome', type=argparse.FileType("r"), help='Fasta genome sequence')

    ### Putative osp output file
    ##### With the naive ORF finding's gff3 output, test to see if there is a lipobox within the input parameters
    parser.add_argument('--osp_min_dist', dest='osp_min_dist', default=10, help='Minimal distance to first AA of TMD, measured in AA', type=int)
    parser.add_argument('--osp_max_dist', dest='osp_max_dist', default=30, help='Maximum distance to first AA of TMD, measured in AA', type=int)
    '''

######## strand : +, -, both
######## start codons: ATG, GTG and TTG
######## isp_min: minimal length of the ORF, measured in AAs
######## isp_nterm_mindist: minimal distance to first AA of TMD, measured in AA
######## isp_nterm_maxdist: maximum distance to first AA of TMD, measured in AA
######## osp_min: minimal length of the ORF, measured in AAs
######## osp_signal_mindist: minimal distance to first AA of Lipobox, measured in AA
######## osp_signal_maxdist: maximum distance to first AA of Lipobox, measured in AA
######## Use LipoRy (?)
######## max_isp_osp_distance: maximum distance between the END of the isp, 
########                       and the beginning of the osp, measured in AA








