import streamlit as st
import pandas as pd
import pulp
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Preorder Me", layout="wide")

# --- HEADER ---
st.title("🧦 Preorder Me")
st.markdown("""
**Simplify your sock ordering process!**  
Upload a catalog image, predict demand per size, optimize your order list under your budget, and generate a ready-to-use report. 🚀
""")

# --- FILE UPLOAD ---
st.subheader("📂 Upload your sock catalog image")
uploaded_file = st.file_uploader("Choose an image (PNG, JPG, JPEG)", type=["png","jpg","jpeg"])

if uploaded_file:
    st.info("📷 Image successfully loaded!")
    image = Image.open(uploaded_file)
    st.image(image, caption='Uploaded catalog image', use_column_width=True)

    # --- EXTRACT DATA FROM IMAGE ---
    st.info("⏳ Extracting sock data from the image...")
    import extractor
    socks_df = extractor.extract_socks_data(uploaded_file)
    st.success("✅ Data extraction completed!")
    st.dataframe(socks_df.head())

    # --- BUDGET INPUT ---
    st.subheader("💰 Enter your quarterly budget (PLN)")
    budget = st.number_input("Budget:", min_value=0.0, value=1000.0, step=50.0)

    # --- EXPAND DATAFRAME BY SIZES ---
    sizes = ['KXXL','XXL','XL','L','M','S','XS']
    socks_expanded = pd.DataFrame()
    for _, row in socks_df.iterrows():
        for size in sizes:
            new_row = row.copy()
            new_row['size'] = size
            socks_expanded = pd.concat([socks_expanded, pd.DataFrame([new_row])], ignore_index=True)

    # --- PREDICT QUANTITIES USING ML MODEL ---
    st.info("📈 Predicting order quantities for each sock and size...")
    import ml_model
    socks_expanded = ml_model.predict_order_quantities(socks_expanded)
    st.success("✅ Prediction completed!")
    st.dataframe(socks_expanded.head(12))

    # --- OPTIMIZATION USING PULP ---
    st.info("🧩 Optimizing the order list based on your budget...")
    prob = pulp.LpProblem("Sock_Order_Optimization", pulp.LpMaximize)
    order_vars = {}
    for _, row in socks_expanded.iterrows():
        key = f"{row['product_catalog_number']}_{row['size']}"
        order_vars[key] = pulp.LpVariable(key, lowBound=0, upBound=row['predicted_quantity'], cat='Integer')

    # Objective: maximize revenue
    prob += pulp.lpSum([order_vars[f"{row['product_catalog_number']}_{row['size']}"] * row['price_in_PLN'] 
                        for _, row in socks_expanded.iterrows()])

    # Budget constraint
    prob += pulp.lpSum([order_vars[f"{row['product_catalog_number']}_{row['size']}"] * row['price_in_PLN'] 
                        for _, row in socks_expanded.iterrows()]) <= budget

    # Solve optimization
    prob.solve()

    # Add optimized quantities to dataframe
    socks_expanded['order_quantity'] = socks_expanded.apply(
        lambda row: int(order_vars[f"{row['product_catalog_number']}_{row['size']}"].varValue), axis=1
    )

    # --- DISPLAY ORDER LIST ---
    st.subheader("📝 Optimized Order List")
    st.dataframe(socks_expanded[['type_of_clothing','product_catalog_number','color','size','price_in_PLN','order_quantity']])

    # --- SAVE REPORT TO EXCEL ---
    report_file = "optimized_order_with_sizes.xlsx"
    socks_expanded.to_excel(report_file, index=False)
    st.success(f"💾 Report saved as {report_file}")

    # --- BAR CHART BY COLOR ---
    st.subheader("📊 Total Orders by Color")
    summary = socks_expanded.groupby('color')['order_quantity'].sum().reset_index()
    fig, ax = plt.subplots(figsize=(10,5))
    ax.bar(summary['color'], summary['order_quantity'], color='skyblue')
    ax.set_xlabel("Color")
    ax.set_ylabel("Total Order Quantity")
    ax.set_title("Total Orders by Color")
    plt.xticks(rotation=45)
    st.pyplot(fig)

    # --- HEATMAP: COLOR vs SIZE ---
    st.subheader("🌡️ Order Heatmap by Color and Size")
    heatmap_data = socks_expanded.pivot_table(index='size', columns='color', values='order_quantity', aggfunc='sum')
    fig, ax = plt.subplots(figsize=(12,6))
    sns.heatmap(heatmap_data, annot=True, fmt='d', cmap="YlGnBu", cbar_kws={'label':'Quantity'})
    ax.set_xlabel("Color")
    ax.set_ylabel("Size")
    ax.set_title("Optimized Order Quantity per Size and Color")
    st.pyplot(fig)
