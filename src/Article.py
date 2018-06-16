class Article:
    def __init__(self, id="", categories=[]):
        self.id = id
        self.title_ids = []
        self.categories = categories

    def add_title(self, title_id):
        self.title_ids.append(title_id)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
