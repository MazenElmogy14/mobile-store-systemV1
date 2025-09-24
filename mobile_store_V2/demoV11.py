from flask import Flask, render_template, request, redirect, url_for, flash
import csv
import os
from datetime import datetime


app = Flask(__name__)
app.secret_key = "your_secret_key"  # Needed for flash messages

# --- File Paths ---
INDIVIDUAL_PHONES_FILE ="phones.csv"
CSV_FILE = "inventory.csv"
FINISHED_FILE = "finished.csv"
SERVICES_FILE = "services.csv"
SOLD_FILE = "sold_phones.csv"
TOTAL_SALES_FILE = "total_sales.csv"

# --- Global Fieldnames ---
FIELDNAMES = ["Brand", "Serial", "Model", "Box", "Charger",
              "Bought Price", "Sell Price", "Category", "Notes", "Quantity",
              "Customer Name", "Customer Number", "Sale Date", "Sale Time", "Service Price"]


INDIVIDUAL_FIELDNAMES = ["Brand", "Serial", "Model", "Box", "Charger", "Bought Price", "Sell Price", "Category", "Notes", "Quantity"]

# Add wrapper functions for the new file




# --- Reusable Load/Save Functions ---
def load_data(file_path):
    """Load data from a given CSV file."""
    if not os.path.exists(file_path):
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()
        return []
    with open(file_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)

def save_data(file_path, data, fieldnames):
    """Save a list of dicts back to a given CSV file."""
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        if data:
            writer.writerows(data)

def load_total_sales():
    if not os.path.exists(TOTAL_SALES_FILE):
        with open(TOTAL_SALES_FILE, "w", newline="", encoding="utf-8") as f:
            f.write("Total Sales\n0.0")
        return 0.0
    with open(TOTAL_SALES_FILE, "r", encoding="utf-8") as f:
        f.readline()
        try:
            return float(f.read())
        except (ValueError, IndexError):
            return 0.0

def save_total_sales(total_sales):
    with open(TOTAL_SALES_FILE, "w", newline="", encoding="utf-8") as f:
        f.write("Total Sales\n" + str(total_sales))

# --- Wrapper functions for specific files ---
def load_inventory():
    return load_data(CSV_FILE)

def save_inventory(phones):
    save_data(CSV_FILE, phones, FIELDNAMES)
    
def load_sold():
    return load_data(SOLD_FILE)

def save_sold(sold_phones):
    save_data(SOLD_FILE, sold_phones, FIELDNAMES)

def load_finished():
    return load_data(FINISHED_FILE)

def save_finished(finished_phones):
    save_data(FINISHED_FILE, finished_phones, FIELDNAMES)

def load_services():
    return load_data(SERVICES_FILE)

def save_services(services):
    save_data(SERVICES_FILE, services, FIELDNAMES)


def load_individual_phones():
    return load_data(INDIVIDUAL_PHONES_FILE)

def save_individual_phones(phones):
    save_data(INDIVIDUAL_PHONES_FILE, phones, INDIVIDUAL_FIELDNAMES)
    
# Ensure the new file is created on startup
if not os.path.exists(INDIVIDUAL_PHONES_FILE):
    save_individual_phones([])



# Ensure all files exist on startup
if not os.path.exists(CSV_FILE):
    save_inventory([])
if not os.path.exists(SOLD_FILE):
    save_sold([])
if not os.path.exists(TOTAL_SALES_FILE):
    save_total_sales(0.0)
if not os.path.exists(FINISHED_FILE):
    save_finished([])
if not os.path.exists(SERVICES_FILE):
    save_services([])

# --- Dynamic Models Helper Function ---
def get_all_brands_and_models():
    phones = load_inventory()
    brands_and_models = {}
    for phone in phones:
        brand = phone.get("Brand", "Unknown")
        model = phone.get("Model", "Unknown")
        if brand not in brands_and_models:
            brands_and_models[brand] = set()
        brands_and_models[brand].add(model)
    # Convert sets back to lists for JSON serialization
    return {brand: sorted(list(models)) for brand, models in brands_and_models.items()}

# --- Routes ---
@app.route("/")
def home():
    return render_template("index.html")

# ------------------- 📦 Inventory -------------------
@app.route("/inventory")
def inventory():
    phones = load_inventory()
    total_quantity = sum(int(p.get("Quantity", 0)) for p in phones)
    return render_template("inventory.html", phones=phones, total_quantity=total_quantity)

