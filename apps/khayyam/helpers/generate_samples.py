'''
Created on Nov 21, 2016

@author: dgrewal
'''

import os
from glob import glob
import warnings

class GenSamples(object):

    def __init__(self, input_file, input_type, samples, sample_id,
                 intervals=None, samplesheet=None):

        self.input = input_file
        self.type = input_type
        self.samples = samples
        self.sample_id = sample_id
        self.interval = intervals
        self.samplesheet = samplesheet

        self.test_inparams()

    def test_inparams(self):
        """
        intervals required if typ in part1, part2, qc
        samplesheet required if typ in part1, qc
        """
        if self.type in ["qc", "part1", "part2"]:
            assert self.interval is not None,\
                "intervals is required for the specified type"

        if self.type in ["qc", "part1"]:
            assert self.samplesheet is not None,\
                "samplesheet is required for the specified type"


    def parse_samplesheet(self):
        """
        parse the required data from a samplesheet
        """
        freader = open(self.samplesheet)

        header = True
        data = []

        for line in freader:
            line = line.strip().split(',')

            if header:
                if line[0] == "Experiment Name":
                    exptname = line[1]
                elif line[0] == "Description":
                    desc = line[1]
                elif line[0] == "[Data]":
                    header = False
            else:
                if line[0] in ['Sample_ID', 'Sample-ID']:
                    continue
                sampid = line[0]
                samp_plate = line[2]
                samp_well = line[3]
                samp_idx = line[5]
                samp_idx2 = line[7]
                samp_desc = line[9]

                data.append((sampid, samp_plate, samp_well,
                             samp_idx, samp_idx2, samp_desc))

        return exptname, desc, data

    def get_sequencing_type(self):
        """
        check if the input dir is from bcl2fastq pipeline (nextseq)
        or the GSC projects data format (Hiseq)
        """
        #remove trailing slash. basename returns '' if path ends with /
        indir = os.path.normpath(self.input)
        
        if os.path.basename(indir) == 'outputs':
            return 'nextseq'
        else:
            return 'hiseq'

    def write_data(self, data, outfile):
        """
        write data to outfile
        data must be str or list of strings
        """
        outfile = open(outfile, 'w')

        if isinstance(data, str):
            outfile.write(data)
        else:
            for dval in data:
                outfile.write(dval)

        outfile.close()

    def check_file_exists(self, path, isdir=False):
        """
        check if the path exists, throw warning if it doesn't
        also checks if path is a file or dir
        """
        if not os.path.exists(path):
            warnings.warn("Could not locate %s" %path)
            return False

        # check if the path is a file or not
        if not isdir:
            if not os.path.isfile(path):
                warnings.warn("%s is a directory, expected a file" %path)
                return False

        return True

    def is_empty(self, path):
        """
        check if the files are smaller than some specified size
        returns False if smaller and raise a warning
        """
        # assuming that the path exists
        filesize = os.path.getsize(path)

        if filesize == 0:
            warnings.warn("empty file %s" %path)
            return True

        return False

    def write_samples_file(self, value, key="samples"):
        """
        create samples file with the path to the interval file
        """
        samples = ["#sample_id", "\t", key, "\n",
                   self.sample_id, "\t", os.path.abspath(value)]
        samples = ''.join(samples)

        self.write_data(samples, self.samples)

    def find_fastq_files(self, seqtype, dataval, idx, exptname):
        """
        generates the file names based on the current dir structure
        and the sequencing type. The nextseq data sits in output dir of the
        bcl2fastq pipeline. Hiseq data shows up in projects and follows same
        filename pattern
        """
        (sampid, _, _, samp_idx, samp_idx2, _) = dataval

        if seqtype == 'nextseq':
            fq1 = '{0}_S{1}_R1_001.fastq.gz'.format(sampid, str(idx + 1))
            fq2 = '{0}_S{1}_R2_001.fastq.gz'.format(sampid, str(idx + 1))

            fq1 = os.path.join(self.input, "results", "fastqfiles", fq1)
            fq2 = os.path.join(self.input, "results", "fastqfiles", fq2)

        else:
            lib_id = os.path.normpath(self.input)
            lib_id = os.path.basename(lib_id)

            dirname = lib_id + '_' + samp_idx + '-' + samp_idx2
            basename = exptname + '_' + samp_idx + '-' + samp_idx2

            fq1 = os.path.join(self.input, exptname, dirname,
                               basename + "_1.fastq.gz")
            fq2 = os.path.join(self.input, exptname, dirname,
                               basename + "_2.fastq.gz")

        if not self.check_file_exists(fq1):
            fq1 = None

        if not self.check_file_exists(fq2):
            fq2 = None

        if fq1 and self.is_empty(fq1):
            fq1 = None

        if fq2 and self.is_empty(fq2):
            fq2 = None

        return fq1, fq2

    def find_part1_outputs(self, sampid):
        """
        find the bam file and samp info file from the part1 output dir
        """
        sampid = sampid.replace('-', '_')

        bam = 'TASK_PICARDTOOLS_SORT___*_' + sampid + '_bwa_aln.sorted.bam'
        info = 'TASK_FASTQ_TRIM___*_' + sampid + '_sample_info.txt'

        bam = os.path.join(self.input, 'results', 'realigned', bam)
        info = os.path.join(self.input, 'results', 'trimgalore', info)

        info = glob(info)
        bam = glob(bam)

        # we shouldn't have more than one file with each sampleid
        assert len(info) == 1, "found more than one info file for %s" % sampid
        assert len(bam) == 1, "found more than one bam file for %s" % sampid

        bam = bam[0]
        info = info[0]

        if not self.check_file_exists(bam):
            bam = None

        if not self.check_file_exists(info):
            info = None

        return bam, info

    def gen_bcl_fastq(self):
        """
        generate samples file for bcl2fastq pipeline
        """
        self.check_file_exists(self.input, isdir=True)

        self.write_samples_file(self.input, key='runfolder_dir')

    def gen_qc(self):
        """
        generates interval and samples file for qc and part1 of the single cell
        analysis pipeline

        get samples and ids from samplesheet, trackdown files and generate output
        """
        exptname, desc, data = self.parse_samplesheet()

        seqtype = self.get_sequencing_type()

        outdata = []
        for i, dataval in enumerate(data):

            fq1, fq2 = self.find_fastq_files(seqtype, dataval, i, exptname)

            # skip empty or missing files
            if not fq1 or not fq2:
                continue

            seqcentre = 'UBCBRC' if seqtype == 'nextseq' else "BCCAGSC"

            (sampid, samp_plate, samp_well, _, _, samp_desc) = dataval

            #pipeline expects dash, samplesheets use both _ and -
            samp_plate = samp_plate.replace('_', '-')
            outstr = ','.join([sampid, fq1, fq2, samp_well, samp_desc,
                               samp_plate, exptname, desc, 'illumina',
                               seqcentre])

            # dashes are not allowed in interval file chunk names
            outstr = '\t'.join([outstr, sampid.replace('-', '_')]) + '\n'

            outdata.append(outstr)

        if len(outdata) == 0:
            raise Exception("No Data found, all files are "
                            "either empty or missing")

        self.write_data(outdata, self.interval)

        # generate samples file
        self.write_samples_file(self.interval)

    def gen_part2(self):
        """
        generates interval and samples file for part2 of the single cell
        analysis pipeline
        get samples and ids from samplesheet, trackdown info and bam files
        """
        _, _, data = self.parse_samplesheet()

        outdata = []
        for sampid, _, _, _, _, _ in data:
            sampid = sampid.replace('-', '_')

            bam, sampinfo = self.find_part1_outputs(sampid)

            # skip empty or missing files
            if not bam or not sampinfo:
                continue

            outstr = bam + ',' + sampinfo + '\t' + sampid + '\n'
            outdata.append(outstr)

        if len(outdata) == 0:
            raise Exception("No Data found at the expected location")

        self.write_data(outdata, self.interval)

        # generate samples file
        self.write_samples_file(self.interval)

    def main(self):
        """
        call the functions based in type specified
        """
        if self.type == 'bcl2fastq':
            self.gen_bcl_fastq()
        elif self.type in ['qc', 'part1']:
            self.gen_qc()
        else:
            self.gen_part2()
