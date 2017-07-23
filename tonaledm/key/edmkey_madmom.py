#!/usr/local/bin/python
#  -*- coding: UTF-8 -*-

import sys

import madmom

from pcp import *
from templates import *
from tonaledm.filesystem import create_dir

# ======== #
# SETTINGS #
# ======== #

# File Settings
# -------------
SAMPLE_RATE                  = 44100
VALID_FILE_TYPES             = {'.wav', '.mp3', 'flac', '.aiff', '.ogg'}

# Analysis Parameters
# -------------------
DETUNING_CORRECTION          = False
PCP_THRESHOLD                = None
WINDOW_SIZE                  = 4096
HOP_SIZE                     = 4096
WINDOW_SHAPE                 = 'hann'
MIN_HZ                       = 27.5 # A-1
MAX_HZ                       = 3500 # 7 octavas
HPCP_SIZE                    = 12
HPCP_REFERENCE_HZ            = 440
HPCP_WEIGHT_WINDOW_SEMITONES = 1  # semitones
HPCP_WEIGHT_TYPE             = 'cosine'  # {'none', 'cosine', 'squaredCosine'}
HPCP_NORMALIZE               = False

# Scope and Key Detector Method
# -----------------------------
DURATION                     = None  # analyse first n seconds of each track (None = full track)
OFFSET                       = 0
ANALYSIS_TYPE                = 'global'  # {'local', 'global'}
N_WINDOWS                    = 100  # if ANALYSIS_TYPE is 'local'
WINDOW_INCREMENT             = 100  # if ANALYSIS_TYPE is 'local'
KEY_PROFILE                  = 'krumhansl'
USE_THREE_PROFILES           = False
WITH_MODAL_DETAILS           = False


# ======================== #
# KEY ESTIMATION ALGORITHM #
# ======================== #

def get_key(input_audio_file, output_text_file):
    """
    This function estimates the overall key of an audio track
    optionaly with extra modal information.
    :type input_audio_file: str
    :type output_text_file: str
    """
    #audio = madmom.audio.signal.Signal(input_audio_file, sample_rate=SAMPLE_RATE, num_channels=1)
    #fs = madmom.audio.signal.FramedSignal(audio, frame_size=WINDOW_SIZE, hop_size=HOP_SIZE)

    #class madmom.audio.chroma.PitchClassProfile(spectrogram,
    #filterbank=<class 'madmom.audio.filters.PitchClassProfileFilterbank'>,
    #num_classes=12, fmin=100.0, fmax=5000.0, fref=440.0, **kwargs)

    chroma = madmom.audio.chroma.CLPChroma(input_audio_file,
                                           fps=SAMPLE_RATE / HOP_SIZE,
                                           fmin=MIN_HZ,
                                           fmax=MAX_HZ,
                                           norm=HPCP_NORMALIZE,
                                           threshold=PCP_THRESHOLD)

    chroma = np.sum(chroma, axis=0)

    if PCP_THRESHOLD is not None:
        chroma = normalize_pcp_peak(chroma)
        chroma = pcp_gate(chroma, PCP_THRESHOLD)

    if DETUNING_CORRECTION:
        chroma = shift_pcp(chroma, HPCP_SIZE)

    if USE_THREE_PROFILES:
        estimation_1 = template_matching_3(chroma, KEY_PROFILE)
    else:
        estimation_1 = template_matching_2(chroma, KEY_PROFILE)

    key_1 = estimation_1[0] + '\t' + estimation_1[1]

    if WITH_MODAL_DETAILS:
        estimation_2 = template_matching_3(chroma)
        key_2 = estimation_2[0] + '\t' + estimation_2[1]
        key_verbose = key_1 + '\t' + key_2
        key = key_verbose.split('\t')

        if key[3] == 'monotonic' and key[0] == key[2]:
            key = '{0}\tminor'.format(key[0])
        else:
            key = key_1

    else:
        key = key_1

    textfile = open(output_text_file, 'w')
    textfile.write(key + '\n')
    textfile.close()

    return key


if __name__ == "__main__":

        from time import clock
        from argparse import ArgumentParser

        clock()
        parser = ArgumentParser(description="Key Estimation Algorithm")
        parser.add_argument("input", help="file (dir if in --batch_mode) to analyse")
        parser.add_argument("output", help="file (dir if in --batch_mode) to write results to")
        parser.add_argument("-b", "--batch_mode", action="store_true", help="batch analyse a whole directory")
        parser.add_argument("-v", "--verbose", action="store_true", help="print progress to console")
        parser.add_argument("-x", "--extra", action="store_true", help="generate extra analysis filesystem")
        parser.add_argument("-c", "--conf_file", help="specify a different configuration file")
        args = parser.parse_args()

        if not args.batch_mode:
            if not os.path.isfile(args.input):
                print("\nWARNING:")
                print("Could not find {0}".format(args.input))
                print("Are you sure is it a valid filename?\n")
                sys.exit()
            elif os.path.isfile(args.input):
                print("\nAnalysing:\t{0}".format(args.input))
                print("Exporting to:\t{0}.".format(args.output))
                estimation = get_key(args.input, args.output)
                if args.verbose:
                    print(":\t{0}".format(estimation)),
            else:
                raise IOError("Unknown ERROR in single file mode")
        else:
            if os.path.isdir(args.input):
                analysis_folder = args.input[1 + args.input.rfind('/'):]
                if os.path.isfile(args.output):
                    print("\nWARNING:")
                    print("It seems that you are trying to replace an existing file")
                    print("In batch_mode, the output argument must be a directory".format(args.output))
                    print("Type 'fkey -h' for help\n")
                    sys.exit()
                output_dir = create_dir(args.output)
                list_all_files = os.listdir(args.input)
                print("\nAnalysing audio filesystem in:\t{0}".format(args.input))
                print("Writing results to:\t{0}\n".format(args.output))
                count_files = 0
                for a_file in list_all_files:
                    if any(soundfile_type in a_file for soundfile_type in VALID_FILE_TYPES):
                        input_file = args.input + '/' + a_file
                        output_file = args.output + '/' + a_file[:-4] + '.txt'
                        estimation = get_key(input_file, output_file)
                        if args.verbose:
                            print("{0} - {1}".format(input_file, estimation))
                        count_files += 1
                print("{0} audio filesystem analysed".format(count_files, clock()))
            else:
                raise IOError("Unknown ERROR in batch mode")
        print("Finished in:\t{0} secs.\n".format(clock()))