# ------------------- ➕ Add Phone -------------------
# ------------------- ➕ Add Phone -------------------
# ------------------- ➕ Add Phone -------------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        # Get data from the form
        brand = request.form["brand"]
        model = request.form["model"].upper()
        box = "Yes" if request.form.get("box") else "No"
        charger = "Yes" if request.form.get("charger") else "No"
        bought_price = request.form["bought_price"]
        sell_price = request.form["sell_price"]
        category = request.form["category"].lower()
        notes = request.form.get("notes", "")
        
        # Get the list of serial numbers submitted by the form
        new_serials = request.form.getlist("serials")
        new_quantity = len(new_serials)

        # Update the main inventory.csv (grouped)
        phones = load_inventory()
        found_phone = None
        for phone in phones:
            if (phone["Brand"] == brand and
                phone["Model"] == model and
                phone["Box"] == box and
                phone["Charger"] == charger and
                phone["Sell Price"] == sell_price):
                found_phone = phone
                break

        if found_phone:
            try:
                current_quantity = int(found_phone.get("Quantity", "0"))
                found_phone["Quantity"] = str(current_quantity + new_quantity)
                flash(f"Quantity for {found_phone['Model']} updated to {found_phone['Quantity']}!", "success")
            except ValueError:
                flash("Error: Invalid quantity value.", "danger")
        else:
            new_phone_data = {
                "Brand": brand,
                "Model": model,
                "Box": box,
                "Charger": charger,
                "Bought Price": bought_price,
                "Sell Price": sell_price,
                "Category": category,
                "Notes": notes,
                "Quantity": str(new_quantity),
                "Serial": "0" # Placeholder for the main inventory view
            }
            phones.append(new_phone_data)
            flash(f"New product ({model}) added successfully!", "success")

        save_inventory(phones)

        # Update the new individual_phones.csv (one entry per serial)
        individual_phones = load_individual_phones()
        for serial in new_serials:
            individual_record = {
                "Brand": brand,
                "Serial": serial,
                "Model": model,
                "Box": box,
                "Charger": charger,
                "Bought Price": bought_price,
                "Sell Price": sell_price,
                "Category": category,
                "Notes": notes,
                "Quantity": "1" # Always 1 for individual records
            }
            individual_phones.append(individual_record)
        
        save_individual_phones(individual_phones)
        
        return redirect(url_for("inventory"))

    brands_and_models = get_all_brands_and_models()
    return render_template("add.html", brands_and_models=brands_and_models)


# ------------------- 💰 Sells Section -------------------
@app.route('/sells')
def sells():
    phones = load_inventory()
    available_phones = [p for p in phones if p.get("Category", "").lower() == "available"]
    search_query = request.args.get('search', '').lower()
    if search_query:
        available_phones = [
            p for p in available_phones
            if p.get("Model", "").lower() == search_query or p.get("Brand", "").lower() == search_query
        ]
    total_available_quantity = sum(int(p.get("Quantity", 0)) for p in available_phones)
    return render_template(
        "sells.html", 
        phones=available_phones, 
        total_available_quantity=total_available_quantity,
        search_query=search_query
    )

# ------------------- ✏ Edit Phone -------------------
@app.route("/edit/<serial>", methods=["GET", "POST"])
def edit(serial):
    phones = load_inventory()
    phone = next((p for p in phones if p["Serial"] == serial), None)
    
    current_list_name = "inventory"

    if not phone:
        services = load_services()
        phone = next((p for p in services if p["Serial"] == serial), None)
        current_list_name = "services"

    if not phone:
        finished = load_finished()
        phone = next((p for p in finished if p["Serial"] == serial), None)
        current_list_name = "finished"

    if not phone:
        flash("Phone not found!", "danger")
        return redirect(url_for("inventory"))
    
    if request.method == "POST":
        for key, value in request.form.items():
            if key in phone:
                phone[key] = value
        
        if "Model" in phone and request.form.get("model"):
            phone["Model"] = request.form.get("model").upper()
        
        new_category = request.form.get("Category", "").lower()

        if new_category == current_list_name:
            if current_list_name == "inventory":
                save_inventory(phones)
            elif current_list_name == "services":
                save_services(services)
            elif current_list_name == "finished":
                save_finished(finished)
        else:
            if current_list_name == "inventory":
                phones = [p for p in phones if p["Serial"] != serial]
                save_inventory(phones)
                target_list = load_inventory()
            elif current_list_name == "services":
                services = [p for p in services if p["Serial"] != serial]
                save_services(services)
                target_list = load_services()
            elif current_list_name == "finished":
                finished = [p for p in finished if p["Serial"] != serial]
                save_finished(finished)
                target_list = load_finished()

            if new_category == "inventory":
                target_list = load_inventory()
                target_list.append(phone)
                save_inventory(target_list)
                flash("Phone moved to Inventory.", "success")
            elif new_category == "service":
                target_list = load_services()
                target_list.append(phone)
                save_services(target_list)
                flash("Phone moved to Service.", "success")
            elif new_category == "finished":
                target_list = load_finished()
                target_list.append(phone)
                save_finished(target_list)
                flash("Phone marked as Finished.", "success")
        
        return redirect(url_for("inventory"))

    return render_template("edit.html", phone=phone)

