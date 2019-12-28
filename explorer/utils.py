import os

def file_cleanup(sender, **kwargs):
    '''Delete the file associated with the model's instance.
    Using signal because simpy overwriting the delete method
    does not work for bulk operations.
    '''
    instance = kwargs['instance']
    if not instance.is_demo:
        os.remove(instance.file.path)
