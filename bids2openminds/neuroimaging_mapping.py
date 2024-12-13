import openminds.latest.neuroimaging as neuroimaging
import openminds.latest.controlled_terms as controlled_terms
import openminds.latest.core as omcore

def add_mri_scanner(mri_scanners,mri_scanner):
    def eq(mri_scanner1, mri_scanner2):

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

def create_mri_scanner(metadata,mri_scanners,dataset_full_name):

    if "Manufacturer" in metadata:
        manufacturers=omcore.Organization(full_name=metadata["Manufacturer"])
    else:
        manufacturers=None
    
    if "ManufacturersModelName" in metadata:
        name=metadata["ManufacturersModelName"]
    else:
        name=f"MRI scanner used in {dataset_full_name}"
    
    if "DeviceSerialNumber" in metadata:
        serial_number=metadata["DeviceSerialNumber"]
    else:
        serial_number=None
    
    if "StationName" in metadata:
        lookup_label=metadata["StationName"]
    else:
        lookup_label=None

    if "MagneticFieldStrength" in metadata:
        magnetic_field_strength=omcore.QuantitativeValue(
            value=float(metadata["MagneticFieldStrength"]),
            unit=controlled_terms.UnitOfMeasurement.by_name("tesla"))

    else:
        magnetic_field_strength=None

    if "InstitutionName" in metadata:
        institution=omcore.Organization(full_name=metadata["InstitutionName"])
        if "InstitutionalDepartmentName" in metadata:
            department_name=f"{metadata["InstitutionName"]} department of {metadata["InstitutionName"]}"
            owner=omcore.Organization(
                full_name=department_name,
                has_parents=institution)
        else:
            owner=institution
    else:
        owner=None

    #TODO more information about MRI scanner can be added to description 
    
    mri_scanner=neuroimaging.MRIScanner(
        manufacturers=manufacturers,
        name=name,
        serial_number=serial_number,
        lookup_label=lookup_label,
        magnetic_field_strength=magnetic_field_strength,
        owner=owner
    )
    
    return mri_scanner
    

def create_functional_MRI_acquisition():
    return None



def create_neuroimaging(bids_layout,collection,subject_dict):
    mri_scanners=[],
    nifti_files=bids_layout.get(extension=["nii.gz","nii"])
    for file in nifti_files:
        metadata=file.get_metadata()
        entities=file.get_entities()
        mri_scanner = create_mri_scanner(metadata, mri_scanners)

        if "session" in entities:
            session = entities["session"]
        else:
            session = ""

        if "datatype" in entities:
            if entities["datatype"] == "func":
                create_functional_MRI_acquisition()

