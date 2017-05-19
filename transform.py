# -*- coding: utf-8 -*-

# imports
import petl
import sys

from utils import is_all_titlecased, is_all_caps, try_to_fix_case, fix_sentence_titlecasing, is_sentence_leading, is_valid, find_split_idx, fix_sentence_smushes, make_suggested_case_corrections, create_output_path

def row_mapper(row):
  row_id = str(row[0])
  # apply transformations from utils functions
  description = fix_sentence_smushes(
    make_suggested_case_corrections(
      fix_sentence_titlecasing(
        str(row[1]))))

  return [row_id, description]

def clean_file(input_path):
  '''clean the input .csv file'''
  # load csv file
  data = petl.fromcsv(input_path)
  # use petl's rowmap to clean each row
  petl.rowmap(data, row_mapper, ['id', 'description'], failonerror=True).tocsv(create_output_path(input_path))
  
clean_file(sys.argv[1])