# ------------------- ❌ Delete Phone -------------------
# ------------------- ❌ Delete Phone -------------------

@app.route("/delete", methods=["POST"])
def delete():
    brand = request.form["brand"]
    model = request.form["model"]
    box = request.form["box"]
    charger = request.form["charger"]
    sell_price = request.form["sell_price"]

    phones = load_inventory()
    phone_to_delete = None

    for phone in phones:
        if (phone["Brand"] == brand and
            phone["Model"] == model and
            phone["Box"] == box and
            phone["Charger"] == charger and
            phone["Sell Price"] == sell_price):
            phone_to_delete = phone
            break

    if phone_to_delete:
        try:
            current_quantity = int(phone_to_delete.get("Quantity", 1))
            if current_quantity > 1:
                phone_to_delete["Quantity"] = str(current_quantity - 1)
                flash(f"One unit of {phone_to_delete['Model']} has been removed.", "success")
            else:
                phones.remove(phone_to_delete)
                flash(f"The last unit of {phone_to_delete['Model']} has been deleted.", "success")
            save_inventory(phones)
        except (ValueError, KeyError):
            flash("Error: Invalid quantity for the selected item.", "danger")
    else:
        flash("Phone not found.", "danger")

    return redirect(url_for("inventory"))


# ------------------- 💵 Sell Product Route -------------------
@app.route("/sell/<serial>", methods=["GET", "POST"])
def sell_product(serial):
    phones = load_inventory()
    phone_to_sell = next((p for p in phones if p["Serial"] == serial), None)

    if not phone_to_sell:
        flash("Product not found!", "danger")
        return redirect(url_for("sells"))
    
    current_time = datetime.now()

    if request.method == "POST":
        customer_name = request.form.get("customer_name")
        customer_number = request.form.get("customer_number")
        sold_serials = request.form.getlist("serials") # This is a list of all serial inputs

        current_quantity = int(phone_to_sell.get("Quantity", 0))
        # This is the core check. It compares the number of submitted serials
        # with the available quantity.
        if len(sold_serials) > current_quantity:
            flash(f"Error: You can only sell up to {current_quantity} of this phone.", "danger")
            return redirect(url_for("sell_product", serial=serial))

        phone_to_sell["Quantity"] = str(current_quantity - len(sold_serials))
        if int(phone_to_sell["Quantity"]) <= 0:
            phones = [p for p in phones if p["Serial"] != serial]
        save_inventory(phones)
        
        sold_phones = load_sold()
        total_sales = load_total_sales()
        
        for sold_serial in sold_serials:
            sold_phone_record = phone_to_sell.copy()
            sold_phone_record.update({
                "Serial": sold_serial,
                "Customer Name": customer_name,
                "Customer Number": customer_number,
                "Sale Date": current_time.strftime("%Y-%m-%d"),
                "Sale Time": current_time.strftime("%H:%M:%S"),
                "Quantity": "1"
            })
            sold_phones.append(sold_phone_record)
            
            try:
                sell_price = float(phone_to_sell.get("Sell Price", 0))
                total_sales += sell_price
            except (ValueError, KeyError):
                pass
        
        save_sold(sold_phones)
        save_total_sales(total_sales)
        
        flash(f"Sale confirmed for {len(sold_serials)} phones to {customer_name}.", "success")
        return redirect(url_for("sells"))

    return render_template("payments.html", phone=phone_to_sell, current_time=current_time.strftime("%Y-%m-%d %H:%M:%S"))


