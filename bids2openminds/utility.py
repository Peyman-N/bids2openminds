import hashlib
import json
import os
import re
import gzip
from warnings import warn
import pandas as pd

import openminds.latest.controlled_terms as controlled_terms
from openminds.latest.core import Hash, QuantitativeValue, ContentType
from openminds.latest.controlled_terms import UnitOfMeasurement

from . import mapping


def read_json(file_path: str) -> dict:
    """
    Reads the content of a JSON file and returns it as a Python dictionary.

    Parameters:
    - file_path (str): The path to the JSON file.

    Returns:
    - dict: A Python dictionary containing the content of the JSON file.

    Example:
    >>> data = read_json('example.json')
    >>> print(data)
    {"Name": "The mother of all experiments" , "BIDSVersion": "1.6.0", "DatasetType": "raw" , "License": "CC0" , "Authors": ["Paul Broca" , "Carl Wernicke" ]}
    """
    try:
        # Open the JSON file
        with open(file_path, "r") as file:
            # Load the JSON content into a dictionary
            json_dic = json.load(file)
        return json_dic
    except FileNotFoundError:
        # Handle file not found error
        print(f"Error: File not found at {file_path}")
        return {}
    except json.JSONDecodeError:
        # Handle JSON decoding error
        print(f"Error: Unable to decode JSON content from {file_path}")
        return {}


def table_filter(dataframe: pd.DataFrame, filter_str: str, column: str = "suffix"):
    """
    Filters a Pandas DataFrame based on a specified condition.

    Parameters:
    - dataframe (pd.DataFrame): The DataFrame to be filtered.
    - filter_str (str): The value to filter the DataFrame on.
    - column (str, optional): The column name to apply the filter on. Default is "suffix".

    Returns:
    - pd.DataFrame: A filtered DataFrame containing only the rows that satisfy the condition.
    """
    try:
        # Apply the filter condition on the specified column
        filtered_dataframe = dataframe[dataframe[column] == filter_str]
        return filtered_dataframe
    except KeyError:
        # Handle the case where the specified column is not present in the DataFrame
        KeyError(f"Error: Column '{column}' not found in the DataFrame.")


def pd_table_value(data_frame, column_name, not_list: bool = True):
    try:
        if column_name in data_frame.columns:
            value = data_frame[column_name].to_list()
            if not_list:
                return value[0]
            else:
                return value
        else:
            return None
    except IndexError:
        warn(f"The data frame doesn't contain {column_name}")
        return None


def file_hash(file_path: str, algorithm: str = "MD5"):
    """
    Compute the hash digest of a file using the specified hashing algorithm an returns an openMINDs object.

    Parameters:
    - file_path (str): The path to the file for which you want to compute the hash.
    - algorithm (str, optional): The hashing algorithm to use. Default is "MD5".

    Returns:
    - Hash: An openMINDS object representing the computed hash, containing the algorithm and digest.
    """
    # Open the file in binary mode
    with open(file_path, "rb") as file:
        # Read the content of the file
        file_content = file.read()

        # Create a new hash object using the specified algorithm
        hash_object = hashlib.new(algorithm)

        # Update the hash object with the content of the file
        hash_object.update(file_content)

        # Calculate the hexadecimal digest of the hash
        hash_value = hash_object.hexdigest()

    # Create a openMINDS Hash object with the algorithm and digest
    openminds_hash = Hash(algorithm=algorithm, digest=hash_value)

    return openminds_hash


def file_storage_size(file_path: str):
    file_stats = os.stat(file_path)
    file_size = QuantitativeValue(
        value=file_stats.st_size, unit=UnitOfMeasurement.by_name("byte"))
    return file_size, file_stats.st_size


def detect_nifti_version(file_name, extension, file_size):

    nii1_sizeof_hdr = 348
    nii2_sizeof_hdr = 540

    if extension == ".nii":

        with open(file_name, 'rb') as fp:
            byte_data = fp.read(4)

        sizeof_hdr = int.from_bytes(byte_data, byteorder='little')

        if sizeof_hdr == 0:
            return None

        if sizeof_hdr == nii1_sizeof_hdr:
            return ContentType.by_name("application/vnd.nifti.1")

        elif sizeof_hdr == nii2_sizeof_hdr:
            return ContentType.by_name("application/vnd.nifti.2")

        else:  # big endian
            sizeof_hdr = int.from_bytes(byte_data, byteorder='big')

            if sizeof_hdr == nii1_sizeof_hdr:
                return ContentType.by_name("application/vnd.nifti.1")

            elif sizeof_hdr == nii2_sizeof_hdr:
                return ContentType.by_name("application/vnd.nifti.2")

    if extension == ".nii.gz":
        try:
            with gzip.open(file_name, 'rb') as fp:
                byte_data = fp.read(4)
        except gzip.BadGzipFile:
            return None

        sizeof_hdr = int.from_bytes(byte_data, byteorder='little')

        if sizeof_hdr == 0:
            return None

        if sizeof_hdr == nii1_sizeof_hdr:
            return ContentType.by_name("application/vnd.nifti.1")

        elif sizeof_hdr == nii2_sizeof_hdr:
            return ContentType.by_name("application/vnd.nifti.2")

        else:  # big endian
            sizeof_hdr = int.from_bytes(byte_data, byteorder='big')

            if sizeof_hdr == nii1_sizeof_hdr:
                return ContentType.by_name("application/vnd.nifti.1")

            elif sizeof_hdr == nii2_sizeof_hdr:
                return ContentType.by_name("application/vnd.nifti.2")

    return None


def extract_metadata(metadata, property):
    """
    Extracts the value of a specified property from metadata using a mapping dictionary.

    The function looks up the corresponding property name in `mapping.bids2openMINDS_prop_dict` 
    and retrieves its value from the provided metadata dictionary. If the property is not found, 
    it returns None.

    Args:
        metadata (dict): A dictionary containing metadata.
        property (str): The property key to be extracted.

    Returns:
        Any or None: The value of the specified property if found, otherwise None.
    """
    property_name_bids = mapping.bids2openMINDS_prop_dict[property]

    if property_name_bids in metadata:
        return metadata[property_name_bids]

    return None


def create_QuantitativeValue(value, unit):
    """
    Creates a QuantitativeValue object with the given value and unit.

    If the value is None, the function returns None.

    Args:
        value (float or int or None): The numerical value of the quantity.
        unit (str): The unit of measurement for the value.

    Returns:
        QuantitativeValue or None: A QuantitativeValue object if value is provided, otherwise None.
    """

    if value is None:
        return None

    return QuantitativeValue(value=value, unit=UnitOfMeasurement.by_name(unit))


def create_boolean(value, property_name="property"):
    """
    The function checks if the extracted value is "true" (case-insensitive) and returns `True`, 
    or "false" (case-insensitive) and returns `False`. If the value is not recognized, a warning 
    is issued, and None is returned.

    Args:
        metadata (dict): A dictionary containing MRI metadata.

    Returns:
        bool or None: `True` if the value is "true", `False` if the value is "false", 
        otherwise `None`.

    Warnings:
        Issues a warning if the value is not "true" or "false".
    """

    if value is None:
        return None

    if value.strip().lower() == "true":
        return True

    if value.strip().lower() == "false":
        return False

    warn(f"The {value} is not an accepted value for {property_name}, it can only be 'true' or 'false'.")
    return None
