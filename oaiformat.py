import json
import os
import random


def load_and_process(file_path, system_prompt):
    # Load the data from the file
    with open(file_path, "r") as file:
        data = json.load(file)

    # Determine the key in the JSON file ('maxims' or 'poems')
    key = "maxims" if "maxims" in data else "poems"

    # Format the data according to OpenAI's format
    formatted_data = []
    for item in data[
        key
    ]:  # Ensure we're iterating over the list within the 'maxims' or 'poems' key
        formatted_data.append(
            {
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": item["input"]},
                    {"role": "assistant", "content": item["output"]},
                ]
            }
        )

    return formatted_data


def save_data(data, file_path):
    # Save the data to a .jsonl file
    with open(file_path, "w") as file:
        for entry in data:
            file.write(json.dumps(entry) + "\n")


def main():
    # Ensure the processed directory exists
    os.makedirs("processed", exist_ok=True)

    # Define system prompts for each type of data
    poem_prompt = "You are Johann Wolfgang von Goethe. Continue writing your poem."
    maxim_prompt = "You are Johann Wolfgang von Goethe. Respond to the following questions or statements."

    # Process poems and maxims
    poems = load_and_process("data/poems.json", poem_prompt)
    maxims = load_and_process("data/maxims.json", maxim_prompt)

    # Combine poems and maxims into one dataset
    combined_data = poems + maxims
    random.shuffle(combined_data)  # Shuffle the combined dataset

    # Split the combined data into training and validation sets
    split_index = int(0.9 * len(combined_data))  # 90% for training, 10% for validation
    train_data = combined_data[:split_index]
    val_data = combined_data[split_index:]

    # Save the combined training and validation data
    save_data(train_data, "processed/train.jsonl")
    save_data(val_data, "processed/val.jsonl")


if __name__ == "__main__":
    main()
