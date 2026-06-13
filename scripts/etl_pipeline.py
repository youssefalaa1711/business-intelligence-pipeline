import pandas as pd
from pathlib import Path

# =====================================================
# EXTRACT
# =====================================================

print("Loading data...")

sales = pd.read_json("data/Sales.json")
forecast = pd.read_json("data/Forecast.json")

print(f"Sales records: {sales.shape}")
print(f"Forecast records: {forecast.shape}")

# =====================================================
# TRANSFORM
# =====================================================

print("Cleaning data...")

# Convert date column
sales["OrderDate"] = pd.to_datetime(sales["OrderDate"])

# Handle missing customer attributes
sales["Name"] = sales["Name"].fillna("Unknown")
sales["Education"] = sales["Education"].fillna("Unknown")
sales["Occupation"] = sales["Occupation"].fillna("Unknown")

# Remove leading/trailing spaces
string_columns = sales.select_dtypes(include="object").columns

for col in string_columns:
    sales[col] = sales[col].str.strip()

# Create Sales Amount
sales["SalesAmount"] = (
    sales["Quantity"] * sales["Net Price"]
)

# =====================================================
# DIMENSION TABLES
# =====================================================

print("Creating dimension tables...")

# -------------------------
# Product Dimension
# -------------------------

dim_product = sales[
    [
        "ProductKey",
        "Product Name",
        "Brand",
        "Color",
        "Subcategory",
        "Category"
    ]
].drop_duplicates()

# -------------------------
# Customer Dimension
# -------------------------

dim_customer = sales[
    [
        "CustomerKey",
        "Customer Code",
        "Name",
        "Education",
        "Occupation"
    ]
].drop_duplicates()

# -------------------------
# Date Dimension
# -------------------------

date_range = pd.date_range(
    sales["OrderDate"].min(),
    sales["OrderDate"].max()
)

dim_date = pd.DataFrame({
    "Date": date_range
})

dim_date["Year"] = dim_date["Date"].dt.year
dim_date["Month"] = dim_date["Date"].dt.month
dim_date["MonthName"] = dim_date["Date"].dt.month_name()
dim_date["Quarter"] = dim_date["Date"].dt.quarter

# =====================================================
# FACT TABLES
# =====================================================

print("Creating fact tables...")

# -------------------------
# Fact Sales
# -------------------------

fact_sales = sales[
    [
        "OrderDate",
        "ProductKey",
        "CustomerKey",
        "CountryRegion",
        "State",
        "City",
        "Quantity",
        "Net Price",
        "SalesAmount"
    ]
]

# -------------------------
# Fact Forecast
# -------------------------

fact_forecast = forecast[
    [
        "CountryRegion",
        "Brand",
        "Forecast",
        "Year"
    ]
]

# =====================================================
# LOAD
# =====================================================

print("Exporting CSV files...")

output_dir = Path("outputs")
output_dir.mkdir(exist_ok=True)

dim_product.to_csv(
    output_dir / "dim_product.csv",
    index=False
)

dim_customer.to_csv(
    output_dir / "dim_customer.csv",
    index=False
)

dim_date.to_csv(
    output_dir / "dim_date.csv",
    index=False
)

fact_sales.to_csv(
    output_dir / "fact_sales.csv",
    index=False
)

fact_forecast.to_csv(
    output_dir / "fact_forecast.csv",
    index=False
)

# =====================================================
# SUMMARY
# =====================================================

print("\nETL Completed Successfully")
print("-" * 50)

print(f"Dim Product : {dim_product.shape}")
print(f"Dim Customer: {dim_customer.shape}")
print(f"Dim Date    : {dim_date.shape}")
print(f"Fact Sales  : {fact_sales.shape}")
print(f"Fact Forecast: {fact_forecast.shape}")

print("\nFiles exported to outputs/")