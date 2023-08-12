import os
import sys
import hashlib

def compute_md5(filename):
    with open(filename, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

def download_and_cut_video(url, start, stop):
    output_file = "downloaded_video.mp4"
    download_command = f"/usr/local/bin/yt-dlp -f bestvideo+bestaudio/best -o {output_file} {url}"
    os.system(download_command)

    trimmed_output_file = "trimmed_video.mp4"
    cut_command = f"ffmpeg -i {output_file} -ss {start} -to {stop} -c:v copy -c:a copy {trimmed_output_file}"
    os.system(cut_command)

    md5_hash = compute_md5(trimmed_output_file)
    final_output_file = f"{md5_hash}.mp4"
    os.rename(trimmed_output_file, final_output_file)

    os.remove(output_file)

    print(f"Trimmed video saved as {final_output_file}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: download-and-trim.py <video_url> <start_time> <end_time>")
        sys.exit(1)
    
    video_url = sys.argv[1]
    start_time = sys.argv[2]
    end_time = sys.argv[3]

    download_and_cut_video(video_url, start_time, end_time)
