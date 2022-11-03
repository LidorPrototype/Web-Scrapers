import subprocess
import os
import datetime, time
import shutil

# Avarage Process Time: 2-4 hours
# New Avarage Time: 50-60 minutes

def ensure_dir(folder):
    """
        If the directory :folder: does not exists, create it
    """
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
    except OSError as e:
        raise


def get_all_stores_path(path):
    def f(path):
        if os.path.isdir(path):
            d = {}
            for name in os.listdir(path):
                d[name] = f(os.path.join(path, name))
        else:
            d = os.path.getsize(path)
        return d
    d = f(path)
    _paths_ = []
    for key in d.keys():
        _paths_.append(path.split("\\")[-1] + "\\" + key)
    return _paths_


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


breaker = "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ !Breaker Line! ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
start = time.time()
FNULL = open(os.devnull, 'w')    # In order to suppress output to stdout from the subprocess
filename = "\"app.exe\""
yesterdays_date = datetime.datetime.strftime(datetime.datetime.now() - datetime.timedelta(1), '%Y_%m_%d')
input_dir = (os.getcwd() + "\\ExportsInputs").replace("net6.0\\", "")
output_dir = (os.getcwd() + "\\ExportsOutputs").replace("net6.0\\", "")
ensure_dir(output_dir)
paths_to_stores = get_all_stores_path(input_dir + f"\\{yesterdays_date}")
print(breaker)
for path_to_store in paths_to_stores:
    print("path_to_store: ", path_to_store)
    input_folder = f"\\{input_dir}" + f"\\{path_to_store}"
    output_folder = f"\\{output_dir}" + f"\\{path_to_store}\\"
    if input_folder[0] == "\\":
        input_folder = input_folder[1:]
    if output_folder[0] == "\\":
        output_folder = output_folder[1:]
    ensure_dir(output_folder)
    yesterdays_date = yesterdays_date.replace("_", "/")
    extra_args = f" {input_folder} {output_folder} {yesterdays_date}"
    args = filename + extra_args
    print(args)
    try:
        return_code = subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=False)
        print(return_code)
    except FileNotFoundError as e:
        try:
            return_code = subprocess.call(args, stdout=FNULL, stderr=FNULL, shell=True, cwd="net6.0")
            print(return_code)
        except Exception as e:
            print(breaker)
            template = "An exception of type {0} occurred. Arguments:\n{1!r}"
            message = template.format(type(e).__name__, e.args)
            print(message)
            print(breaker)
    print(f"I'm going to delete this now: {os.getcwd()}\\ExportsInputs\\{path_to_store}")
    delete_old_files(os.getcwd() + "\\ExportsInputs\\" + path_to_store)
    print(breaker)
end = time.time()
time_dif = end - start
print(f"This entire process took: {str(datetime.timedelta(seconds=int(time_dif)))} seconds")


