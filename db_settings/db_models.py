from typing import Optional, List

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Table, Column


class Base(DeclarativeBase):
    pass


class Player(Base):
    __tablename__ = 'karuta_player'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    is_verified: Mapped[bool] = mapped_column(default=False)

    player_cards: Mapped[Optional[List['Card']]] = relationship(
        back_populates='player',
    )

    def __repr__(self) -> str:
        return f'User(id={self.id!r}, name={self.name!r})'


class Card(Base):
    __tablename__ = 'karuta_card'

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(7))

    player_id: Mapped[Optional[int]] = mapped_column(ForeignKey('karuta_player.id'))
    player: Mapped[Optional['Player']] = relationship(back_populates="player_cards")

    character_id: Mapped[int] = mapped_column(ForeignKey('anime_character.id'))
    character: Mapped['Character'] = relationship(back_populates='cards')

    def __repr__(self) -> str:
        return (f'Card(id={self.id!r},'
                f'code={self.code!r})')


""" Takes edition from CardEdition model and the cards to link them """


class Character(Base):
    __tablename__ = 'anime_character'

    id: Mapped[int] = mapped_column(primary_key=True)

    character_name: Mapped[str] = mapped_column(String(120))
    series: Mapped[str] = mapped_column(String(120))
    wishlist: Mapped[Optional[int]]
    edition_num: Mapped[int]
    # aliases: Mapped[Optional[list]]

    edition: Mapped[List['CardEdition']] = relationship(
        back_populates='character'
    )

    cards: Mapped[List['Card']] = relationship(
        back_populates='character'
    )

    def __repr__(self) -> str:
        return (
            f'Character(id={self.id}, character_name={self.character_name!r}, series={self.series!r}, wishlist={self.wishlist!r}, '
            f'edition_num={self.edition_num!r})')


"""Some editions for characters """


class CardEdition(Base):
    __tablename__ = 'karuta_card_edition'

    id: Mapped[int] = mapped_column(primary_key=True)
    image: Mapped[str] = mapped_column(String(255))

    character_id: Mapped[int] = mapped_column(ForeignKey('anime_character.id'))
    character: Mapped['Character'] = relationship(
        back_populates='edition'
    )

    def __repr__(self) -> str:
        return f'CardEdition(id={self.id!r}, image={self.image!r})'
