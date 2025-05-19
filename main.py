import argparse
import re
import time

from playwright.sync_api import sync_playwright

from driver.automation.game_page import GamePage
from driver.images import (analyze_images, clean_up, download_images,
                           dummy_download, set_up)
from game.cards import find_matches

URL = "https://www.setgame.com/set/puzzle"


def automate(matches):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        game = GamePage(page)
        game.open(URL)

        for card_triplet in matches:
            print(f"Clicking cards in set: {card_triplet}")
            for card in card_triplet:
                game.click_card(card)

        time_text = page.locator("text=You completed today's puzzle in").inner_text()
        pattern = r"(\d+) hours (\d+) minutes and ([\d\.]+) seconds"
        match = re.search(pattern, time_text)

        if match:
            seconds = float(match.group(3))
            print(f"Solved in: {seconds} seconds")
        else:
            print("No time match found")

        browser.close()


def main():
    parser = argparse.ArgumentParser(description="Solve the Daily Set Puzzle")
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug mode (show image windows)"
    )
    parser.add_argument(
        "--use-dummy",
        action="store_true",
        help="Use dummy card download (offline image set)",
    )
    parser.add_argument(
        "--skip-download", action="store_true", help="Skip downloading images"
    )
    parser.add_argument(
        "--skip-cleanup",
        action="store_true",
        help="Save the downloaded files after solving",
    )

    args = parser.parse_args()

    print("SOLVING THE DAILY SET PROBLEM")
    start = time.perf_counter()
    set_up()

    if not args.skip_download:
        if args.use_dummy:
            dummy_download(URL)
        else:
            download_images(URL)

    cards = analyze_images(args.debug)
    matches = find_matches(cards)
    automate(matches)

    if not args.skip_cleanup:
        clean_up()

    end = time.perf_counter()
    elapsed = end - start
    print(f"Total runtime is {elapsed:.2f} seconds.")


if __name__ == "__main__":
    main()
