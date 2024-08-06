import tkinter as tk
from tkinter import filedialog
import json


class Book:
    def __init__(self, isbn, name, author, price, quantity):
        self.Isbn = isbn
        self.Name = name
        self.Author = author
        self.Price = price
        self.Quantity = quantity

class BTreeNode:
    def __init__(self, degree):
        self.Books = []
        self.Children = []
        self.Degree = degree

    @property
    def IsLeaf(self):
        return len(self.Children) == 0

class BTree:
    def __init__(self, t):
        self._t = t
        self._root = BTreeNode(t)

    def Insert(self, book):
        r = self._root
        if len(r.Books) == 2 * self._t - 1:
            s = BTreeNode(self._t)
            self._root = s
            s.Children.append(r)
            self.SplitChild(s, 0, r)
            self.InsertNonFull(s, book)
        else:
            self.InsertNonFull(r, book)
        print(f"Libro insertado con ISBN: {book.Isbn}")

    def InsertNonFull(self, x, book):
        i = len(x.Books) - 1
        if x.IsLeaf:
            x.Books.append(None)
            while i >= 0 and book.Isbn < x.Books[i].Isbn:
                x.Books[i + 1] = x.Books[i]
                i -= 1
            x.Books[i + 1] = book
        else:
            while i >= 0 and book.Isbn < x.Books[i].Isbn:
                i -= 1
            i += 1
            if len(x.Children[i].Books) == 2 * self._t - 1:
                self.SplitChild(x, i, x.Children[i])
                if book.Isbn > x.Books[i].Isbn:
                    i += 1
            self.InsertNonFull(x.Children[i], book)

    def SplitChild(self, x, i, y):
        z = BTreeNode(self._t)
        x.Children.insert(i + 1, z)
        x.Books.insert(i, y.Books[self._t - 1])
        z.Books = y.Books[self._t:(2 * self._t - 1)]
        y.Books = y.Books[0:(self._t - 1)]
        if not y.IsLeaf:
            z.Children = y.Children[self._t:(2 * self._t)]
            y.Children = y.Children[0:self._t]

    def Delete(self, isbn):
        self.DeleteNode(self._root, isbn)
        if len(self._root.Books) == 0:
            if not self._root.IsLeaf:
                self._root = self._root.Children[0]
            else:
                self._root = BTreeNode(self._t)
        print(f"Libro eliminado con ISBN: {isbn}")

    def DeleteNode(self, node, isbn):
        idx = next((i for i, book in enumerate(node.Books) if book.Isbn == isbn), -1)
        if idx != -1:
            if node.IsLeaf:
                node.Books.pop(idx)
            else:
                if len(node.Children[idx].Books) >= self._t:
                    pred = self.GetPredecessor(node, idx)
                    node.Books[idx] = pred
                    self.DeleteNode(node.Children[idx], pred.Isbn)
                elif len(node.Children[idx + 1].Books) >= self._t:
                    succ = self.GetSuccessor(node, idx)
                    node.Books[idx] = succ
                    self.DeleteNode(node.Children[idx + 1], succ.Isbn)
                else:
                    self.Merge(node, idx)
                    self.DeleteNode(node.Children[idx], isbn)
        else:
            if node.IsLeaf:
                return
            idx = next((i for i, book in enumerate(node.Books) if isbn < book.Isbn), len(node.Books))
            if len(node.Children[idx].Books) < self._t:
                self.Fill(node, idx)
            if idx > len(node.Books):
                self.DeleteNode(node.Children[idx - 1], isbn)
            else:
                self.DeleteNode(node.Children[idx], isbn)

    def GetPredecessor(self, node, idx):
        current = node.Children[idx]
        while not current.IsLeaf:
            current = current.Children[len(current.Books)]
        return current.Books[len(current.Books) - 1]

    def GetSuccessor(self, node, idx):
        current = node.Children[idx + 1]
        while not current.IsLeaf:
            current = current.Children[0]
        return current.Books[0]

    def Merge(self, node, idx):
        child = node.Children[idx]
        sibling = node.Children[idx + 1]
        child.Books.append(node.Books[idx])
        child.Books.extend(sibling.Books)
        if not child.IsLeaf:
            child.Children.extend(sibling.Children)
        node.Books.pop(idx)
        node.Children.pop(idx + 1)

    def Fill(self, node, idx):
        if idx != 0 and len(node.Children[idx - 1].Books) >= self._t:
            self.BorrowFromPrev(node, idx)
        elif idx != len(node.Books) and len(node.Children[idx + 1].Books) >= self._t:
            self.BorrowFromNext(node, idx)
        else:
            if idx != len(node.Books):
                self.Merge(node, idx)
            else:
                self.Merge(node, idx - 1)

    def BorrowFromPrev(self, node, idx):
        child = node.Children[idx]
        sibling = node.Children[idx - 1]
        child.Books.insert(0, node.Books[idx - 1])
        if not child.IsLeaf:
            child.Children.insert(0, sibling.Children.pop())
        node.Books[idx - 1] = sibling.Books.pop()

    def BorrowFromNext(self, node, idx):
        child = node.Children[idx]
        sibling = node.Children[idx + 1]
        child.Books.append(node.Books[idx])
        if not child.IsLeaf:
            child.Children.append(sibling.Children.pop(0))
        node.Books[idx] = sibling.Books.pop(0)

    def Update(self, isbn, updates):
        book = self.SearchByIsbn(self._root, isbn)
        if book:
            for key, value in updates.items():
                if key.lower() == "author":
                    book.Author = value
                elif key.lower() == "price":
                    book.Price = float(value)
                elif key.lower() == "quantity":
                    book.Quantity = int(value)
            print(f"Libro actualizado con ISBN: {isbn}")

    def SearchByName(self, name):
        results = []
        self.SearchByNameNode(self._root, name, results)
        return results

    def SearchByNameNode(self, node, name, results):
        for book in node.Books:
            if book.Name.lower() == name.lower():
                results.append(book)
        if not node.IsLeaf:
            for child in node.Children:
                self.SearchByNameNode(child, name, results)

    def SearchByIsbn(self, node, isbn):
        i = 0
        while i < len(node.Books) and isbn > node.Books[i].Isbn:
            i += 1
        if i < len(node.Books) and node.Books[i].Isbn == isbn:
            return node.Books[i]
        if node.IsLeaf:
            return None
        return self.SearchByIsbn(node.Children[i], isbn)

