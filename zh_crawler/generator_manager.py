# -*- coding: utf-8 -*-

import threading


class GeneratorManager:
    '''管理类'''

    def __init__(self):
        self.__kw_gens = dict()

    def __process(self, kwg):
        while kwg in self.__kw_gens:
            kwg(self.__kw_gens[kwg])

    def add_generator(self, kwg, data=None):
        '''data用于传递控制信息'''
        self.__kw_gens[kwg] = data
        t1 = threading.Thread(target=self.__process, args=(kwg,))
        t1.start()

    def remove_generator(self, kwg):
        del self.__kw_gens[kwg]

    def remove_all(self):
        self.__kw_gens.clear()

    @property
    def data(self):
        return self.__kw_gens.values()

    @data.setter
    def data(self, data):
        for kwg in self.__kw_gens.keys():
            self.__kw_gens[kwg] = data

    def set_data(self, kwg, data):
        if kwg in self.__kw_gens:
            self.__kw_gens[kwg] = data
