import tkinter as tk
from tkinter import messagebox

import mysql.connector as c
import pandas.io.sql

con = c.connect(host='localhost', user='root', password='************', database="extra_credit")
cursor = con.cursor(buffered=True)
cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
table_names = [table[0] for table in tables]

query = "SELECT * FROM extra_credit.authors"
cursor.execute(query)
df = pandas.io.sql.read_sql(query, con)
data = df.values.tolist()

auIDs = []
for x in data:
    auIDs.append(x[0])


def edit_action(row):
    # Retrieve the existing row data
    existing_data = data[row - 1]

    # Replace the labels with entry fields for each column in the row
    for col, cell_data in enumerate(existing_data):
        entry = tk.Entry(root, relief=tk.RIDGE, width=25)
        entry.insert(tk.END, cell_data)  # Populate the entry field with existing data
        entry.grid(row=row, column=col, sticky=tk.EW)
        existing_data[col] = entry  # Replace the label with the entry field in the data list

    edit_button.grid_forget()
    # Replace the Edit button with the Update button
    update_button = tk.Button(root, text='Update', command=lambda row=row: update1(row))
    update_button.grid(row=row, column=4, padx=0, pady=5, sticky='W')

    print("Edit button clicked in row", row)


def update1(row):
    # Retrieve the updated row data
    updated_data = [entry.get() if isinstance(entry, tk.Entry) else entry for entry in data[row - 1]]

    # Perform any additional logic here (e.g., update data in the database)
    # ...

    # Update the table with the updated row data
    for col, cell_data in enumerate(updated_data):
        cell_label = tk.Label(root, text=cell_data, relief=tk.RIDGE, width=25)
        cell_label.grid(row=row, column=col, sticky=tk.W)

    # Replace the Update button with the Edit button

    for widget in root.grid_slaves():
        if isinstance(widget, tk.Button) and widget.cget('text') == 'Update':
            widget.grid_forget()

    edit_button = tk.Button(root, text='Edit', command=lambda row=row: edit_action(row), background='green')
    edit_button.grid(row=row, column=4, padx=0, pady=5, sticky='W')

    print("Update button clicked for row", row)


def delete_action(row):
    auID_to_delete = auIDs[row - 1]
    cursor.execute("DELETE FROM extra_credit.authors where auID =%s", (auID_to_delete,))
    con.commit()

    print("Delete button clicked for auID", auIDs[row - 1])

    for widget in root.grid_slaves():
        if int(widget.grid_info()["row"]) == row:
            widget.grid_forget()

        # Update the remaining widgets' row numbers
    for widget in root.grid_slaves():
        current_row = int(widget.grid_info()["row"])
        if current_row > row:
            widget.grid(row=current_row - 1)


root = tk.Tk()
root.title("Authors Table")


# Create the table headers
headers = ['auID', 'aName', 'email', 'phone', 'Actions']
for col, header_text in enumerate(headers):
    header_label = tk.Label(root, text=header_text, relief=tk.RIDGE, width=15, background='cyan')
    header_label.grid(row=0, column=col, pady=5, sticky=tk.EW)
    root.grid_columnconfigure(col, weight=0)


# Create table rows

def add_data():
    new_row = []
    for col in range(len(headers) - 1):  # Exclude the last column (Actions)
        entry = tk.Entry(root, relief=tk.RIDGE, width=25)
        entry.grid(row=len(data) + 1, column=col, sticky=tk.EW)
        new_row.append(entry)

    update_button = tk.Button(root, text='Update', command=lambda row=row: update(row))
    update_button.grid(row=row + 2, column=0)

    cancel_button = tk.Button(root, text='Cancel', command=lambda row=row: cancel(row))
    cancel_button.grid(row=row + 2, column=1)

    def update(row):

        row = len(data) + 1

        # Store the data from the new row
        new_row_data = [entry.get() for entry in new_row]
        # print(new_row_data)

        # Perform any additional logic here (e.g., insert data into the database)
        # ...

        if any(not z for z in new_row_data):
            messagebox.showwarning("Warning", "All columns must be filled")
            return
        else:
            data.append(new_row_data)

        for col, cell_data in enumerate(new_row_data):
            cell_label = tk.Label(root, text=cell_data, relief=tk.RIDGE, width=25)
            cell_label.grid(row=row, column=col, sticky=tk.W)

        print("Update button clicked for row", row)

        # Add the new row data to the existing data list
        insert_query = "INSERT INTO extra_credit.authors (auID, aName, email, phone) VALUES (%s, %s, %s, %s)"
        cursor.execute(insert_query, new_row_data)
        con.commit()

        edit_button = tk.Button(root, text='Edit', command=lambda row=row: edit_action(row), background='green')
        edit_button.grid(row=row, column=4, padx=5, pady=1, sticky='W')

        delete_button = tk.Button(root, text='Delete', command=lambda row=row: delete_action(row), background='red')
        delete_button.grid(row=row, column=4, padx=5, pady=1, sticky='E')

        for widget in root.grid_slaves():
            if widget.grid_info().get("row") == row:
                update_button.grid_forget()
                cancel_button.grid_forget()

        # Update the remaining widgets' row numbers
        for widget in root.grid_slaves():
            current_row = widget.grid_info().get("row")
            if current_row < row:
                add_data_button.grid(row=current_row + 2)

        row = len(data)+1

    def cancel(row):
        for widget in root.grid_slaves():
            if widget.grid_info().get("row") == row:
                update_button.grid_forget()
                cancel_button.grid_forget()

        # Remove the entry fields and labels associated with the new row

        for form in new_row:
            form.destroy()

        print("Cancel button clicked for new row", row)

    # Update the table with the new row


for row, row_data in enumerate(data, start=1):
    for col, cell_data in enumerate(row_data):
        cell_label = tk.Label(root, text=cell_data, relief=tk.RIDGE, width=25, background='white')
        cell_label.grid(row=row, column=col, sticky=tk.EW)

    edit_button = tk.Button(root, text='Edit', command=lambda row=row: edit_action(row), background='green')
    edit_button.grid(row=row, column=4, padx=5, pady=1, sticky='W')

    delete_button = tk.Button(root, text='Delete', command=lambda row=row: delete_action(row), background='red')
    delete_button.grid(row=row, column=4, padx=5, pady=1, sticky='E')

    add_data_button = tk.Button(root, text='Add Data', command=add_data)
    add_data_button.grid(row=len(data) + 2, columnspan=6, padx=5, pady=10)

frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

root.mainloop()
