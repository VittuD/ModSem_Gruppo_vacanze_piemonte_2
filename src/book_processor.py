import json
import pandas as pd

# Main function
def main():
    input_file = 'book_details/Beowulf.json'
    output_file = 'book_details/Beowulf_test.csv'

    # Open the file with pandas
    with open(input_file, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    df.to_csv(output_file, index=False)

if __name__ == "__main__":
    main()
