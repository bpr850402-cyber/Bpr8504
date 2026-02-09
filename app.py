import streamlit as st
import pandas as pd
from datetime import date
import os

# ফাইলের নামসমূহ
STOCK_FILE = "shop_stock.csv"
SALES_FILE = "sales_history.csv"

# ডেটা লোড করার ফাংশন
def load_data(file, columns):
    if os.path.exists(file):
        return pd.read_csv(file)
    return pd.DataFrame(columns=columns)

st.set_page_config(page_title="স্মার্ট দোকান", layout="wide")
st.title("📊 দোকানের হিসাব ও লাভ-ক্ষতি খাতা")

# ডেটা লোড করা
df_stock = load_data(STOCK_FILE, ["পণ্য", "স্টক", "কেনা দাম", "বিক্রয় মূল্য"])
df_sales = load_data(SALES_FILE, ["তারিখ", "পণ্য", "পরিমাণ", "মোট বিক্রয়", "মোট লাভ"])

# ট্যাব তৈরি (একটি স্টকের জন্য, একটি বিক্রির জন্য)
tab1, tab2 = st.tabs(["📦 স্টক ও বিক্রি", "📈 সেলস রিপোর্ট"])

with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("নতুন স্টক যোগ")
        name = st.text_input("পণ্যের নাম")
        qty = st.number_input("পরিমাণ", min_value=1)
        buy_p = st.number_input("কেনা দাম (প্রতি পিস)", min_value=0.0)
        sell_p = st.number_input("বিক্রয় মূল্য (প্রতি পিস)", min_value=0.0)
        
        if st.button("স্টক আপডেট করুন"):
            new_data = pd.DataFrame([[name, qty, buy_p, sell_p]], columns=df_stock.columns)
            df_stock = pd.concat([df_stock, new_data], ignore_index=True)
            df_stock.to_csv(STOCK_FILE, index=False)
            st.success("স্টক যোগ হয়েছে!")
            st.rerun()

    with col2:
        st.subheader("🛒 পণ্য বিক্রি করুন")
        if not df_stock.empty:
            item_to_sell = st.selectbox("পণ্য নির্বাচন করুন", df_stock["পণ্য"].tolist())
            s_qty = st.number_input("বিক্রির পরিমাণ", min_value=1)
            
            if st.button("বিক্রি নিশ্চিত করুন"):
                idx = df_stock[df_stock["পণ্য"] == item_to_sell].index[0]
                if df_stock.at[idx, "স্টক"] >= s_qty:
                    # হিসাব নিকেশ
                    total_sell = s_qty * df_stock.at[idx, "বিক্রয় মূল্য"]
                    total_profit = (df_stock.at[idx, "বিক্রয় মূল্য"] - df_stock.at[idx, "কেনা দাম"]) * s_qty
                    
                    # স্টক কমানো
                    df_stock.at[idx, "স্টক"] -= s_qty
                    df_stock.to_csv(STOCK_FILE, index=False)
                    
                    # বিক্রির ইতিহাসে যোগ করা
                    new_sale = pd.DataFrame([[date.today(), item_to_sell, s_qty, total_sell, total_profit]], columns=df_sales.columns)
                    df_sales = pd.concat([df_sales, new_sale], ignore_index=True)
                    df_sales.to_csv(SALES_FILE, index=False)
                    
                    st.balloons()
                    st.success(f"বিক্রি হয়েছে! মোট বিল: {total_sell} টাকা")
                    st.rerun()
                else:
                    st.error("স্টক শেষ!")
        
        st.divider()
        st.write("Current Stock Status:")
        st.table(df_stock)

with tab2:
    st.subheader("📅 আজকের বিক্রয় রিপোর্ট")
    today = str(date.today())
    today_sales = df_sales[df_sales["তারিখ"] == today]
    
    if not today_sales.empty:
        total_revenue = today_sales["মোট বিক্রয়"].sum()
        total_profit_today = today_sales["মোট লাভ"].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("আজকের মোট বিক্রি", f"{total_revenue} টাকা")
        c2.metric("আজকের মোট লাভ", f"{total_profit_today} টাকা")
        
        st.write("আজকের বিক্রির তালিকা:")
        st.dataframe(today_sales)
    else:
        st.info("আজ এখনো কোনো বিক্রি হয়নি।")
      
