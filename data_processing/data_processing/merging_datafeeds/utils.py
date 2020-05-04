import csv


def getNewColumnNames(file):
    '''
    :param file: csv file where the new column for the feature are
    :return: list of the new column
    '''
    set_column_names = set()
    with open(file, encoding=enc) as f:
        csv_reader = csv.reader(f, delimiter=";")
        c = 0
        for row in csv_reader:
            if c > 0:
                set_column_names.add(row[2])
            c += 1
    set_column_names = list(set_column_names)
    return set_column_names