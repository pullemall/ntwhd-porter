def get_message_content(message):  # pylint: disable=too-many-return-statements
    """
        returns actual message content for each message type
    """
    if message.content_type == "photo":
        return message.photo[0].file_id
    if message.content_type == "text":
        return message.text
    if message.content_type == "audio":
        return message.audio.file_id
    if message.content_type == "document":
        return message.document.file_id
    if message.content_type == "sticker":
        return message.sticker.thumb.file_id
    if message.content_type == "video":
        return message.video.file_id
    if message.content_type == "voice":
        return message.voice.file_id
    return message.text or "None"