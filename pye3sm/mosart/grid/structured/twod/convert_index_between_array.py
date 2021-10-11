

def convert_index_between_array(nrow0, ncolumn0, index0, nrow1, ncolumn1, row_start, column_start):

    dummy_row_index = index0[0][0]
    dummy_column_index = index0[1][0]

    dummy_row_index1 = dummy_row_index - row_start
    dummy_column_index1 = dummy_column_index - column_start

    index1 = [ dummy_row_index1, dummy_column_index1 ]

    return  index1

