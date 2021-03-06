#  -*- coding: UTF-8 -*-


def key_eval_mirex(estimated_key_tuple, reference_key_tuple):
    """
    Performs an evaluation of the key estimation
    according to the MIREX protocol, assigning:

    - 1.0 point to correctly identified keys,
    - 0.5 points to keys at a neighbouring keys
    - 0.3 points to relative keys,
    - 0.2 points to parallel keys, and
    - 0.0 points to other types of errors.

    :param estimated_key_tuple: tuple with values for estimated key and mode (tonic, mode) :type tuple
    :param reference_key_tuple: tuple with values for reference key and mode (tonic, mode) :type tuple
    """

    # removes additional modal information if existing
    estimated_key_tuple = estimated_key_tuple[:2]
    reference_key_tuple = reference_key_tuple[:2]

    # directly score 0 for unknown files!
    if -2 in estimated_key_tuple or -2 in reference_key_tuple:
        return 0

    # return to the main process without performing an evaluation!
    if -3 in estimated_key_tuple or -3 in reference_key_tuple:
        return

    estimated_tonic, estimated_mode = estimated_key_tuple
    reference_tonic, reference_mode = reference_key_tuple

    # perfect match
    if estimated_tonic == reference_tonic and estimated_mode == reference_mode:
        score = 1.

    # neighbouring keys (circle of fifths with the same mode)
    elif estimated_tonic == (reference_tonic + 7) % 12 and estimated_mode == reference_mode:
            score = 0.5
    elif estimated_tonic == (reference_tonic + 5) % 12 and estimated_mode == reference_mode:
            score = 0.5

    # relative error (0.3)
    elif estimated_tonic == (reference_tonic + 3) % 12 and estimated_mode == 0 and reference_mode == 1:
        score = 0.3
    elif estimated_tonic == (reference_tonic - 3) % 12 and estimated_mode == 1 and reference_mode == 0:
        score = 0.3

    # parallel error (0.2)
    elif estimated_tonic == reference_tonic and estimated_mode != reference_mode:
        score = 0.2

    else:
        score = 0.0

    return score


def key_eval_relative_errors(estimated_key_tuple, reference_key_tuple):
    """
    Performs a detailed evaluation of the key each_file.
    :type estimated_key_tuple: tuple with numeric values for key and mode
    :type reference_key_tuple: tuple with numeric values for key and mode

    """
    PC2DEGREE = {0: 'I', 1: 'bII', 2: 'II', 3: 'bIII', 4: 'III', 5: 'IV',
                 6: '#IV', 7: 'V', 8: 'bVI', 9: 'VI', 10: 'bVII', 11: 'VII',}

    # removes additional modal information if existing
    estimated_key_tuple = estimated_key_tuple[:2]
    reference_key_tuple = reference_key_tuple[:2]

    # directly score 0 for unknown files!
    if -2 in estimated_key_tuple or -2 in reference_key_tuple:
        return 0, 'UNKNOWN'

    # return to the main process without performing an evaluation!
    if -3 in estimated_key_tuple or -3 in reference_key_tuple:
        return None, 'EXCLUDED'

    estimated_tonic, estimated_mode = estimated_key_tuple
    reference_tonic, reference_mode  = reference_key_tuple

    if estimated_key_tuple == [-1, None]:
        if reference_mode == 0:
            return (37 * 4) - 4, 'I as X'
        elif reference_mode == 1:
            return (37 * 4) - 3, 'i as X'
        elif reference_mode == 2:
            return (37 * 4) - 2, '1? as X'
        elif reference_mode is None:
            return (37 * 4) - 1, 'X as X'

    elif reference_key_tuple == [-1, None]:
        if estimated_mode == 0:
            return 3, 'X as I'
        elif estimated_mode == 1:
            return (12 * 4) + 2, 'X as i'
        elif estimated_mode == 2:
            return (24 * 4) + 3, 'X as 1?'

    else:
        interval = (estimated_tonic - reference_tonic) % 12
        degree = PC2DEGREE[interval]
        error_id = 4 * (interval + (estimated_mode * 12)) + reference_mode
        if estimated_mode == 1:
            degree = degree.lower()
        else:
            degree = degree.upper()
            degree = degree.replace('B', 'b')
        if reference_mode == 1:
            degree = 'i as ' + degree
        else:
            degree = 'I as ' + degree
        return error_id, degree


def key_tonic_mode(estimated_key_tuple, reference_key_tuple):
    """
    Performs a baseline evaluation of tonic note and mode.

    :param estimated_key_tuple: tuple with values for estimated key and mode (tonic, mode) :type tuple
    :param reference_key_tuple: tuple with values for reference key and mode (tonic, mode) :type tuple
    """

    import numpy as np

    # removes additional modal information if existing
    estimated_key_tuple = estimated_key_tuple[:2]
    reference_key_tuple = reference_key_tuple[:2]

    # directly score 0 for unknown files!
    if -2 in estimated_key_tuple or -2 in reference_key_tuple:
        return 0

    # return to the main process without performing an evaluation!
    if -3 in estimated_key_tuple or -3 in reference_key_tuple:
        return

    estimated_tonic, estimated_mode = estimated_key_tuple
    reference_tonic, reference_mode = reference_key_tuple


    result = np.array([estimated_tonic == reference_tonic, estimated_mode == reference_mode])

    return result.astype(int)
