class Title:
    def __init__(self, id, words=set()):
        self.id = id
        self.words = words
        self.articles = []

    def add_article(self, article):
        self.articles.append(article)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__