def select_file(file_type):
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de tkinter
    file_path = filedialog.askopenfilename(title=f'Select {file_type} file', filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
    return file_path

def read_books_file(file_path, b_tree):
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            parts = line.strip().split(';')
            if len(parts) < 2:
                print(f"Formato de linea invalido: {line}")
                continue

            operation = parts[0]
            try:
                json_data = json.loads(parts[1])
                print(f"JSON data: {json_data}")  # Imprimir para depurar
            except json.JSONDecodeError:
                print(f"Error convertiendo data JASON: {parts[1]}")
                continue

            if operation == "INSERT":
                try:
                    # Convertir los valores a los tipos adecuados
                    json_data['price'] = float(json_data['price'])
                    json_data['quantity'] = int(json_data['quantity'])

                    # Verificar que json_data contiene todas las claves necesarias
                    required_keys = {'isbn', 'name', 'author', 'price', 'quantity'}
                    if not required_keys.issubset(json_data.keys()):
                        print(f"Error convertiendo data faltan keys para el JASON: {json_data}")
                        continue

                    book = Book(**json_data)
                    b_tree.Insert(book)
                    
                except TypeError as e:
                    print(f"Error insertando el libro: {e}")
                except ValueError as e:
                    print(f"Error convertiendo data: {e}")
            elif operation == "DELETE":
                try:
                    isbn = json_data.get('isbn')
                    if isbn:
                        book_to_delete = Book(isbn, None, None, None, None)
                        b_tree.Delete(book_to_delete.Isbn)
                        
                    else:
                        print(f"Faltan datos ISBN: {json_data}")
                except TypeError as e:
                    print(f"Error borrando el libro: {e}")
                except ValueError as e:
                    print(f"Error convertiendo data: {e}")
            elif operation == "PATCH":
                try:
                    updates = json_data
                    isbn = updates.get('isbn')
                    if not isbn:
                        print(f"Faltan datos ISBN: {updates}")
                        continue

                    if 'price' in updates:
                        updates['price'] = float(updates['price'])
                    if 'quantity' in updates:
                        updates['quantity'] = int(updates['quantity'])

                    b_tree.Update(isbn, updates)
                    
                except TypeError as e:
                    print(f"Error actualizando el libro: {e}")
                except ValueError as e:
                    print(f"Error convertiendo data: {e}")

def read_search_file(file_path, b_tree):
    results = []
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        for line in lines:
            parts = line.strip().split(';')
            operation = parts[0]
            json_data = parts[1]

            if operation == "SEARCH":
                search_params = json.loads(json_data)
                name = search_params.get('name')
                search_results = b_tree.SearchByName(name)
                results.extend(search_results)
    return results

def main():
    b_tree = BTree(3)  # Inicializar Árbol B con grado 3

    books_file = select_file('books')
    if books_file:
        read_books_file(books_file, b_tree)
        print("Libros cargados al arbol B.")

    search_file = select_file('search')
    if search_file:
        results = read_search_file(search_file, b_tree)
        print("Resultados de busqueda ")
        for result in results:
            print(json.dumps(result.__dict__, ensure_ascii=False))  # Imprimir el libro en una sola línea

if __name__ == "__main__":
    main()