# ------------------- 🔧 Service Section -------------------
@app.route("/service")
def service():
    phones = load_services()
    return render_template("service.html", phones=phones)

# ------------------- ➕ Add Phone to Service -------------------
@app.route("/add_service", methods=["GET", "POST"])
def add_service():
    if request.method == "POST":
        new_service_phone = {
            "Brand": request.form.get("brand", ""),
            "Serial": request.form.get("serial", ""),
            "Model": request.form.get("model", "").upper(),
            "Notes": request.form.get("notes", ""),
            "Customer Name": request.form.get("customer_name", ""),
            "Customer Number": request.form.get("customer_number", ""),
            "Service Price": request.form.get("service_price", ""),
            "Category": "service",
            "Box": "", "Charger": "", "Bought Price": "", "Sell Price": "", 
            "Quantity": "1", "Sale Date": "", "Sale Time": ""
        }
        services = load_services()
        services.append(new_service_phone)
        save_services(services)
        flash(f"Phone ({new_service_phone['Model']}) added to service successfully!", "success")
        return redirect(url_for("service"))
    return render_template("add_service.html")


# ------------------- ✅ Finish Service Route -------------------
@app.route("/finish_service/<serial>", methods=["POST"])
def finish_service(serial):
    services = load_services()
    phone_to_finish = next((p for p in services if p["Serial"] == serial), None)
    if not phone_to_finish:
        flash("Service item not found!", "danger")
        return redirect(url_for("service"))
    services = [p for p in services if p["Serial"] != serial]
    save_services(services)
    finished_phones = load_finished()
    finished_phones.append(phone_to_finish)
    save_finished(finished_phones)
    flash(f"Service for {phone_to_finish['Model']} has been marked as finished.", "success")
    return redirect(url_for("service"))

# ------------------- 🛠 Send to Service Route -------------------
@app.route("/send_to_service", methods=["POST"])
def send_to_service():
    brand = request.form["brand"]
    model = request.form["model"]
    box = request.form["box"]
    charger = request.form["charger"]
    sell_price = request.form["sell_price"]

    inventory_phones = load_inventory()
    phone_to_move = None

    for phone in inventory_phones:
        if (phone["Brand"] == brand and
            phone["Model"] == model and
            phone["Box"] == box and
            phone["Charger"] == charger and
            phone["Sell Price"] == sell_price):
            phone_to_move = phone
            break

    if not phone_to_move:
        flash("Phone not found in inventory!", "danger")
        return redirect(url_for("inventory"))
    
    try:
        current_quantity = int(phone_to_move.get("Quantity", 1))
        if current_quantity > 1:
            phone_to_move["Quantity"] = str(current_quantity - 1)
            # Create a new, single-unit record for the services list
            service_record = phone_to_move.copy()
            service_record['Quantity'] = '1'
            service_record['Category'] = 'service'
            services = load_services()
            services.append(service_record)
            save_services(services)
        else:
            # If it's the last one, move the original record
            inventory_phones.remove(phone_to_move)
            phone_to_move['Category'] = 'service'
            services = load_services()
            services.append(phone_to_move)
            save_services(services)

        save_inventory(inventory_phones)
        flash(f"Phone {phone_to_move['Model']} has been sent to service.", "success")
    
    except (ValueError, KeyError):
        flash("Error processing the selected item.", "danger")

    return redirect(url_for("inventory"))

# ------------------- ✅ Finished Service Section -------------------
@app.route("/finished")
def finished():
    finished_phones = load_finished()
    return render_template("finished.html", phones=finished_phones)


# ------------------- 📦 Move to Inventory Route -------------------
@app.route("/move_to_inventory/<serial>", methods=["POST"])
def move_to_inventory(serial):
    finished_phones = load_finished()
    phone_to_move = next((p for p in finished_phones if p["Serial"] == serial), None)
    if not phone_to_move:
        flash("Finished phone not found!", "danger")
        return redirect(url_for("finished"))
    finished_phones = [p for p in finished_phones if p["Serial"] != serial]
    save_finished(finished_phones)
    phone_to_move['Category'] = 'available'
    inventory_phones = load_inventory()
    inventory_phones.append(phone_to_move)
    save_inventory(inventory_phones)
    flash(f"Phone {phone_to_move['Model']} has been moved back to inventory.", "success")
    return redirect(url_for("finished"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
