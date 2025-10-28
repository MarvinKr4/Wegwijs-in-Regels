import argparse
import re


def encode_slashes_in_lido_uris(input_file, output_file):
    # Regular expression to match lido: URIs containing slashes, but not starting with http
    lido_uri_pattern = r"(lido:[^\s>]+)"

    try:
        # Open the input TTL file and read its content
        with open(input_file, "r", encoding="utf-8") as infile:
            content = infile.read()

        def encode_slashes(match):
            object_value = match.group(0)
            encoded_uri = object_value.replace("/", "%2F")
            print(f"Encoded URI: {encoded_uri}")  # Debugging: print the encoded URI
            return encoded_uri

        # Replace the lido URIs in the content with encoded slashes
        modified_content = re.sub(lido_uri_pattern, encode_slashes, content)

        with open(output_file, "w", encoding="utf-8") as outfile:
            outfile.write(modified_content)

        print(f"Successfully encoded slashes in lido URIs and saved to {output_file}")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        "--input", help="Input TTL file path", default="knowledge-graphs/JAS.ttl"
    )
    argparser.add_argument(
        "--output", help="Output TTL file path", default="knowledge-graphs/JAS.ttl"
    )

    args = argparser.parse_args()

    input_file: str = args.input
    output_file: str = args.output

    print(input_file)
    print(output_file)

    encode_slashes_in_lido_uris(input_file, output_file)
