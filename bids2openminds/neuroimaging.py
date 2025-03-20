import openminds.latest.neuroimaging as neuroimaging
import openminds.latest.controlled_terms as controlled_terms
import openminds.latest.core as omcore
import warnings
from utility import extract_metadata, create_QuantitativeValue, create_boolean
from . import mapping




def create_mri_scanner(metadata, mri_scanners, collection, dataset_full_name):
    def _create_mri_scanner(metadata, dataset_full_name):

        if "Manufacturer" in metadata:
            manufacturers = omcore.Organization(full_name=metadata["Manufacturer"])
        else:
            manufacturers = None

        if "ManufacturersModelName" in metadata:
            name = metadata["ManufacturersModelName"]
        else:
            name = f"MRI scanner used in {dataset_full_name}"

        if "DeviceSerialNumber" in metadata:
            serial_number = metadata["DeviceSerialNumber"]
        else:
            serial_number = None

        if "StationName" in metadata:
            lookup_label = metadata["StationName"]
        else:
            lookup_label = None

        if "MagneticFieldStrength" in metadata:
            magnetic_field_strength = omcore.QuantitativeValue(
                value=float(metadata["MagneticFieldStrength"]),
                unit=controlled_terms.UnitOfMeasurement.by_name("tesla"))

        else:
            magnetic_field_strength = None

        if "InstitutionName" in metadata:
            institution = omcore.Organization(full_name=metadata["InstitutionName"])
            if "InstitutionalDepartmentName" in metadata:
                department_name = f"{metadata["InstitutionName"]} department of {metadata["InstitutionName"]}"
                owner = omcore.Organization(
                    full_name=department_name,
                    has_parents=institution)
            else:
                owner = institution
        else:
            owner = None

        # TODO more information about MRI scanner can be added to description

        mri_scanner = neuroimaging.MRIScanner(
            manufacturers=manufacturers,
            name=name,
            serial_number=serial_number,
            lookup_label=lookup_label,
            magnetic_field_strength=magnetic_field_strength,
            owner=owner
        )

        return mri_scanner

    def _eq(mri_scanner1, mri_scanner2):

        # If both have digital identifiers and they are same that means they are the same device
        if (mri_scanner1.digital_identifier is not None) and (mri_scanner2.digital_identifier is not None):
            if mri_scanner1.digital_identifier.identifier == mri_scanner2.digital_identifier.identifier:
                return True
            else:
                return False

        if (mri_scanner1.serial_number is not None) and (mri_scanner2.serial_number is not None):
            if mri_scanner1.serial_number == mri_scanner2.serial_number:
                return True
            else:
                return False

        if (mri_scanner1.name is not None) and (mri_scanner2.name is not None):
            if mri_scanner1.name == mri_scanner2.name:
                return True
            else:
                return False
        return False

    new_mri_scanner = _create_mri_scanner(metadata, dataset_full_name)

    for scanner in mri_scanners:
        if _eq(scanner, new_mri_scanner):
            return scanner

    collection.add(new_mri_scanner)
    mri_scanners.append(new_mri_scanner)
    return new_mri_scanner


