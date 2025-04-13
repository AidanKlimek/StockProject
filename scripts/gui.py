import tkinter as tk
from tkinter import messagebox
from valuation_final import final_val_exit, final_val_ggm
import yfinance as yf

# Function to get the user input and calculate the valuation
def calculate_valuation():
    # Get user inputs
    ticker = ticker_entry.get()
    base_weight = float(base_weight_entry.get())
    bull_weight = float(bull_weight_entry.get())
    bear_weight = float(bear_weight_entry.get())

    # Call the valuation functions
    try:
        # Use Exit Multiple or GGM as needed
        exit_upside, exit_msg = final_val_exit(ticker, base_weight, bull_weight, bear_weight)
        ggm_upside, ggm_msg = final_val_ggm(ticker, base_weight, bull_weight, bear_weight)

        result_label.config(
            text=(
                f"Upside (Comps & Exit): {exit_upside:.2f}%\n"
                f"Upside (Comps & GGM): {ggm_upside:.2f}%\n"
                f"{exit_msg if exit_msg else ''}\n"
            )
        )
    except Exception as e:
        # Handle errors
        messagebox.showerror("Error", f"An error occurred: {e}")

# Create the main window
root = tk.Tk()
root.title("Stock Valuation")

# Create and place widgets in the window
ticker_label = tk.Label(root, text="Stock Ticker:")
ticker_label.pack()

ticker_entry = tk.Entry(root)
ticker_entry.pack()

base_weight_label = tk.Label(root, text="Base Weight:")
base_weight_label.pack()

base_weight_entry = tk.Entry(root)
base_weight_entry.pack()

bull_weight_label = tk.Label(root, text="Upside Weight:")
bull_weight_label.pack()

bull_weight_entry = tk.Entry(root)
bull_weight_entry.pack()

bear_weight_label = tk.Label(root, text="Downside Weight:")
bear_weight_label.pack()

bear_weight_entry = tk.Entry(root)
bear_weight_entry.pack()

calculate_button = tk.Button(root, text="Calculate Valuation", command=calculate_valuation)
calculate_button.pack()

result_label = tk.Label(root, text="Results will appear here")
result_label.pack()

# Run the application
root.mainloop()

