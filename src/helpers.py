import json
from fastapi.encoders import jsonable_encoder


def generate_links(stmt_id, messages, base_url):
    _list = []
    for message in messages:
        _message = jsonable_encoder(message)

        _files = []
        if isinstance(_message['file_path'], list):
            for _file in _message['file_path']:
                _files.append(
                    f"{base_url}/chat/download?stmt_id={stmt_id}&user_id={_message['user_id']}&file_id={_file['file_id']}&name={_file['name']}")

        _message['file_path'] = _files
        _list.append(_message)

    return json.dumps(_list)


def generate_link(stmt_id, message, base_url):
    _message = jsonable_encoder(message)

    _files = []
    if isinstance(_message['file_path'], list):
        for _file in _message['file_path']:
            _files.append(
                f"{base_url}/chat/download?stmt_id={stmt_id}&user_id={_message['user_id']}&file_id={_file['file_id']}&name={_file['name']}")

    _message['file_path'] = _files
    _list = [_message]

    return json.dumps(_list)
