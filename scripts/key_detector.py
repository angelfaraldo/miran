#!/usr/local/bin/python
#  -*- coding: UTF-8 -*-

"""
Ángel Faraldo, July 2017.

"""

from __future__ import absolute_import


if __name__ == "__main__":

    from time import clock
    from argparse import ArgumentParser

    from miran.base import *
    from miran.labels import *
    from miran.key.find import *

    clock()
    parser = ArgumentParser(description="Key estimation algorithm.")
    parser.add_argument("input", help="file or dir to analyse")
    parser.add_argument("output", help="file or dir to write results to")
    parser.add_argument("-a", "--algorithm", help="algorithm to use in the analysis", default="essentia_python")
    parser.add_argument("-p", "--profile", help="key profile; all other settings defaults apply.")
    parser.add_argument("-s", "--settings", help="json file with the key estimation settings")

    args = parser.parse_args()

    print("preparing the '{}' algorithm".format(args.algorithm))

    if args.settings:
        settings = load_settings_as_dict(args.settings)
        print("Using key estimation settings in {}".format(args.settings))
    else:
        settings = dekey_defs
        print("Using default key estimation settings")

    if args.profile:
        settings["KEY_PROFILE"] = args.profile
        print("Key profile:", settings["KEY_PROFILE"])

    if os.path.isfile(args.input):
        estimation, confidence = key_angel(args.input, args.output, **settings)
        print("\nAnalysing:\t{0}".format(args.input))
        print("Exporting to:\t{0}.".format(args.output))
        print(":\t{0} ({})".format(estimation, confidence))

    elif os.path.isdir(args.input):
        output_dir = create_dir(args.output)
        list_of_files = folderfiles(args.input)
        print("\nAnalysing audio filesystem in:\t{0}".format(args.input))
        print("Writing results to:\t{0}\n".format(args.output))
        count_files = 0
        for a_file in list_of_files:
            if any(soundfile_type in a_file for soundfile_type in AUDIO_FILE_EXT):
                output_file = os.path.join(args.output, os.path.splitext(os.path.split(a_file)[1])[0] + '.txt')
                estimation, confidence = eval(args.algorithm)(a_file, output_file)
                print("{} - {} ({})".format(a_file, estimation, confidence))
                count_files += 1

        print("{} audio filesystem analysed".format(count_files, clock()))

    else:
        raise NameError("Invalid input. Make sure it is a valid file or dir.")

    print("Finished in:\t{} secs.\n".format(clock()))
