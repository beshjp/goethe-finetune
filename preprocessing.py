import json
import re

from bs4 import BeautifulSoup


def clean_poem_input(text):
    # Split the text into two sections
    before_period, after_period = text.split(".", 1)

    # Clean the section after the first period
    cleaned_after_period = (
        after_period.replace("\u2014", "")
        .replace("\n", "")
        .replace("-", "")
        .replace("*", "")
        .strip()
    )
    # Remove Notes
    cleaned_after_period = re.sub(r"\[.*\)", "", cleaned_after_period, flags=re.DOTALL)
    cleaned_after_period = re.sub(r"\(.*\)", "", cleaned_after_period, flags=re.DOTALL)
    cleaned_after_period = re.sub(r"\[.*\]", "", cleaned_after_period, flags=re.DOTALL)

    # Combine the sections back together
    cleaned_text = before_period.strip() + "——" + cleaned_after_period

    return cleaned_text


def extract_poems(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    poems = []

    # Pattern to identify title/date lines
    title_date_pattern = re.compile(r"^\s*\d{4}\.\*?\s*——")

    current_poem = []
    current_title = "1797. DEDICATION."

    # Start from the first relevant paragraph
    current_tag = soup.find("p", {"id": "id00109"})

    # Flag to check if the previous tag was a title
    prev_tag_was_title = False

    while current_tag:
        if current_tag.name == "p" or (
            current_tag.name == "h5" and not prev_tag_was_title
        ):
            text = current_tag.get_text().strip()

            if title_date_pattern.match(text):  # If it's a title/date line
                if current_poem:  # Save the current poem
                    poems.append(
                        {"input": current_title, "output": "\n".join(current_poem)}
                    )
                    current_poem = []
                current_title = text
                prev_tag_was_title = True
            else:
                current_poem.append(text)
                prev_tag_was_title = False

        current_tag = current_tag.find_next_sibling(
            ["p", "h5", "h2"]
        )  # Look for next sibling that is p, h5, or h2

        if (
            current_tag is None
            or current_tag.get("id") == "id05473"
            or (
                current_tag.name == "h2"
                and title_date_pattern.match(current_tag.get_text().strip())
            )
        ):
            poems.append({"input": current_title, "output": "\n".join(current_poem)})

    # Manual fixes
    poems[1]["output"] = poems[1]["output"].split("TO THE KIND READER.\n")[1]
    poems[1]["input"] += "TO THE KIND READER."

    # Clean the poems and create proper input
    for poem in poems:
        # Remove anything in parenthesis that contains "Goethe" case insensitive
        poem["output"] = re.sub(
            r"\(.*Goethe.*\)", "", poem["output"], flags=re.IGNORECASE
        )
        # Remove square brackets content
        poem["output"] = re.sub(
            r"\[.*\]", "", poem["output"], flags=re.DOTALL
        )  # Remove (* ) content
        poem["output"] = re.sub(
            r"\(\*.*\)", "", poem["output"], flags=re.DOTALL
        )  # Remove (* ) content
        poem["output"] = poem["output"].replace("*", "")  # Remove asterisks
        # Remove something enclosed by [ and  )
        poem["output"] = re.sub(r"\[.*\)", "", poem["output"], flags=re.DOTALL)

        # Clean the input
        poem["input"] = clean_poem_input(poem["input"])
        # Add the first line of the poem to the input after the title split by a newline
        poem["input"] += "\n" + poem["output"].split("\n")[0]

    return poems


def extract_maxims(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        html_content = file.read()

    soup = BeautifulSoup(html_content, "html.parser")
    maxims = []

    # Extracting Maxims
    for i in range(1, 591):
        anchor = soup.find("a", id=f"a{i}")
        if anchor:
            number_tag = anchor.parent
            text_tag = number_tag.find_next_sibling("p")
            if text_tag:
                maxim_number = number_tag.get_text(strip=True)
                maxim_text = " ".join(text_tag.get_text().split())
                maxims.append({"number": maxim_number, "output": maxim_text})

    # Extracting Nature Aphorisms
    nature_aphorisms_text = []
    nature_aphorisms_anchor = soup.find("a", id="NATURE_APHORISMS")
    if nature_aphorisms_anchor:
        current_tag = nature_aphorisms_anchor.find_parent("h2").find_next_sibling()
        while current_tag and current_tag.name != "h2":
            if current_tag.name == "p":
                paragraph_text = " ".join(current_tag.get_text().split())
                nature_aphorisms_text.append(paragraph_text)
            current_tag = current_tag.find_next_sibling()

    # Add Nature Aphorisms as a single entry with proper line breaks
    if nature_aphorisms_text:
        maxims.append(
            {
                "number": "NATURE: APHORISMS",
                "output": "\n\n".join(nature_aphorisms_text),
            }
        )

    return maxims


def merge_maxims(maxims, maxims_input):
    merged_maxims = []
    for maxim, maxim_input in zip(maxims, maxims_input["maxims"]):
        merged_maxim = {"input": maxim_input["input"], "output": maxim["output"]}
        merged_maxims.append(merged_maxim)
    return merged_maxims


def main():
    # Load maxims-input.json
    with open("data/maxims-input.json", "r", encoding="utf-8") as file:
        maxims_input = json.load(file)

    # Extract maxims and merge with input
    maxims = extract_maxims("data/maxims-reflections.html")
    maxims = merge_maxims(maxims, maxims_input)

    # Extract poems
    poems = extract_poems("data/poems.html")

    # Save to files
    with open("data/maxims.json", "w", encoding="utf-8") as file:
        json.dump({"maxims": maxims}, file, indent=4)
    with open("data/poems.json", "w", encoding="utf-8") as file:
        json.dump({"poems": poems}, file, indent=4)


if __name__ == "__main__":
    main()
