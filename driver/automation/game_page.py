from driver.automation.page import Page


class GamePage(Page):
    def __init__(self, page):
        super().__init__(page)

        self.cards = {f"card{i}": page.locator(f"[name=card{i}]") for i in range(1, 13)}

    def open(self, url):
        self.go_to(url)

    def click(self, locator):
        locator.click()

    def click_card(self, card_filename):
        card_name = self.preprocess_card(card_filename)
        locator = self.cards.get(card_name)
        if locator:
            self.click(locator)
        else:
            print(f"Locator for '{card_name}' not found.")

    def preprocess_card(self, card):
        return card[:-4] if card.endswith(".png") else card
