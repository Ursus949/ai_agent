import os


def get_files_info(working_directory, directory=".", extension_filter=None):
    abs_working_dir = os.path.abspath(working_directory)
    target_dir = os.path.abspath(os.path.join(working_directory, directory))

    if not target_dir.startswith(abs_working_dir):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

    if not os.path.isdir(target_dir):
        return f'Error: "{directory}" is not a directory'

    try:
        files_info = []
        for filename in sorted(os.listdir(target_dir)):
            filepath = os.path.join(target_dir, filename)

            try:
                if os.path.islink(filepath):
                    continue

                if extension_filter and not filename.endswith(extension_filter):
                    continue

                is_dir = os.path.isdir(filepath)
                file_size = os.path.getsize(filepath)

                files_info.append(
                    f"- {filename}: file_size={file_size} bytes, is_dir={is_dir}"
                )
            except Exception as e:
                files_info.append(f"- {filename}: Error: {e}")
        return "\n".join(files_info)
    except Exception as e:
        return f"Error listing files: {e}"

