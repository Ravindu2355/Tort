import os
import libtorrent as lt
import time
import sys
import shutil
from pyrogram import Client, filters
from pyrogram.types import InputFile
from pyrogram.errors import RPCError
from moviepy.editor import VideoFileClip

# Initialize the bot with API ID, API Hash, and Bot Token
api_id = os.getenv("apiid")  # Replace with your API ID
api_hash = os.getenv("apihash")  # Replace with your API Hash
bot_token = os.getenv("tk") # Replace with your Bot Token

# Initialize the Pyrogram Client
app = Client("TorrentBot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define download folder
download_dir = "/path/to/download/folder"

# Function to generate thumbnail for video files
def generate_thumbnail(video_path, thumbnail_path):
    try:
        video = VideoFileClip(video_path)
        video.save_frame(thumbnail_path, t=1.0)  # Save thumbnail at 1 second
        return thumbnail_path
    except Exception as e:
        print(f"Error generating thumbnail: {e}")
        return None

# Function to handle torrent downloading
def download_torrent(torrent_file, chat_id, message_id):
    # Create a session
    ses = lt.session()

    # Load the torrent file
    info = lt.torrent_info(torrent_file)
    h = ses.add_torrent({'ti': info, 'save_path': download_dir})

    # Prepare to send initial message
    message = app.edit_message_text(chat_id, message_id, f"Downloading {h.name()}...")

    # Start the download loop
    last_update = time.time()
    
    while not h.is_seed():
        # State information
        state = h.status()
        progress = state.progress * 100
        download_rate = state.download_rate / 1000
        upload_rate = state.upload_rate / 1000
        num_peers = state.num_peers

        # Only update the message every 10 seconds to avoid flooding
        if time.time() - last_update > 10:
            try:
                # Update the progress message
                app.edit_message_text(chat_id, message_id, 
                    f"Downloading {h.name()}...\n"
                    f"Progress: {progress:.1f}%\n"
                    f"Down: {download_rate:.1f} kB/s | Up: {upload_rate:.1f} kB/s\n"
                    f"Peers: {num_peers}\n"
                )
                last_update = time.time()
            except RPCError:
                pass  # Ignore any error from Telegram API flood

        # Sleep for a bit before checking the progress again
        time.sleep(1)

    # Once download is complete, check if it's a video and handle accordingly
    try:
        downloaded_file = os.path.join(download_dir, h.name())
        is_video = downloaded_file.lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.flv'))

        if is_video:
            # Generate thumbnail
            thumbnail_path = os.path.join(download_dir, f"{h.name()}_thumbnail.jpg")
            thumbnail = generate_thumbnail(downloaded_file, thumbnail_path)

            if thumbnail:
                # Send the video as streamable with thumbnail
                app.edit_message_text(chat_id, message_id, f"Download complete! Sending video: {h.name()} now...")
                with open(downloaded_file, "rb") as video_file:
                    app.send_video(
                        chat_id,
                        video_file,
                        caption=f"Here is your video: {h.name()}",
                        thumb=InputFile(thumbnail)
                    )
            else:
                # Send video without thumbnail if thumbnail generation failed
                app.edit_message_text(chat_id, message_id, f"Download complete! Sending video: {h.name()} now...")
                with open(downloaded_file, "rb") as video_file:
                    app.send_video(
                        chat_id,
                        video_file,
                        caption=f"Here is your video: {h.name()}"
                    )
        else:
            # If the file is not a video, send it as a regular file
            app.edit_message_text(chat_id, message_id, f"Download complete! Sending file: {h.name()} now...")
            app.send_document(chat_id, InputFile(downloaded_file))

    except Exception as e:
        app.edit_message_text(chat_id, message_id, f"Error during download: {str(e)}")

# Start command handler
@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("Send me a torrent file or magnet link to start the download.")

# Handle file (torrent file) download request
@app.on_message(filters.document.mime_type("application/x-bittorrent"))
def handle_torrent(client, message):
    try:
        # Download the torrent file
        torrent_file_path = f"/path/to/save/torrents/{message.document.file_name}"
        message.download(torrent_file_path)

        # Send an initial message to notify the user that the download has started
        progress_msg = message.reply_text("Starting download...")

        # Call the function to download the torrent
        download_torrent(torrent_file_path, message.chat.id, progress_msg.message_id)
    except Exception as e:
        message.reply_text(f"An error occurred while handling the torrent: {str(e)}")

# Handle magnet link download request
@app.on_message(filters.text)
def handle_magnet(client, message):
    if message.text.startswith("magnet:?"):
        try:
            # Save the magnet link to a temporary file (for simplicity)
            torrent_file_path = "/path/to/temp/magnet.torrent"
            with open(torrent_file_path, "w") as f:
                f.write(message.text)

            # Send an initial message to notify the user that the download has started
            progress_msg = message.reply_text("Starting download...")

            # Call the function to download the torrent from the magnet link
            download_torrent(torrent_file_path, message.chat.id, progress_msg.message_id)
        except Exception as e:
            message.reply_text(f"An error occurred while handling the magnet link: {str(e)}")

# Run the bot
app.run()
