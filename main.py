import pygame
import os
import sys


def save(money, multiplayer, money_in_sec, shop_item_counts):
    with open('data/data.txt', 'w', encoding='utf-8') as f:
        f.write(f'{money};{multiplayer};{money_in_sec}')
        for i in shop_item_counts:
            f.write(f';{i}')


def load():
    with open('data/data.txt', 'r', encoding='utf-8') as f:
        data = f.read().split(';')
        money = int(data[0])
        multiplayer = int(data[1])
        money_in_sec = int(data[2])
        shop_item_counts = [int(count) for count in data[3:]]
        return money, multiplayer, money_in_sec, shop_item_counts


class ProgrammerClicker:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Programmer clicker')
        try:
            self.size = self.width, self.height = 700, 700
        except ValueError:
            print('Неправильный формат ввода')
            exit()
        self.screen = pygame.display.set_mode(self.size, pygame.RESIZABLE)
        self.screen.fill((255, 255, 255))
        pygame.mixer.music.load('data/music.mp3')
        pygame.mixer.music.play(loops=-1)
        pygame.mixer.music.set_volume(0.30)
        self.money = 0
        self.multiplayer = 1
        self.money_in_sec = 0
        self.last_tick_time = pygame.time.get_ticks()
        self.main_screen = pygame.sprite.Group()
        self.ClickButton = ClickButton(self.main_screen)
        self.ShopButton = ShopButton(self.main_screen)
        self.shop = Shop()
        self.open_shop = 0
        self.font = pygame.font.Font(None, 36)
        try:
            self.load_game_state()
        except FileNotFoundError:
            pass

    def save_game_state(self):
        count_shop = []
        for i in self.shop.all_item:
            count_shop.append(i.count)
        save(self.money, self.multiplayer, self.money_in_sec, count_shop)

    def load_game_state(self):
        self.money, self.multiplayer, self.money_in_sec, shop_item_counts = load()
        for i in range(len(shop_item_counts)):
            self.shop.all_item[i].count = shop_item_counts[i]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_game_state()
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.ClickButton.rect.collidepoint(event.pos):
                self.handle_click()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.ShopButton.rect.collidepoint(event.pos):
                if self.open_shop == 0:
                    self.open_shop = 1
                else:
                    self.open_shop = 0
            if self.open_shop == 1:
                for i in self.shop.all_item:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and i.get_buy_button().rect.collidepoint(event.pos):
                        i.on_click(self)

    def handle_click(self):
        self.money += 1 + self.multiplayer

    def update_display(self):
        self.screen.fill((255, 255, 255))
        score_text = self.font.render(f"Денег: {self.money}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        multiplier_text = self.font.render(f"Множитель: {self.multiplayer}", True, (0, 0, 0))
        self.screen.blit(multiplier_text, (10, 50))
        money_in_sec_text = self.font.render(f"Деньги/сек: {self.money_in_sec}", True, (0, 0, 0))
        self.screen.blit(money_in_sec_text, (10, 90))
        if self.open_shop == 1:
            pygame.draw.rect(self.screen, pygame.Color('gray'), (350, 100, 350, 500))
            all_buy_button = pygame.sprite.Group()
            for i in self.shop.all_item:
                i.render(self.screen)
            all_buy_button.draw(self.screen)
        current_time = pygame.time.get_ticks()
        elapsed_time = current_time - self.last_tick_time
        if elapsed_time >= 1000:
            self.money += self.money_in_sec
            self.last_tick_time = current_time
        self.main_screen.draw(self.screen)
        pygame.display.flip()
        pygame.time.Clock().tick(60)

    def run(self):
        while True:
            self.handle_events()
            self.update_display()


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    return pygame.image.load(fullname)


class ClickButton(pygame.sprite.Sprite):
    image = load_image("button.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = ClickButton.image
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = 275
        self.mask = pygame.mask.from_surface(self.image)


class Shop:
    def __init__(self):
        self.all_item = [ShopItem('Процессор', '1 д. за клик', 100, 0, 1, 110),
                         ShopItem('Видеокарта', '2 д. за клик', 200, 0, 2, 200),
                         ShopItem('Оперативная память', '1 д./сек', 100, 1, 0, 290)]


class ShopItem:
    def __init__(self, name, description, price, money_in_sec, multiplayer, start_num):
        self.name = name
        self.description = description
        self.price = price
        self.money_in_sec = money_in_sec
        self.multiplayer = multiplayer
        self.count = 0
        self.font = pygame.font.Font(None, 36)
        self.start_num = start_num
        self.buy_button = None

    def render(self, screen):
        item_text = self.font.render(self.name, True, (0, 0, 0))
        screen.blit(item_text, (360, self.start_num))
        item_text = self.font.render(f"{self.description} - {self.price + (self.count * 25)} д. - {self.count}x", True, (0, 0, 0))
        screen.blit(item_text, (360, self.start_num + 25))
        if self.buy_button:
            self.buy_button.rect.y = self.start_num + 20
            screen.blit(self.buy_button.image, self.buy_button.rect.topleft)

    def on_click(self, cat_clicker):

        if cat_clicker.money >= self.price + (self.count * 25):
            self.price += self.count * 25
            cat_clicker.money -= self.price
            cat_clicker.money_in_sec += self.money_in_sec
            cat_clicker.multiplayer += self.multiplayer
            self.count += 1

    def get_buy_button(self, group=None):
        if not self.buy_button:
            if group:
                self.buy_button = BuyButton(group, x=340, y=self.start_num + 20)
            else:
                self.buy_button = BuyButton(x=340, y=self.start_num + 20)
        return self.buy_button


class BuyButton(pygame.sprite.Sprite):
    image = load_image("buy.png")

    def __init__(self, *group, x, y):
        super().__init__(*group)
        self.image = BuyButton.image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.mask = pygame.mask.from_surface(self.image)


class ShopButton(pygame.sprite.Sprite):
    image = load_image("shop_button.png")

    def __init__(self, *group):
        super().__init__(*group)
        self.image = ShopButton.image
        self.rect = self.image.get_rect()
        self.rect.x = 600
        self.rect.y = 10
        self.mask = pygame.mask.from_surface(self.image, 1)


if __name__ == "__main__":
    clicker_game = ProgrammerClicker()
    clicker_game.run()
