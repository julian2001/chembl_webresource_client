#!/usr/bin/env python
from __future__ import print_function


__author__ = 'mnowotka'

# ----------------------------------------------------------------------------------------------------------------------

import sys
import argparse
from chembl_webresource_client.scripts.utils import get_serializer, chembl_id_regex, smiles_regex, convert_to_smiles
from chembl_webresource_client.new_client import new_client

AVAILABLE_SOURCE_FORMATS = ('chembl_id', 'sdf', 'smi')

# ----------------------------------------------------------------------------------------------------------------------


def get_options():

    description = 'Perform similarity search, against ChEMBL DB using the official cartridge'
    parser = argparse.ArgumentParser(description=description, prog='chembl_sim')
    parser.add_argument('-i', '--input', action='store', dest='input',
                        help='input file, standard input by default')
    parser.add_argument('-o', '--output', action='store', dest='output',
                        help='output file, standard output by default')
    parser.add_argument('-t', '--threshold', action='store', dest='threshold', default='95',
                        help='similarity threshold a number from range [70-100], 95 is a default value')
    parser.add_argument('-s', '--source-format', action='store', dest='source_format', default='csv',
                        help='input file format. Can be one of 3: chembl_id (a comma separated list of chembl IDs), '
                             'sdf: (MDL molfile), smi (file containing smiles)')
    parser.add_argument('-d', '--destination-format', action='store', dest='dest_format', default='chembl_id',
                        help='output file format. can be chosen from 5 options: '
                             '[chembl_id, smi, sdf, inchi, inchi_key]')
    parser.add_argument('-H', '--Human', action='store_true', dest='human',
                        help='human readable output: prints header and first column with original names')
    return parser.parse_args()

# ----------------------------------------------------------------------------------------------------------------------


def main():
    similarity = new_client.similarity
    options = get_options()

    try:
        threshold = int(options.threshold)
        if threshold not in range(70, 101):
            sys.stderr.write('Threshold should be an integer in range [70-100]')
            return
        threshold = str(threshold)
    except:
        sys.stderr.write('Threshold should be an integer in range [70-100]')
        return

    source_format = options.source_format.lower()
    if source_format not in AVAILABLE_SOURCE_FORMATS:
        sys.stderr.write('Unsupported source format', options.source_format)
        return

    inp = sys.stdin
    if source_format == 'sdf':
        with open(options.input) if options.input else sys.stdin as in_f:
            options.input = None
            inp = convert_to_smiles(in_f)

    with open(options.input) if options.input else inp as in_f, \
            open(options.output, 'w') if options.output else sys.stdout as out_f:

        serializer_cls = get_serializer(options.dest_format)
        if not serializer_cls:
            sys.stderr.write('Unsupported format', options.dest_format)
            return

        if options.human:
            serializer_cls.write_header(out_f)

        for line in in_f:
            if not line or line.lower().startswith('smiles'):
                continue
            chunk = line.strip().split()[0]
            identifiers = chunk.strip().split(',')
            valid_identifiers = list()
            sim = list()
            for identifier in identifiers:
                if chembl_id_regex.match(identifier):
                    valid_identifiers.append(identifier)
                    sim.extend(list(similarity.filter(chembl_id=identifier, similarity=threshold)))
                elif smiles_regex.match(identifier):
                    valid_identifiers.append(identifier)
                    sim.extend(list(similarity.filter(smiles=identifier, similarity=threshold)))
            sim = list({v['molecule_chembl_id']: v for v in sim}.values())
            out_f.write(serializer_cls.serialize_line(sim, human=options.human, name=','.join(valid_identifiers)))

# ----------------------------------------------------------------------------------------------------------------------


if __name__ == "__main__":
    main()


# ----------------------------------------------------------------------------------------------------------------------
