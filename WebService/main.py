from constants import DRIVE_FOLDER_ID
from drive_utils import load_data_from_drive_folder

documents = load_data_from_drive_folder(DRIVE_FOLDER_ID)


print(documents)