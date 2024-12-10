mapping=[

]


def create_mriscanner(bids_layout,mri_scanners):
    if not(scanner in mri_scanners) or mri_scanners is empthy:
        mriscanner
    return mri_scanners
    



def create_neuroimaging(bids_layout,collection):
    mri_scanners=[],
    nifti_files=bids_layout.get(extension=['nii.gz','nii'])
    for file in nifti_files:
