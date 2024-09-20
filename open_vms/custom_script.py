


import qrcode
import base64
from io import BytesIO

from PIL import Image
import frappe

# to automate stock transfer from web store to delivery store
# Created By Faruk on 16/08/2024

# NECESSARY PREREQUISITE
#==============================================================================
# Provide user to "Stock User" Roll
#                 "Stock" Module
#                 "User Permission" Allow:company, Permission: [Company Name] 

# Selling > Customer > [Customer Name]
#                       Under Detail > Internal Customer 
#                       Select "Is Internal Customer"
#                       Represents Company: [Company Name]
#                       Under Allowed To Transact With
#                       add [Company Name] in the list


def create_stock_entry(doc, method):
    

    
    try:
          # Check if the Sales Order is placed via the Shopping Cart
        if doc.get("order_type") == "Shopping Cart":
            frappe.log_error(f"Starting stock transfer for Sales Order {doc.name}", "Stock Transfer Debug")
            # Create a new Stock Entry
            stock_entry = frappe.new_doc("Stock Entry")
            stock_entry.stock_entry_type = "Material Transfer"
            stock_entry.from_warehouse = "Web Store - PG"
            stock_entry.to_warehouse = "Delivery Store - PG"
            
            # Specify the Difference AccountStock and Manufacturing 
            stock_entry.difference_account = "Stock Adjustment - PG"  # Accounting > Company > [Company name]> Stock and Manufacturing > Stock Adjustment Account:
            
            # Add items to the Stock Entry
            for item in doc.items:
                frappe.log_error(f"Processing item {item.item_code} with qty {item.qty}", "Stock Transfer Debug")
                stock_entry.append("items", {
                    "item_code": item.item_code,
                    "qty": item.qty,
                    "uom": item.uom,
                    "stock_uom": item.stock_uom,
                    "s_warehouse": stock_entry.from_warehouse,
                    "t_warehouse": stock_entry.to_warehouse
                })

            # Insert and submit the Stock Entry
            stock_entry.insert()
            stock_entry.submit()
            frappe.log_error(f"Stock transfer completed for Sales Order {doc.name}", "Stock Transfer Debug")
            
        else:
             frappe.log_error(f"Skipping stock transfer for non-webshop order {doc.name}", "Stock Transfer")
             
             
    except Exception as e:
        frappe.log_error(message=str(e), title="Stock Entry Creation Failed")
        frappe.throw(_("Stock transfer failed. Please contact support."))


# def enqueue_stock_entry(doc, method):
#     frappe.enqueue('open_vms.custom_script.create_stock_entry', sales_order_name=doc.name)
#----------------------------------------------------------------------------------------------------------------------

# GENERATE QR CODE IN REPORTS
# Open your terminal and navigate to your bench directory:

# cd /path/to/your/bench
# Install the libraries using bench's pip:
# bench pip install qrcode[pil] Pillow

@frappe.whitelist()
def generate_qr_code(data):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode('utf-8')

    return f'data:image/png;base64,{img_str}'