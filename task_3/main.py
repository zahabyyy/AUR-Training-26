from abc import ABC, abstractmethod
from enum import Enum


class ItemStatus(Enum):
    AVAILABLE = "AVAILABLE"
    CHECKED_OUT = "CHECKED_OUT"
    LOST = "LOST"

ITEM_REGISTRY = {}

def register_item(item_type):
    def decorator(cls):
        ITEM_REGISTRY[item_type] = cls
        return cls
    return decorator

class LibraryItem(ABC):
    def __init__(self, title):
        self.title = title
        self._status = ItemStatus.AVAILABLE 

    @property
    @abstractmethod
    def loan_period(self):
        pass

    def checkout(self):
        if self._status == ItemStatus.AVAILABLE:
            self._status = ItemStatus.CHECKED_OUT
        else:
            print(f"Cannot checkout {self.title}: Currently {self._status.name}")

    def return_item(self):
        self._status = ItemStatus.AVAILABLE

    def mark_lost(self):
        self._status = ItemStatus.LOST

    def __lt__(self, other):
        return self.title < other.title

    def __repr__(self):
        return f"{self.__class__.__name__}(title={self.title!r}, status={self._status.name})"

    def __str__(self):
        status_str = self._status.name.replace('_', ' ').title()
        return f"{self.title} ({self.__class__.__name__}) - {status_str}"

    @staticmethod
    def validate_isbn(isbn):
        isbn = str(isbn).replace("-", "")
        if len(isbn) != 13 or not isbn.isdigit():
            return False
        
        total = 0
        for i, digit in enumerate(isbn):
            weight = 1 if i % 2 == 0 else 3
            total += int(digit) * weight
        return total % 10 == 0

    @classmethod
    def from_dict(cls, data):
        item_type = data.get("type")
        if item_type in ITEM_REGISTRY:
            return ITEM_REGISTRY[item_type].from_dict(data)
        raise ValueError(f"Unknown item type: {item_type}")



@register_item("Book")
class Book(LibraryItem):
    loan_period = 21

    def __init__(self, title, author, isbn):
        super().__init__(title)
        self.author = author
        self.isbn = isbn

    @classmethod
    def from_dict(cls, data):
        item = cls(data["title"], data["author"], data["isbn"])
        if "status" in data:
            item._status = ItemStatus[data["status"]]
        return item

@register_item("DVD")
class DVD(LibraryItem):
    loan_period = 5

    def __init__(self, title, director):
        super().__init__(title)
        self.director = director

    @classmethod
    def from_dict(cls, data):
        item = cls(data["title"], data["director"])
        if "status" in data:
            item._status = ItemStatus[data["status"]]
        return item

@register_item("Magazine")
class Magazine(LibraryItem):
    loan_period = 14

    def __init__(self, title, issue):
        super().__init__(title)
        self.issue = issue

    @classmethod
    def from_dict(cls, data):
        item = cls(data["title"], data["issue"])
        if "status" in data:
            item._status = ItemStatus[data["status"]]
        return item



class Database:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def load_items(self, filename="database.txt"):
        items = []
        try:
            with open(filename, "r") as file:
                for line in file:
                    line = line.strip()
                    if not line: continue
                    
                    data_dict = dict(pair.split("=") for pair in line.split("|"))
                    items.append(LibraryItem.from_dict(data_dict))
        except FileNotFoundError:
            print(f"{filename} not found. Starting with empty database.")
        return items

class Library:
    def __init__(self, database):
        self.db = database
        self.collection = self.db.load_items()

    def add_item(self, item):
        self.collection.append(item)

    def checkout_item(self, title):
        item = self.find_by_title(title)
        if item:
            item.checkout()

    def return_item(self, title):
        item = self.find_by_title(title)
        if item:
            item.return_item()

    def find_by_title(self, title):
        for item in self.collection:
            if item.title.lower() == title.lower():
                return item
        print("Item not found.")
        return None

    def list_available(self):
        available = sorted([item for item in self.collection if item._status.name == "AVAILABLE"])
        for item in available:
            print(item)


if __name__ == "__main__":
    db = Database()
    my_library = Library(db)
    
    print("--- Available Items (Sorted) ---")
    my_library.list_available()
    
    print("\n--- Checking out Dune ---")
    my_library.checkout_item("Dune")
    
    print("\n--- Available Items after checkout ---")
    my_library.list_available()