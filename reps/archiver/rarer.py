from patoolib import create_archive, extract_archive
import os

#RARArchiver
# @purpose - the archiver which can extract and create winrar archives
class RARArchiver:

    def __init__(self):
        self.extension = '.rar'

    #extract
    # @params - the path to source winrar file and path to destination
    #   where the contents will be written
    # @return - no return values
    # @purpose - extract the contents of a winrar archive
    def extract(self, src, dest):
        #make destination directory first, or else patool complains
        #also change replay
        try:
            os.mkdir(dest)
        except OSError:
            pass

        extract_archive(src, outdir=dest)
    

    #create
    # @params - the name to give the archive and the directory to start compression
    #   and paths to compress into rar
    # @return - no return values
    # @purpose - create a winrar archive with the given name.
    def create(self, archive_name, archive_root):
        create_archive(archive_name, [archive_root])
