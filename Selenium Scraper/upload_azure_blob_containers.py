from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceExistsError
import os, time
from datetime import datetime, timedelta
import shutil
# Install the following package before running this program
# pip install azure-storage-blob

# Avarage Upload Time: 5-9 minutes


def delete_old_files(folder: str):
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.isfile(file_path) or os.path.islink(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (file_path, e))
    try:
        os.remove(folder)
    except Exception as e:
        try:
            shutil.rmtree(folder)
        except Exception as e:
            print('Failed to delete %s. Reason: %s' % (folder, e))


def upload_data(container_path: str, extra_folder: str = None):
    # Azure Storage connection string
    connect_str = "<INSTERT YOUR CONNECTION STRING HERE>"
    # Name of the Azure container
    container_name = container_path
    # The path to be removed from the local directory path while uploading it to ADLS
    path_to_remove = ""
    # The local directory to upload to ADLS
    output_dir = 'ExportsOutputs'
    local_path = output_dir + extra_folder
    print(local_path)
    # Establish a connection to the ADLS blob service
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    # The below code block will iteratively traverse through the files and directories under the given folder and uploads to ADLS.
    try:
        for r, d, f in os.walk(local_path):
            if f:
                for file in f:
                    file_path_on_azure = os.path.join(r, file).replace(path_to_remove, "")
                    if local_path in file_path_on_azure:
                        file_path_on_azure = file_path_on_azure[len(local_path) + 1:]
                    file_path_on_local = os.path.join(r, file)
                    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_path_on_azure)
                    with open(file_path_on_local, "rb") as data:
                        blob_client.upload_blob(data)
                try:
                    print("uploaded folder —-> ", file_path_on_local.split('\\')[1], "\t\tFull Path: ", file_path_on_local)
                except Exception as e:
                    print("EXCEPTION: ", str(e))
        delete_old_files(os.getcwd() + "\\ExportsOutputs")
    except ResourceExistsError:
        print("This Folder and/or File already exists in that location mate!\nPlease provide a new location...")
        print(file_path_on_local.split('\\')[1].strip())


if __name__ == '__main__':
    start = time.time()
    yesterday_date = datetime.strftime(datetime.now() - timedelta(1), '%Y_%m_%d')
    path_ = f"raw/foodmarket/raw_parquet/{yesterday_date}"
    print(path_)
    upload_data(path_, extra_folder = f"/{yesterday_date}")
    end = time.time()
    time_dif = end - start
    print(f"This entire upload took: {str(timedelta(seconds=int(time_dif)))} seconds")
