import argparse
import os
import sys
import time
import logging
from pprint import pprint
import moviepy.editor as mp
from tqdm import tqdm
from youtube_upload.client import YoutubeUploader
from subprocess import call


def main(args):
    print(args)
    # Lets create a logger
    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if args.debug else logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.info("Starting GoPro-Uploader")
    # Lets check if the path exists
    if not os.path.exists(args.path):
        logger.error("The path provided does not exist")
        return

    # Make sure that the provided path is a directory
    if not os.path.isdir(args.path):
        logger.error("The path provided is not a directory")
        return

    # # Lets check if the secrets file exists
    # if not os.path.exists(args.secrets):
    #     logger.error("The secrets file does not exist")
    #     return

    # First we will need to authenticate with the youtube api
    # uploader = YoutubeUploader()
    # uploader.authenticate()

    # Lets get a list of files from the provided path
    files = os.listdir(args.path)
    logger.debug(files)
    logger.info("Found {} files in the provided path".format(len(files)))

    # Then lets grab all of the mp4 files
    mp4_files = [file for file in files if file.endswith(".MP4")]
    logger.info("Found {} mp4 files in the provided path".format(
        len(mp4_files)))
    print(mp4_files)

    # Now we need to generate lists such that we can combine the files that are from the same recording
    # We will do this by checking the last 8 characters of the file name
    # If the last 8 characters are the same then we will assume that the files are from the same recording
    # We will then combine the files into a list and add that list to a list of lists
    # This will allow us to upload the files in the correct order

    # First we will create a dictionary where the key is the last 8 characters of the file name
    # and the value is a list of files that have the same last 8 characters
    recordings = {}
    for file in mp4_files:
        key = file[-8:]
        if key in recordings:
            recordings[key]["files"].append(file)
        else:
            recordings[key] = {"files": [file]}

    # Now we will sort the files in each list
    for key in recordings:
        recordings[key]["files"].sort()

    # Now we will update the recordings dictionary to include the time that the first file was created
    for key in recordings:
        recordings[key]["time"] = os.path.getmtime(
            os.path.join(args.path, recordings[key]["files"][0]))

        recordings[key]["filename"] = os.path.join(args.path,
                                                   "combined" + key + ".mp4")

    # Now we can grab the information about each game
    call(["open", args.path])
    for key in recordings:
        print("Enter the First Team name for game {}".format(key))
        recordings[key]["first_team"] = input("First Team: ")
        print("Enter the Second Team name for game {}".format(key))
        recordings[key]["second_team"] = input("Second Team: ")
        print("Enter the location of the game {}".format(key))
        recordings[key]["location"] = input("Location: ")
        recordings[key]["title"] = "{} vs {} at {} on {}".format(
            recordings[key]["first_team"], recordings[key]["second_team"],
            recordings[key]["location"], time.ctime(recordings[key]["time"]))

    pprint(recordings)
    input("Press enter to continue and upload the videos to youtube.")

    # for key in tqdm(recordings):
    #     #Use moviepy to combine each list of videos into a single video
    #     clips = [
    #         mp.VideoFileClip(os.path.join(args.path, file))
    #         for file in recordings[key]["files"]
    #     ]
    #     # Concatenate the clips
    #     final_clip = mp.concatenate_videoclips(clips)
    #     # Write the result to a file
    #     # Make sure that the file name does not exist already
    #     if os.path.exists(recordings[key]["filename"]):
    #         logger.error("The file {} already exists. Not overwriting.".format(
    #             recordings[key]["filename"]))
    #         continue
    #     final_clip.write_videofile(recordings[key]["filename"])

    # New we will go ahead and upload the footage to youtube
    # We will do this by using the youtube api
    # We will use the google api client library for python

    # Now we will upload the videos
    for key in tqdm(recordings):
        num_files = len(recordings[key]["files"])
        for i, file in enumerate(recordings[key]["files"]):
            options = {
                "title": f'{recordings[key]["title"]} ({i + 1}/{num_files})',
                "privacyStatus":
                "unlisted",  # Video privacy. Can either be "public", "private", or "unlisted"
                "kids":
                False,  # Specifies if the Video if for kids or not. Defaults to False.
            }
            logger.info("Uploading a video with the following options")
            logger.info(options)
            uploader.upload(os.path.join(args.path, file), options=options)


if __name__ == '__main__':
    # generate argument parser
    parser = argparse.ArgumentParser(
        description=
        'Welcome to GoPro-Uploader. Please provide the following arguments.')
    parser.add_argument('-p',
                        '--path',
                        help='Path to the folder containing the GoPro files',
                        required=True)
    # parser.add_argument('-s',
    #                     '--secrets',
    #                     help='Path to the secrets.json file',
    #                     required=True)
    parser.add_argument('-d',
                        '--debug',
                        help='Enable debug mode',
                        action='store_true',
                        default=True)
    args = parser.parse_args()

    main(args)
