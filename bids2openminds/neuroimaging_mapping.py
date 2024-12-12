MAP_2_NEUROIMAGING={
    "AcquisitionDuration":["acquisitionDuration"],
    "DelayAfterTrigger":["delayAfterTrigger"],
    "DelayTime":["delayTime"],
    "NumberOfVolumesDiscardedByUser":["numberOfVolumesDiscardedByUser"],
    "":["magneticFieldStrength"],

}

MAP_NEUroimaging_array={
    "VolumeTiming":["volumeTiming"]
}


def check_mri_scanner(mri_scanners,mri_scanner):
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


def create_mri_scanner(bids_layout,mri_scanners):
    
    if +
    return mri_scanner
    

def create_functional_MRI_acquisition():
    return None



def create_neuroimaging(bids_layout,collection,subject_dict):
    mri_scanners=[],
    nifti_files=bids_layout.get(extension=["nii.gz","nii"])
    for file in nifti_files:
        metadata=file.get_metadata()
        entities=file.get_entities()
        mri_scanner = create_mri_scanner(bids_layout, mri_scanners)

        if "session" in entities:
            session = entities["session"]
        else:
            session = ""

        if "datatype" in entities:
            if entities["datatype"] == "func":
                create_functional_MRI_acquisition()

