import hashlib
import time 
from pathlib import Path 

def bytes_to_unit(num):
    """
    Convert bytes to KB, MB, GB and TB

    Parameters 
    ----------
    num : number of bytes
    """
    
    for unit in ['bytes','KB','MB','GB','TB']:
        if num < 1024:
            return f'{num:3.2f} {unit}'
        num /= 1024
        

class File:
    
    def __init__(self,filename):
        self.filename = filename
        
    def filesize(self):
        """ 
        Return string with size of the file in appropriate unit
        """
        
        return bytes_to_unit(self.filename.stat().st_size)

    def hash(self):
        """
        Return a unique id for the file. Moving, copying or renaming
        the file does not change the result. However the timestamp is 
        relevant and hence every edit changes the result. Undoing the 
        change is irrelevant since the timestamp remains changed.
        """
        
        with open(self.filename, 'rb', buffering=0) as f:
            return hashlib.file_digest(f, 'sha256').hexdigest()
        
        
        
        
def log_folder(path,
               excluded_folders=[],
               include_files=True,
               filename=True,
               max_depth=0,
               depth=0
              ):
    '''Returns the structure of path in a dictionary

    Parameters 
    ----------
    path  : pahtlib.Path
        The folder for which we save the structure.
        
    excluded_folders : 
        List of folders to exclude from the structure.

    include_files : bool
        Record a list with all contained files.

    filename : str or bool
        Save the result to a .json file
    
    max_depth : int
        How deep (in terms of subfolders) should be recorded.

    depth : 
        The depth of the current folder (needed for max_depth).
    '''

    # create the dictionary and add the current path
    structure = {'_path':str(path)} 
    # we save some additional information for the parent folder
    if depth == 0:
        structure['_date'] = time.strftime('%Y-%m-%d',time.gmtime())
    
    # record the name of the subfolders to dictionary
    subfolders = {x.name:{} for x in path.iterdir() if x.is_dir()}
    # we only fill them if we are not too deep yet
    if depth < max_depth:
        for key in subfolders.keys():
            # only parse folders that are not excluded and don't start with '.'
            if (key not in excluded_folders) and (not key.startswith('.')):
                # we call the function with the same parameters for the subfolder
                subfolders[key] = log_folder(path = path / key,
                                             excluded_folders=excluded_folders,
                                             include_files=include_files,
                                             filename=None,
                                             max_depth=max_depth,
                                             depth=depth+1,
                                            )
    structure['_subfolders'] = subfolders

    # save the files in that folder 
    if include_files:
        structure['_files'] = [x.name for x in path.iterdir() if x.is_file()]

    if filename:
        if isinstance(filename,bool):      
            # save to the folder `logs` as `YYYY-mm-dd_parent_folder.json`
            filename = Path('logs') / (f'{path.name}_log_' + time.strftime('%Y-%m-%d',time.gmtime()) + '.json')
            
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(structure, f, ensure_ascii=False, indent=4)
    
    return structure


def compare_structure(old_structure,
                      new_structure,
                      print_message=True,
                      save_message=False,
                      message=[]
                      ):
    '''compare two dictionaries
    
    old_structure : dict
        An old dictionary produced by `log_folder`.
        
    new_structure : dict
        The new dictionary produced by `log_folder`.

    print_message : bool
    '''

    path_old = old_structure['_path']
    path_new = new_structure['_path']
        
    # first we compare the files
    if ('_files' in old_structure.keys()) and  ('_files' in new_structure.keys()):
        old_files = set(old_structure['_files'])
        new_files = set(new_structure['_files'])

        for i, filename in enumerate(old_files - new_files):
            if i==0:
                message.append(f'Missing file(s) in {path_old}:')
            message.append(f'    {filename}')
        for i, filename in enumerate(new_files - old_files):
            if i==0:
                message.append(f'New file(s) in {path_old}:')
            message.append(f'    {filename}') 

    # next we compare the folders
    if ('_subfolders' in old_structure.keys()) and  ('_subfolders' in new_structure.keys()):
        # we turn the keys of the dict to a set
        old_subfolders = set(old_structure['_subfolders'])
        new_subfolders = set(new_structure['_subfolders'])

        for i, folder in enumerate(old_subfolders - new_subfolders):
            if i==0:
                message.append(f'Missing folder(s) in {path_old}:')
            message.append(f'    {folder}') 
        for i, folder in enumerate(new_subfolders - old_subfolders):
            if i==0:
                message.append(f'New folder(s) in {path_old}:')
            message.append(f'    {folder}') 
    
        # finally we go through the shared subfolders
        for key in (old_subfolders & new_subfolders):
            # we only continue if both dicts contain data for the subfolder
            if (len(old_structure['_subfolders'][key])>0) and (len(new_structure['_subfolders'][key])>0):
                compare_structure(old_structure['_subfolders'][key],
                                  new_structure['_subfolders'][key],
                                  print_message=False,
                                  save_message=False,
                                  message=message
                                 )

    # print or save the message
    if print_message:
        print('\n'.join(message))
    
    if save_message:
        filename = Path('logs') / (f'{Path(path_old).name}_diff_{old_structure["_date"]}_vs_{new_structure["_date"]}.txt')
        with open(filename, "w") as f:
            f.write('\n'.join(message))
            
    return message

