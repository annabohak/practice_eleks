from tkinter import *
from tkinter.ttk import *
from tkcalendar import DateEntry
import json


class App(Frame):

    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.categories = []
        self.load_categories()
        self.create_UI()
        self.load_table()
        self.grid(sticky=(N, S, W, E))
        self.parent = parent
        self.parent.protocol("WM_DELETE_WINDOW", self.exit)

        self.parent.grid_rowconfigure(0, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.cached_items = []

    def exit(self):
        try:
            self.save_data()
            self.save_categories()
            self.parent.destroy()
        except:
            self.parent.destroy()

    def create_UI(self):
        tv = Treeview(self)
        tv['columns'] = ('task', 'category',)
        tv.heading('#0', text='Date')
        tv.column('#0', anchor='w', width=100)
        tv.heading('task', text='Task')
        tv.column('task', anchor='center', width=100)
        tv.heading('category', text='Category')
        tv.column('category', anchor='center', width=100)

        self.add_button = Button(self, text="Add", command=self.add_menu)
        self.add_button.grid(row=4, column=0, sticky=W)

        self.delete_button = Button(self, text="Delete", command=self.delete_data)
        self.delete_button.grid(row=4, column=1, sticky=W)

        self.categories_edit_button = Button(self, text="Categories", command=self.categories_edit_menu)
        self.categories_edit_button.grid(row=4, column=2, sticky=W)

        tv.grid(sticky=(N, S, W, E))
        self.treeview = tv
        for col in self.treeview['columns']:
            self.treeview.heading(col, text=col, command=lambda _col=col: self.treeview_sort_column(self.treeview, _col, False))
        self.treeview.grid(row=2, columnspan=3)


        self.search_string = StringVar()
        self.search_string.trace_add("write", self.search)
        self.search_entry = Entry(self, textvariable=self.search_string)
        self.search_entry.grid(row=0, columnspan=3)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def search(self, name, index, mode):
        print(self.search_string.get())
        if self.search_string.get() == '':
            self.clean_up_table()
            self.fill_up_table(self.cached_items)
        else:
            self.clean_up_table()
            self.fill_up_table(self.get_items_search(self.search_string.get()))

    def add_category(self):
        new_category = self.category_input.get()
        if new_category is not None and new_category != '' and new_category not in self.categories:
            self.categories.append(new_category)
        self.update_categories_list()

    def delete_related(self, dead_category):
        for child in self.treeview.get_children():
            if self.treeview.item(child)["values"][1] == dead_category:
                self.treeview.delete(child)
        self.cached_items = self.get_items()

    def delete_category(self):
        dead_category = self.categories_listbox.get("active")
        if dead_category in self.categories:
            self.categories.remove(dead_category)
            self.delete_related(dead_category)
        self.update_categories_list()

    def update_categories_list(self):
        self.categories_listbox.delete(0, "end")
        for category in self.categories:
            self.categories_listbox.insert("end", category)

    def categories_edit_menu(self):
        try:
            self.add_window.destroy()
        except:
            pass
        self.category_edit = Toplevel(self)
        self.category_edit.wm_title("Categories")
        self.category_input = Entry(self.category_edit, width=20)
        self.category_input.grid(row=1, column=0)

        self.add_category_button = Button(self.category_edit, text="Add category", command=self.add_category)
        self.add_category_button.grid(row=1, column=1)

        self.delete_category = Button(self.category_edit, text="Delete", command=self.delete_category)
        self.delete_category.grid(row=1, column=2)

        self.categories_listbox = Listbox(self.category_edit)
        self.categories_listbox.grid(row=2, column=0, columnspan=2)
        self.update_categories_list()

    def add_menu(self):
        try:
            self.categories_edit_menu.destroy()
        except:
            pass
        self.add_window = Toplevel(self)
        self.add_window.wm_title("Add task")
        self.label = Label(self.add_window, text="Task:")
        self.entry = Entry(self.add_window)
        self.label.grid(row=1, column=1, sticky=W)
        self.entry.grid(row=1, column=2)

        self.date_label = Label(self.add_window, text="Date:")
        self.date_entry = DateEntry(self.add_window)
        self.date_label.grid(row=2, column=1, sticky=W)
        self.date_entry.grid(row=2, column=2)

        self.variable = StringVar(self)
        self.variable.set('')
        self.category_label = Label(self.add_window, text="Category:")
        self.category_label.grid(row=3, column=1)
        self.w = OptionMenu(self.add_window, self.variable, *self.categories)
        self.w.grid(row=3, column=2)

        self.submit_button = Button(self.add_window, text="Insert", command=self.insert_data)
        self.submit_button.grid(row=4, column=1, sticky=W)

    def load_categories(self):
        try:
            with open('categories.json') as f:
                data = json.load(f)
            print(data)
            for category in data:
                self.categories.append(category)
        except FileNotFoundError:
            print('categories not found')

    def load_table(self):
        try:
            with open('data.json') as f:
                data = json.load(f)
            print(data)
            self.fill_up_table(data)
            self.cached_items = self.get_items()
        except FileNotFoundError:
            print('data not found')

    def fill_up_table(self, data):
        print(data)
        for item in data:
            self.treeview.insert('', 'end', text=item['date'], values=(item['task'], item['category']))

    def clean_up_table(self):
        for child in self.treeview.get_children():
            self.treeview.delete(child)

    def insert_data(self):
        if self.entry.get():
            self.treeview.insert('', 'end', text=self.date_entry.get(),
                                 values=(self.entry.get(), self.variable.get()))
            self.add_window.destroy()
        self.cached_items = self.get_items()

    def save_data(self):
        with open('data.json', 'w+') as f:
            json.dump(self.get_items(), f, ensure_ascii=False)

    def save_categories(self):
        cleared_categories = self.categories
        with open('categories.json', 'w+') as fp:
            json.dump(cleared_categories, fp)

    def delete_data(self):
        selected_items = self.treeview.selection()
        for item in selected_items:
            self.treeview.delete(item)
        self.cached_items = self.get_items()

    def treeview_sort_column(self, tv, col, reverse):
        items_list = [(tv.set(k, col), k) for k in tv.get_children('')]
        items_list.sort(reverse=reverse)

        for index, (val, k) in enumerate(items_list):
            tv.move(k, '', index)

        tv.heading(col, command=lambda: self.treeview_sort_column(tv, col, not reverse))

    def get_items(self):
        items = []
        for child in self.treeview.get_children():
            end = {'date': self.treeview.item(child)["text"],
                    'task': self.treeview.item(child)["values"][0],
                    'category': self.treeview.item(child)["values"][1],
                    }
            items.append(end)
        return items

    def get_items_search(self, string):
        items = []
        for item in self.cached_items:
            if str(string) in str(item["task"]):
                items.append(item)
        return items

def main():
    root = Tk()
    App(root)
    root.mainloop()


if __name__ == '__main__':
    main()
