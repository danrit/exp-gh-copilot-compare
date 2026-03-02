"""
Upload the list of files to the AWS S3 bucket.
"""

# settings:
CSV_FILE_PATH = 'data/export.lite.csv'

TIMESTAMP_FORMAT = '%Y%m%d-%H%M%S'

# SKIPPED_PREFIX path prefix in publicId file (from cloudinary) not in AWS S3.
SKIPPED_PREFIX = 'editorial/'
# EXTENSION_JPEG: this one is a best guess, as cloudinary seems to have remove
# the actual 'fake' extension the image was uploaded with and replaced it with
# the actual format of the image: psd. We will assume the original extension
# was jpg, because it seems to be the most common one in the dataset.
IMAGE_EXTENSION = 'jpg' #
# BACKUP_EXTENSION: all the files are PSD file originally. Prior to
# replacing the original by a real jpg version, we are doing a backup as PSD.
BACKUP_EXTENSION = 'psd'
