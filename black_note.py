from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from db_settings.db_models import Player, Base, Card, CardEdition, Character
from PIL import Image, ImageOps
from sqlalchemy import select
import random

""" DB initializing """
engine = create_engine("sqlite://", echo=True)
initialize_db = Base.metadata.create_all(engine)

session = Session(bind=engine)
print(session)

""" Values for random selecting """
some_series = {
    'Jujutsu Kaisen': ['Satoru Gojo', 'Megumi Fushiguro', 'Itadori Yuji'],
    'Re Zero': ['Emilia', 'Rem', 'Ram', 'Echidna', 'Natsuki Subaru']
}

""" Selecting random: Character name, Series, Edition """
select_some_series = [random.choice([i for i in some_series.keys()]) for s in range(3)]
select_some_characters = [random.choice(some_series[c]) for c in select_some_series]
select_some_edition = [random.choice([i for i in range(1, 4)]) for num in range(1, 4)]

""" Generating path by above values """
path_to_character_img = [
    (f'character_images/{"_".join(select_some_series[i].lower().split())}/'
     f'{"_".join(select_some_characters[i].lower().split())}/ed_{select_some_edition[i]}/'
     f'{"_".join(select_some_characters[i].lower().split())}.jpg')
    for i in range(3)
]

print(select_some_series)
print(select_some_characters)
print(select_some_edition)
print(path_to_character_img)

""" Creating card """
some_card = Card(code='r3980fe')

""" Creating character """
some_character = [
    Character(character_name=select_some_characters[i],
              series=select_some_series[i],
              wishlist=20000,
              edition_num=select_some_edition[i],
              edition=[
                  CardEdition(image=path_to_character_img[i]),
              ],
              cards=[
                  some_card,
              ]
              )
    for i in range(3)
]

""" Creating Player """
some_player = Player(name='Adel', is_verified=True, player_cards=[
    some_card,
])

print(some_player)
""" Adding some values to a database """
session.add(some_player)
session.add_all(some_character)

#
# """ Getting some information about model """
# print(session.query(Card).join(Card.character).where(Character.character_name == select_some_characters).all())
# print(session.query(Character).filter_by(character_name=select_some_characters).all())
print(session.query(Character).all())
print(session.query(CardEdition).all())
print(session.query(Player).all())

""" Selecting image from database """

image = [
    session.query(CardEdition.image)
    .join(CardEdition.character)
    .where(Character.character_name == select_some_characters[i])
    .first()
    for i in range(3)
]

""" Showing image """

get_image = list(zip(*image))[0]
print(get_image)


def merge():
    img = Image.new('RGBA', (836, 419))

    resize_image = [ImageOps.fit(Image.open(get_image[i]), (230, 355)) for i in range(3)]

    width = 24
    for i in range(3):
        img.paste(resize_image[i], (width, 32))
        width += resize_image[i].size[0] + 50
    return img.show()


merge()
