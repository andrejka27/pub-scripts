#!/usr/bin/python3

import os
import hashlib
import subprocess
import argparse
import uuid
import shutil

VIDEO_FORMAT = ".mp4"
YT_DLP_PATH = "/usr/local/bin/yt-dlp"
FFMPEG_PATH = "ffmpeg"

def check_dependencies():
    dependencies = [YT_DLP_PATH, FFMPEG_PATH, "aria2c"]
    for dep in dependencies:
        if shutil.which(dep) is None:
            raise EnvironmentError(f"Required binary '{dep}' not found. Please ensure it's installed and available in PATH.")

def compute_md5(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def run_command(command_list, msg):
    print(msg)
    process = subprocess.Popen(command_list, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"Command failed with error: {stderr.decode()}")

def download_and_cut_video(url, start, stop, output_directory="."):
    temp_video_name = f"{uuid.uuid4()}{VIDEO_FORMAT}"
    trimmed_temp_name = f"{uuid.uuid4()}{VIDEO_FORMAT}"

    try:
        run_command(
            [YT_DLP_PATH, "--external-downloader", "aria2c", "-f", "bestvideo+bestaudio/best", "-o", temp_video_name, url],
            "Downloading video with yt-dlp..."
        )

        run_command(
            [FFMPEG_PATH, "-i", temp_video_name, "-ss", start, "-to", stop, "-c:v", "copy", "-c:a", "copy", trimmed_temp_name],
            "Trimming video with ffmpeg..."
        )

        md5_hash = compute_md5(trimmed_temp_name)
        final_output_file_name = f"{md5_hash}{VIDEO_FORMAT}"
        final_output_file_path = os.path.join(output_directory, final_output_file_name)
        os.rename(trimmed_temp_name, final_output_file_path)

    finally:
        if os.path.exists(temp_video_name):
            os.remove(temp_video_name)

    print(f"Trimmed video saved as {final_output_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and trim videos using yt-dlp and ffmpeg.")
    parser.add_argument("video_url", help="URL of the video to be downloaded.")
    parser.add_argument("start_time", help="Start time for trimming (e.g., 00:00:21).")
    parser.add_argument("end_time", help="End time for trimming (e.g., 00:01:10).")
    parser.add_argument("-d", "--directory", default=".", help="Output directory for the final video. Defaults to the current directory.")
    
    args = parser.parse_args()

    output_directory = args.directory

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    try:
        check_dependencies()
        download_and_cut_video(args.video_url, args.start_time, args.end_time, output_directory)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
