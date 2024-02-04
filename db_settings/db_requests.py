import random
import io

import numpy as np

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from PIL import Image, ImageOps

from db_settings.db_models import Player, Base, Card, CardEdition, Character, Drop
from utils.bot_commands_fucntionality import generate_cards


class InitializeDataBase:

    def __init__(self):
        """ Values for random selecting """
        self.some_series = {
            'Jujutsu Kaisen': ['Satoru Gojo', 'Megumi Fushiguro', 'Itadori Yuji'],
            'Re Zero': ['Emilia', 'Rem', 'Ram', 'Echidna', 'Natsuki Subaru']
        }

    """ DB initializing """
    engine = create_engine("sqlite://", echo=True)
    initialize_db = Base.metadata.create_all(engine)
    session = Session(bind=engine)


class MainPlayer(InitializeDataBase):
    def __init__(self, player):
        super().__init__()
        self.player = player

    def create_player(self):
        """ Creating Player """
        player = Player(name=self.player, is_verified=True)
        self.session.add(player)

    def collection(self):
        player_cards_collection = self.session.query(Card).join(Card.player).where(Player.name == self.player).all()
        return player_cards_collection


class DropCards(InitializeDataBase):

    def __init__(self, drop_qty: int | None = None) -> None:
        super().__init__()

        """ A variable for expanding functionality in the future """
        self.drop_qty = drop_qty

        self.select_random_series = [random.choice([i for i in self.some_series.keys()]) for s in range(self.drop_qty)]
        self.select_characters_by_series = [random.choice(self.some_series[c]) for c in self.select_random_series]
        self.select_card_edition = [random.choice([i for i in range(1, 4)]) for num in range(self.drop_qty)]

    def generate_path(self) -> list:
        """ Generating path by above values """

        path_to_character_img = [
            (f'character_images/{"_".join(self.select_random_series[i].lower().split())}/'
             f'{"_".join(self.select_characters_by_series[i].lower().split())}/ed_{self.select_card_edition[i]}/'
             f'{"_".join(self.select_characters_by_series[i].lower().split())}.jpg')
            for i in range(self.drop_qty)
        ]

        return path_to_character_img

    """ Generating card codes """
    card_code = [''.join(generate_cards(1)) for i in range(3)]

    def create_character_for_card(self):
        """ Creating character """

        character = [
            Character(character_name=self.select_characters_by_series[i],
                      series=self.select_random_series[i],
                      wishlist=20000,
                      edition_num=self.select_card_edition[i],
                      edition=[
                          CardEdition(image=self.generate_path()[i]),
                      ],
                      cards=[
                          Card(code=[''.join(generate_cards(1)) for i in range(3)][i])
                      ]
                      )
            for i in range(self.drop_qty)

        ]
        print(character)
        return character

    def run(self) -> None:
        """ Adding some values to a database """

        self.session.add_all(self.create_character_for_card())
        drop_count = Drop()
        self.session.add(drop_count)

        print(self.session.query(Player).all())
        print(self.session.query(Character).all())
        print(self.session.query(CardEdition).all())
        print(self.session.query(Card).all())
        drop_id = select(Drop.id)
        print(self.session.scalars(drop_id).all())

    def images(self):
        """ Selecting image from database """

        get_character_ids = list(zip(*self.session.query(Card.character_id).all()[-3:]))[0]
        print('--- GET CHARACTER ---')
        print(get_character_ids)

        image = [
            select(CardEdition.image)
            .join(CardEdition.character)
            .where(Character.id == get_character_ids[i])
            for i in range(self.drop_qty)
        ]

        image = [self.session.scalars(image[i]).all() for i in range(3)]
        print('--- IMAGE ---')
        print(image)

        """ Showing image """
        get_image = list(zip(*image))[0]

        return get_image

    def merge(self):
        """ Merging images and we result in bytes """

        """ Image board creation """
        img = Image.new('RGBA', (836, 419))

        """ Resizing images we are claimed from images func """
        resize_image = [ImageOps.fit(Image.open(self.images()[i]), (230, 355)) for i in range(self.drop_qty)]

        """ Boards left side width """
        width = 24

        """ Pasting all three images into our board with a distance of 74 pixels between the pictures """
        for i in range(self.drop_qty):
            img.paste(resize_image[i], (width, 32))
            width += resize_image[i].size[0] + 50

        """ Getting bytes of our board """
        buffer = io.BytesIO()
        buffer.name = 'image.png'
        img.save(buffer, format='PNG')

        return buffer


class GrabCard(InitializeDataBase):

    def grab(self):
        get_character_ids = list(zip(*self.session.query(Card.id).all()))[0]
        print('--- GRAB ---')
        print(get_character_ids)
        return get_character_ids


if __name__ == '__main__':
    """ Player creation """
    player = MainPlayer(player='xyro')
    player.create_player()

    """ Drop Creation """
    drop = DropCards(3)
    drop.run()
    Image._show(Image.open(io.BytesIO(drop.merge().getvalue())))

    """ Grab creation """
    grab = GrabCard()
    grab.grab()
