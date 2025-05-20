"""Main module for the sample project."""

import utils

def main():
    """Run the program."""
    utils.helper()
    print("Hello, LLMStruct!")

class App:
    """Application class."""
    def run(self):
        """Execute the app."""
        utils.log("Running app")

if __name__ == "__main__":
    main()