from math import ceil
from alembic.util.exc import CommandError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from metric.src import iniConfig
from metric.src.cabin import Cabin
from metric.src.path import auto

Model = declarative_base()


def session(connection=False):
    '''
    session(conection=bool(True/False))
    ---
    ____fungsi ini digunakan untuk system melakukan koneksi sesi ke database dengan menggunakan
    sesi yang ada pada fungsi sqlalchemy, dan konfigurasi .ini menggunakan alembic konfigurasi.
    parameter connection berfungsi sebagai penanda dari sesi koneksi dalam boolean, jika "True"
    maka koneksi akan digunakan untuk membuat engine, jika tidak koneksi digunakan untuk mengikat
    sesi pada database____
    ---
    '''
    config = iniConfig()
    try:
        url = config.get_main_option('sqlalchemy.url')
    except CommandError as e:
        raise e
    else:
        if not connection:
            session_ng = sessionmaker(bind=create_engine(url), expire_on_commit=False)
            return session_ng()
        else:
            return create_engine(url).begin()


class DB:
    def __init__(self):
        """
        ## **DB**
        ____This class is served as class declared all the model from the directory, collected and gather into one
        property class so which class inherit DB can use all the model by calling the attribute____
        """
        self.model = lambda: None
        for k, v in auto('databases', 'models', 'databases/models').items():
            setattr(self.model, v.__name__, v)

    def pagination(self, model, page=0, limit=10, *args):
        """
        ## **PAGINATION**
        ____This function is purposely serve as additional utility for model as pagination pre-rendered and
        returned in HTML display____

        :param model: Model object
        :param page : Page position
        :param limit: Limit record in a page
        :param args : List column to shown
        :return Object with attribute Total, Page, & Data
        """
        result = lambda: None
        record_count = model.count()
        record_pagination = '<ul class="uk-pagination">'

        for i in range(1, ceil(record_count / limit) + 1):
            record_pagination += '<li class="uk-active">' if i - 1 == page else '<li>'
            record_pagination += f'<a href="?page={i}">{i}</a></li>'

        record_pagination += '</ul>'
        record_data = model.select(*args) if args else model.select()

        setattr(result, 'total', record_count)
        setattr(result, 'page', record_pagination)
        setattr(result, 'data', record_data)

        result.data = result.data.grab(page, limit).all()
        return result
