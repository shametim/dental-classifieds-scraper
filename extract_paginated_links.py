def extract_urls(file_path, indexes):
    urls = []
    with open(file_path, "r") as file:
        lines = file.readlines()
        for index in indexes:
            # Subtracting 1 from index since list indexing starts at 0
            if 0 <= index - 1 < len(lines):
                line = lines[index - 1]
                # Extract URL from the line, assuming it's formatted as "1. url"
                url = line.split(" ", 1)[1].strip()
                urls.append(url)
    return urls


def save_urls_to_file(urls, output_file):
    with open(output_file, "w") as file:
        for url in urls:
            file.write(url + "\n")


# Provide the path to the outgoing_links.txt file and the set of indexes
file_path = "outgoing_links.txt"
output_file = "extracted_links.txt"

# TODO: find relevant with GPT
indexes = [241, 242, 243, 244, 245, 246, 247]
extracted_urls = extract_urls(file_path, indexes)

# Save the extracted URLs to a file
save_urls_to_file(extracted_urls, output_file)
