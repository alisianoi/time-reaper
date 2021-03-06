#!/usr/bin/env python

from datetime import datetime
from datetime import timedelta
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.db.model import Base
from src.db.model import SlotModel
from src.db.model import TagModel
from src.db.model import TaskModel


def create_a_day(session, delta):
    """
    Create a single simple day of tasks

    Note:
        Function attempts to create non-overlapping tasks. However, if
        the date changes while this function is being called several
        times, then overlapping tasks can be created. Pay attention!
    """

    chores_tag = TagModel(name='Chores')
    health_tag = TagModel(name='Health')
    workout_tag = TagModel(name='Workout')
    free_time_tag = TagModel(name='Free Time')

    cook_task = TaskModel(name='Cook breakfast/dinner/supper')
    shop_task = TaskModel(name='Buy groceries')
    wash_task = TaskModel(name='Do the washing')

    movies_task = TaskModel(name='Watch Deadpool')
    internet_task = TaskModel(name='Surf the web')

    aerobic_task = TaskModel(name='Run \'em miles')
    anaerobic_task = TaskModel(name='Lift \'em weights')

    chores_tag.tasks = [cook_task, shop_task, wash_task]
    health_tag.tasks = [aerobic_task, anaerobic_task]
    workout_tag.tasks = [aerobic_task, anaerobic_task]
    free_time_tag.tasks = [movies_task, internet_task]

    base = datetime.utcnow() - delta

    aerobic_slot0 = SlotModel(
        task=aerobic_task
        , fst=base.replace(hour=8, minute=0, second=0)
        , lst=base.replace(hour=9, minute=0, second=0)
    )

    anaerobic_slot0 = SlotModel(
        task=anaerobic_task
        , fst=base.replace(hour=21, minute=30, second=0)
        , lst=base.replace(hour=22, minute=0 , second=0)
    )

    shop_slot0 = SlotModel(
        task=shop_task
        , fst=base.replace(hour=11, minute=4, second=2)
        , lst=base.replace(hour=13, minute=8, second=9)
    )

    wash_slot0 = SlotModel(
        task=wash_task
        , fst=base.replace(hour=13, minute=20, second=44)
        , lst=base.replace(hour=13, minute=55, second=18)
    )

    movies_slot0 = SlotModel(
        task=movies_task
        , fst=base.replace(hour=19, minute=0, second=0)
        , lst=base.replace(hour=20, minute=10, second=0)
    )

    internet_slot0 = SlotModel(
        task=internet_task
        , fst=base.replace(hour=15, minute=20, second=2)
        , lst=base.replace(hour=18, minute=33, second=2)
    )

    cook_slot0 = SlotModel(
        task=cook_task
        , fst=base.replace(hour=10, minute=10, second=10)
        , lst=base.replace(hour=10, minute=43, second=32)
    )

    cook_slot1 = SlotModel(
        task=cook_task
        , fst=base.replace(hour=14, minute=19, second=43)
        , lst=base.replace(hour=14, minute=55, second=22)
    )

    cook_slot2 = SlotModel(
        task=cook_task
        , fst=base.replace(hour=20, minute=30, second=0)
        , lst=base.replace(hour=21, minute=10, second=1)
    )

    session.add_all([chores_tag, workout_tag, free_time_tag])
    session.add_all([
        cook_task, shop_task, wash_task, aerobic_task, anaerobic_task,
        movies_task, internet_task
    ])
    session.add_all([
        cook_slot0, cook_slot1, cook_slot2, aerobic_slot0, shop_slot0,
        anaerobic_slot0, wash_slot0, movies_slot0, internet_slot0
    ])

    session.commit()


if __name__ == '__main__':

    dbpath = Path(Path.cwd(), Path('tslot.db'))

    engine = create_engine('sqlite:///{}'.format(dbpath))

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    Session = sessionmaker()
    Session.configure(bind=engine)

    session = Session()

    for days in range(0, 25):
        create_a_day(session, timedelta(days=days))
