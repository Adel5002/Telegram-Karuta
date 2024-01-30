import random

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from PIL import Image, ImageOps

from db_settings.db_models import Player, Base, Card, CardEdition, Character
from utils.bot_commands_fucntionality import generate_cards


class InitializeDataBase:
    """ DB initializing """

    def __init__(self):
        self.engine = create_engine("sqlite://", echo=True)
        self.initialize_db = Base.metadata.create_all(self.engine)
        self.session = Session(bind=self.engine)

        """ Values for random selecting """
        self.some_series = {
            'Jujutsu Kaisen': ['Satoru Gojo', 'Megumi Fushiguro', 'Itadori Yuji'],
            'Re Zero': ['Emilia', 'Rem', 'Ram', 'Echidna', 'Natsuki Subaru']
        }

        self.select_random_series = [random.choice([i for i in self.some_series.keys()]) for s in range(3)]
        self.select_characters_by_series = [random.choice(self.some_series[c]) for c in self.select_random_series]
        self.select_card_edition = [random.choice([i for i in range(1, 4)]) for num in range(1, 4)]


class DropCards(InitializeDataBase):

    def generate_path(self) -> list:
        """ Generating path by above values """
        path_to_character_img = [
            (f'../character_images/{"_".join(self.select_random_series[i].lower().split())}/'
             f'{"_".join(self.select_characters_by_series[i].lower().split())}/ed_{self.select_card_edition[i]}/'
             f'{"_".join(self.select_characters_by_series[i].lower().split())}.jpg')
            for i in range(3)
        ]
        return path_to_character_img

    card = [Card(code=''.join(generate_cards(1))) for i in range(3)]

    def create_character_for_card(self):
        """ Creating character """
        print(self.card)
        character = [
            Character(character_name=self.select_characters_by_series[i],
                      series=self.select_random_series[i],
                      wishlist=20000,
                      edition_num=self.select_card_edition[i],
                      edition=[
                          CardEdition(image=self.generate_path()[i]),
                      ],
                      cards=[
                          self.card[i]
                      ]
                      )
            for i in range(3)
        ]
        return character

    def create_player(self):
        """ Creating Player """
        player = Player(name='Adel', is_verified=True, player_cards=[
            self.card[0]
        ])
        return player

    def run(self) -> None:
        """ Adding some values to a database """

        self.session.add(self.create_player())
        self.session.add_all(self.create_character_for_card())

        print(self.session.query(Player).all())
        print(self.session.query(Character).all())
        print(self.session.query(CardEdition).all())
        print(self.session.query(Card).all())

    def images(self):
        """ Selecting image from database """

        image = [
            self.session.query(CardEdition.image)
            .join(CardEdition.character)
            .where(Character.character_name == self.select_characters_by_series[i])
            .first()
            for i in range(3)
        ]

        """ Showing image """

        get_image = list(zip(*image))[0]
        return get_image

    def merge(self):
        img = Image.new('RGBA', (836, 419))

        resize_image = [ImageOps.fit(Image.open(self.images()[i]), (230, 355)) for i in range(3)]

        width = 24
        for i in range(3):
            img.paste(resize_image[i], (width, 32))
            width += resize_image[i].size[0] + 50
        return img.show()


class GrabCard(InitializeDataBase):
    pass


if __name__ == '__main__':
    drop = DropCards()
    drop.create_player()
    drop.run()
    drop.merge()
