import tkinter as tk
from tkinter import filedialog
import json

class Book:
    def __init__(self, isbn, name, author, category, price, quantity):
        self.Isbn = isbn
        self.Name = name
        self.Author = author
        self.Category = category
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

def format_book_output(book):
    return json.dumps({
        "isbn": book.Isbn,
        "name": book.Name,
        "author": book.Author,
        "category": book.Category if book.Category else "null",  # Maneja nulos
        "price": f"{book.Price:.2f}" if book.Price is not None else "null",  # Maneja nulos para precio
        "quantity": book.Quantity if book.Quantity is not None else "null"  # Maneja nulos para cantidad
    }, ensure_ascii=False)

def write_output_to_file(results, output_file):
    with open(output_file, 'w', encoding='utf-8') as file:
        for result in results:
            formatted_output = format_book_output(result)
            file.write(formatted_output + "\n")
    print(f"Archivo de salida generado: {output_file}")

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
                print(f"Formato de línea inválido: {line}")
                continue

            operation = parts[0]
            try:
                json_data = json.loads(parts[1])
            except json.JSONDecodeError:
                print(f"Error convirtiendo data JSON: {parts[1]}")
                continue

            if operation == "INSERT":
                try:
                    # Asignar valores por defecto (None) si faltan claves en el JSON
                    isbn = json_data.get('isbn', None)
                    name = json_data.get('name', None)
                    author = json_data.get('author', None)
                    category = json_data.get('category', None)
                    price = float(json_data['price']) if 'price' in json_data else None
                    quantity = int(json_data['quantity']) if 'quantity' in json_data else None

                    # Crear el libro con valores nulos en caso de faltar claves
                    book = Book(isbn, name, author, category, price, quantity)
                    b_tree.Insert(book)

                except (TypeError, ValueError) as e:
                    print(f"Error insertando el libro: {e}")

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

    write_output_to_file(results, "resultados_busqueda.txt")
    return results

def main():
    b_tree = BTree(3)  # Inicializar Árbol B con grado 3

    # Seleccionar archivo de libros
    books_file = select_file('books')
    if books_file:
        read_books_file(books_file, b_tree)
        print("Libros cargados al árbol B.")

    # Seleccionar archivo de búsqueda
    search_file = select_file('search')
    if search_file:
        results = read_search_file(search_file, b_tree)
        print("Resultados de búsqueda:")
        for result in results:
            print(json.dumps(result.__dict__, ensure_ascii=False))  # Imprimir libro en una línea

if __name__ == "__main__":
    main()
