import os

DIRECTORY = "butterfly_images"
IMAGE_URL_PREFIX = "https://d1y65j5e4tchkc.cloudfront.net/"
IMAGE_SUFFIX = ".jpeg"
BUTTERFLY_NAMES_FILENAME = "butterfly_names.txt"


def cleanup_image_names():
    for root, dirs, files in os.walk(DIRECTORY):
        for filename in files:
            new_name = filename.replace(".png", "").lower()
            new_path = os.path.join(root, new_name)
            old_path = os.path.join(root, filename)
            os.rename(old_path, new_path)


def get_file_names():
    file_names = []
    for root, dirs, files in os.walk(DIRECTORY):
        for filename in files:
            file_names.append(filename)
    return file_names


def save_file_names_to_file(filename, names):
    with open(filename, "w") as f:
        for name in names:
            f.write("%s\n" % name)


def save_image_names_to_file():
    file_names = get_file_names()
    save_file_names_to_file(BUTTERFLY_NAMES_FILENAME, file_names)


def get_butterfly_names():
    with open(BUTTERFLY_NAMES_FILENAME, "r") as f:
        lines = [line.rstrip() for line in f]
    return lines


def rename_files():
    with open(BUTTERFLY_NAMES_FILENAME, "r") as f:
        lines = [line.rstrip() for line in f]
    removed_prefix_lines = [l.replace(IMAGE_URL_PREFIX, "") for l in lines]
    remove_file_extension = [l.replace(".jpeg", "") for l in lines]
    save_file_names_to_file(BUTTERFLY_NAMES_FILENAME, remove_file_extension)


if __name__ == "__main__":
    butterfly_names = get_butterfly_names()
    values = [
        f"(1600, '{n}', '{IMAGE_URL_PREFIX}{n}{IMAGE_SUFFIX}')" for n in butterfly_names
    ]
    values_string = ",".join(values)
    sql_string = """INSERT INTO butterflies
        (rating, name, image_url)
        VALUES {values};""".format(
        values=values_string
    )
    print(sql_string[0:200])

    # pass