def create_MRI_scanner_usage(metadata, mri_scanner, file_associations, files_dict, filename, dataset_full_name):

    def create_mr_acquisition_type(metadata):
        """
        Extracts the MRI acquisition type from the given metadata and returns a controlled term 
        if it is a recognized value. Otherwise, it issues a warning and returns None.

        Args:
            metadata (dict): A dictionary containing MRI metadata.

        Returns:
            controlled_terms.MRAcquisitionType or None: The corresponding MRI acquisition type 
            if found in the mapping, otherwise None.

        Warnings:
            Issues a warning if the extracted MRI acquisition type is not recognized.
        """
        mr_acquisition_type_text = extract_metadata(metadata, "MRAcquisitionType")
        
        if mr_acquisition_type_text is None:
            return None
        
        if mr_acquisition_type_text in mapping.MAP_2_MRACQUISITIONTYPE:
            return controlled_terms.MRAcquisitionType.by_name(mr_acquisition_type_text)
        
        warnings.warn(f"The {mr_acquisition_type_text} is not an accepted value for MRAcquisitionType")
        return None
    
    
    def create_echo_times(metadata):
        """
        Extracts echo times from the given metadata and converts them into QuantitativeValue objects.

        The function supports:
        - Lists of echo times (converted to a list of QuantitativeValue objects).
        - Single string echo times (converted to a QuantitativeValue object).
        - Separate "EchoTime1" and "EchoTime2" fields (if "echoTime" is missing).

        Args:
            metadata (dict): A dictionary containing MRI metadata.

        Returns:
            list[QuantitativeValue] or QuantitativeValue or None:
                - A list of QuantitativeValue objects if multiple echo times exist.
                - A single QuantitativeValue object if only one echo time is found.
                - None if no valid echo time is present.
        """
        echo_times_bids = extract_metadata(metadata, "echoTime")

        # If echoTime is a list, convert each item
        if isinstance(echo_times_bids, list):
            return [create_QuantitativeValue(item, "second") for item in echo_times_bids]

        # If echoTime is a string, convert it to a QuantitativeValue object
        if isinstance(echo_times_bids, str):
            return create_QuantitativeValue(float(echo_times_bids), "second")

        # If echoTime is not found, check EchoTime1 and EchoTime2
        echo_times = []
        flag_multiple_echo_time = False 

        if "EchoTime1" in metadata:
            echo_times.append(metadata["EchoTime1"])
            flag_multiple_echo_time = True

        if "EchoTime2" in metadata:
            echo_times.append(metadata["EchoTime2"])
            flag_multiple_echo_time = True

        # If multiple echo times exist, convert them
        if flag_multiple_echo_time:
            return [create_QuantitativeValue(float(item), "second") for item in echo_times]

        return None
    
    def create_pulse_sequence_type(metadata):

        pulse_sequence_text=extract_metadata(metadata, "MRIPulseSequence")

        if pulse_sequence_text in mapping.MAP_2_PULSESEQUENCETYPE:
            return controlled_terms.MRAcquisitionType.by_name(mapping.MAP_2_PULSESEQUENCETYPE(pulse_sequence_text))
        
        try:
            return controlled_terms.MRAcquisitionType.by_name(pulse_sequence_text)
        except:
            return None

    

    mr_acquisition_type=create_mr_acquisition_type(metadata)
    mt_state=create_boolean(extract_metadata(metadata, "MTState"), property_name="MTState")
    dwell_time=create_QuantitativeValue(extract_metadata(metadata, "dwellTime"),"second")
    echo_times=create_echo_times(metadata)
    flip_angle=create_QuantitativeValue(extract_metadata(metadata, "flipAngle"), "arcdegree")
    inversion_time=create_QuantitativeValue(extract_metadata(metadata, "inversionTime"), "second")
    lookup_label=f"The scanner usage for {filename} of {dataset_full_name}"

    file_associations_obj=[]
    for file_association in file_associations:
        if file_association.path in files_dict:
            file_associations_obj.append(files_dict[file_association.path])

    metadata_locations=file_associations_obj

    nonlinear_gradient_correction=create_boolean(extract_metadata(metadata, "nonlinearGradientCorrection"), property_name="NonlinearGradientCorrection")
    number_of_volumes_discarded_by_scanner=int(extract_metadata(metadata, "numberOfVolumesDiscardedByScanner"))
    parallel_acquisition_technique=str(extract_metadata(metadata, "parallelAcquisitionTechnique"))
    
    """TODO
    The implementation of `phase_encoding_direction` is pending as the controlled term is not yet finalized.  
    """


    pulse_sequence_type=create_pulse_sequence_type(metadata)

    
    

    
    




def create_fMRI_scanner_usage(metadata, mri_scanner, collection, file_associations, files_dict, filename, dataset_full_name):
    scanner_usage=create_MRI_scanner_usage(metadata, mri_scanner, file_associations, files_dict, filename, dataset_full_name)


    collection.add(scanner_usage)
    return scanner_usage




def create_fMRI_acquisition():
    
    return None


def create_neuroimaging(bids_layout, collection, files_dict, subject_dict, dataset_full_name):
    mri_scanners = [],
    nifti_files = bids_layout.get(extension=["nii.gz", "nii"])
    for file in nifti_files:
        metadata = file.get_metadata()
        entities = file.get_entities()
        file_associations=file.get_associations()

        mri_scanner = create_mri_scanner(metadata, mri_scanners, collection, dataset_full_name)

        if "session" in entities:
            session = entities["session"]
        else:
            session = ""

        if "datatype" in entities:
            if entities["datatype"] == "func":
                create_fMRI_scanner_usage(metadata, mri_scanner, collection, file_associations, files_dict, file.filename, dataset_full_name)
                create_fMRI_acquisition(metadata, mri_scanners, collection, dataset_full_name)
