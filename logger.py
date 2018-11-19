from collections import OrderedDict


def prepare_log(initial_line='', ending_line='\n'):

    def decorator(func):

        def wrap(*args, **kwargs):
            Logger().write(initial_line)

            result = func(*args, **kwargs)

            Logger().write(ending_line)
            return result

        return wrap

    return decorator


class Logger(object):
    __instance = None
    __ROOMS = OrderedDict()

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls.__instance, cls):
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    def save(self, room, filename='default.log.txt'):
        self.__check(room)
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(self.__ROOMS[room])

    def __check(self, room):
        if not self.exist(room):
            raise Exception(f'Room {room} does not exist')

    def __validate(self, value):
        if type(value) != str:
            raise TypeError(f'Only strings accessible, not {type(value)}')

    def exist(self, room):
        return room in self.__ROOMS

    def is_empty(self, room):
        self.__check(room)

        if self.__ROOMS[room]:
            return False

        return True

    def set_room(self, room, value):
        self.__check(room)
        self.__validate(value)
        self.__ROOMS[room] = value

    def get_room(self, room):
        self.__check(room)
        return self.__ROOMS[room]

    def create_room(self, room, force=False):
        if self.exist(room) and not force:
            raise Exception(f'Room {room} already exist')
        self.__ROOMS[room] = ''

    def delete_room(self, room, force=False):
        self.__check(room)
        if self.__ROOMS[room] and not force:
            raise Exception(f'Room {room} is not empty')
        del self.__ROOMS[room]

    def write_into(self, room, string, create_if_not_exist=False):
        if create_if_not_exist and not self.exist(room):
            self.create_room(room)

        self.__check(room)
        self.__validate(string)
        self.__ROOMS[room] += string

    def clear_room(self, room):
        self.create_room(room, force=True)

    def merge_rooms(self, merge_into, rooms, create_if_not_exist=False, clear_merged=True):
        if create_if_not_exist:
            self.__ROOMS.setdefault(merge_into, '')

        self.__check(merge_into)

        if type(rooms) != list:
            raise TypeError('Rooms must be presented as list of room names')

        for room in rooms:
            self.__check(room)
            self.__ROOMS[merge_into] += self.__ROOMS[room]

            if clear_merged:
                self.clear_room(room)
