class Item:

    def __init__(self, title, view, link):
        self.title = title
        self.view = view
        self.link = link

    def __str__(self):
        return self.title + " " + str(self.view)
