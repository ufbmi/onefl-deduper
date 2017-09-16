#!/usr/bin/env python
"""
Goal: extract rows from `file_large` with values of the `join_column`
which do not exist in `file_small`.

This script is equivalent to running the mlr command:
$mlr --tsv join -j join_column --ul --np -f large.csv small.csv > extra.csv

mlr command explanation:
    --np         Do not emit paired records
    --ul         Emit unpaired records from the left file

$ cat a.csv
col1,col2
a,1
b,2
c,3
d,4

$ cat b.csv
col1,col3
b,200
a,100
x,999

$ ./find_extra_rows.py -a a.csv  -b b.csv -c col1 -s ,

Wrote the 2 extra rows to: extra_a.csv
col1    col2
c       3
d       4

"""
import pandas as pd
import argparse


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--file_a', required=True,
                        help='the large file'
                        )
    parser.add_argument('-b', '--file_b', required=True,
                        help='the small file'
                        )
    parser.add_argument('-c', '--join_column', required=True,
                        help='the name of the column used for the join'
                        )
    parser.add_argument('-s', '--separator', required=False, default='\t',
                        help='record separator'
                        )

    args = parser.parse_args()
    file_large = args.file_a
    file_small = args.file_b
    join_column = args.join_column.strip()
    separator = args.separator.strip(' ')
    output_file = 'extra_{}'.format(args.file_a)

    print("Reading file: {}".format(file_large))
    df_a = pd.read_csv(file_large, dtype=object, sep=separator)
    # df_a.fillna('', inplace=True)
    print("Found {} rows".format(len(df_a)))
    print(df_a.head())

    print("Reading file: {}".format(file_small))
    df_b = pd.read_csv(file_small, dtype=object, sep=separator)
    print("Found {} rows".format(len(df_b)))

    print("Checking common lines in {} and {}".format(file_large, file_small))
    df_common = pd.merge(df_a, df_b, on=join_column,
                         how='inner', sort=True)
    print("Found {} common rows.".format(len(df_common)))

    df_extra = df_a[~df_a[join_column].isin(df_common[join_column])]
    print("Found {} extra rows in file: {}".format(len(df_extra), file_large))

    df_extra.to_csv(output_file, index=False, sep='\t')
    print("Wrote the {} extra rows to: {}".format(len(df_extra), output_file))
    print(df_extra.head().to_csv(sep='\t', index=False))


if __name__ == '__main__':
    main()
