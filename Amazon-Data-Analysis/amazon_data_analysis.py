#!/usr/bin/python3

import os
import signal
import time
import pandas as pd

from colorama import Fore
from rich.table import Table
from rich.console import Console
from rich.columns import Columns
from rich.layout import Layout

# Colores
color_verde = Fore.GREEN
color_rojo = Fore.RED
color_yellow = Fore.YELLOW

def def_handler(sig, frame):
    print(color_rojo + "\n\n[!]Saliendo...\n")
    exit(0)

# Ctrl + C
signal.signal(signal.SIGINT, def_handler)


# Load csv data
def load_data():
    default_filename = 'Retail.OrderHistory.2.csv'
    filename = default_filename
    if not os.path.isfile(filename):
        path = input(color_rojo + "\n\n[!] No se pudo encontrar el archivo en el directorio actual. Por favor, introduce la ruta del directorio donde se encuentra el archivo: ")
        filename = os.path.join(path, default_filename)
    while not os.path.isfile(filename):
        print(color_rojo + "\n\n[!] No se pudo encontrar el archivo %s en el directorio proporcionado.\n" % filename)
        path = input(color_yellow + "Por favor, introduce la ruta correcta del directorio: ")
        filename = os.path.join(path, default_filename)
    try:
        df = pd.read_csv(filename)
        df = df.fillna(0)
        print(color_verde + "\n\n[+] Archivo cargado con éxito. Mostrando tabla....\n")
        time.sleep(2)
        return df
    except Exception as e:
        print(color_rojo +f"Ocurrió un error al leer el archivo: {e}")



# Diferent functions
def calculate_highest_spending_month(df):
    # Convert the Order Date column to datetime format
    df['Order Date'] = pd.to_datetime(df['Order Date'])

    # Extract year and month from 'Order Date'
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month

    # Group by year and month, and calculate the sum of Unit Price
    spending = df.groupby(['Year', 'Month'])['Unit Price'].sum()

    # Find the year and month with the highest spending
    highest_spending_month = spending.idxmax()

    return highest_spending_month


def calculate_products_per_provider(df):
    
    df['Carrier Name & Tracking Number'] = df['Carrier Name & Tracking Number'].astype(str)
    products_per_provider = df.groupby('Carrier Name & Tracking Number')['Order ID'].count()

    return products_per_provider

def calculate_products_per_payment(df):

    df['Payment Instrument Type'] = df['Payment Instrument Type'].astype(str)
    products_per_payment = df.groupby('Payment Instrument Type')['Order ID'].count()

    return products_per_payment

# Tables

# Main Table
def create_table(df):
    # Variables
    product_name = df["Product Name"]
    total_products = len(product_name)
    unit_price = df["Unit Price"]
    order_id = df["Order ID"]
    order_date = df["Order Date"]

    table = Table()
    table.add_column("Product Name", justify="left", style="purple")
    table.add_column("Order Date", justify="center", style="blue")
    table.add_column("Order ID", justify="center", style="yellow")
    table.add_column("Unit Price (€)",justify="center", style="green")

    for row in range(total_products):
        table.add_row(f"{product_name[row]}",f"{order_date[row]}",f"{order_id[row]}", f"{unit_price[row]:.2f}")
        table.add_row("","")
    
    return table

    

# Resume Table
def create_resume_table(df):
    # Variables
    unit_price = df["Unit Price"]
    product_name = df["Product Name"]
    
    total_price = sum(unit_price)
    most_expensive_product = product_name[unit_price.idxmax()]
    most_expensive_price = unit_price.max()
    cheapest_product = product_name[unit_price.idxmin()]
    cheapest_price = unit_price.min()
    highest_spending_month = calculate_highest_spending_month(df)
    
    
    # Número total de pedidos
    total_orders = len(df['Order ID'].unique())
    # Número total de productos
    total_products = df['Quantity'].sum()
    

    table_resume = Table()
    table_resume.add_column("Resume", justify="left", style="red")
    table_resume.add_column("Data", justify="center", style="green")

    table_resume.add_row(f"Total Spent", f"{total_price:.2f}€")
    table_resume.add_row("Total Products", str(total_products))
    table_resume.add_row("Total Orders", str(total_orders))
    table_resume.add_row(f"Highest Year and Month Spent", f"{highest_spending_month}")
    table_resume.add_row(f"Most Expensive Product: [cyan]{most_expensive_product}", f"{most_expensive_price:.2f}")
    table_resume.add_row(f"Cheapest Product: [cyan]{cheapest_product}", f"{cheapest_price:.2f}")

    return table_resume

# Providers Table
def create_table_providers(df):

    products_per_provider = calculate_products_per_provider(df)

    table_providers = Table()
    table_providers.add_column("Providers", justify="left", style="purple")
    table_providers.add_column("Num Products", justify="center", style="yellow") 

    for provider, num_products in products_per_provider.items():
        table_providers.add_row(f"[purple]{provider}", str(num_products))  

    return table_providers


# Payments Table
def create_table_payments(df):

    products_per_payment = calculate_products_per_payment(df)

    table_payments = Table()
    table_payments.add_column("Payment", justify="left", style="purple")
    table_payments.add_column("Num Products", justify="center", style="yellow") 

    for payment, num_products in products_per_payment.items():
        table_payments.add_row(f"[purple]{payment}", str(num_products))

    return table_payments


if __name__ == "__main__":

    df = load_data()

    table = create_table(df)
    provider_table = create_table_providers(df)
    payment_table = create_table_payments(df)
    resume_table = create_resume_table(df)

    tables = [provider_table, payment_table]
    console = Console()
    layout = Layout()

    console.print(table)
    print("\n")

    columns = Columns(tables)
    console.print(columns)

    print("\n")
    console.print(resume_table)
    
    