import streamlit as st
import pandas as pd
import json
import math

st.set_page_config(layout="wide")

def get_page_range(current_page, total_pages, max_visible=5):
    """Calculate which page numbers to show in pagination"""
    if total_pages <= max_visible:
        return list(range(1, total_pages + 1))
    
    # Always show first and last page
    pages = [1]
    
    # Calculate start and end of visible range
    start = max(2, current_page - 1)
    end = min(total_pages - 1, current_page + 1)
    
    # Add ellipsis if needed
    if start > 2:
        pages.append("...")
    
    # Add middle pages
    for page in range(start, end + 1):
        pages.append(page)
    
    # Add ellipsis if needed
    if end < total_pages - 1:
        pages.append("...")
    
    # Add last page
    if total_pages > 1:
        pages.append(total_pages)
    
    return pages

# Read JSON file using the standard json module first, then convert to DataFrame
with open("matched_horses_1750712894606.json", "r") as f:
    data = json.load(f)

# Flatten nested fields
def flatten_horse(row):
    # Flatten horseDam
    if isinstance(row.get("horseDam"), dict):
        for k, v in row["horseDam"].items():
            row[f"horseDam_{k}"] = v
    # Flatten horseSire
    if isinstance(row.get("horseSire"), dict):
        for k, v in row["horseSire"].items():
            row[f"horseSire_{k}"] = v
    # Flatten trainer
    if isinstance(row.get("trainer"), dict):
        for k, v in row["trainer"].items():
            row[f"trainer_{k}"] = v
    return row

flat_data = [flatten_horse(item) for item in data]

# Convert to DataFrame
df = pd.DataFrame(flat_data)

# Select only the requested columns
selected_columns = [
    'id', 'name', 'age', 'sex', 
    'damHorseName', 'horseDam_id',  # dam name and dam id
    'sireHorseName', 'horseSire_id',  # sire name and sire id
    'trainer_name', 'trainer_id',  # trainer name and trainer id
    'Price', 'careerPrizeMoney', 'rating', 'colour', 'country'
]

# Filter DataFrame to only show selected columns (only if they exist)
available_columns = [col for col in selected_columns if col in df.columns]
df_filtered = df[available_columns]

# Sidebar for search filters
st.sidebar.title("Search Filters")

# Initialize filtered dataframe
df_search = df_filtered.copy()

# Search filters for each field
if 'id' in df_filtered.columns:
    id_search = st.sidebar.text_input("Search by ID", "")
    if id_search:
        df_search = df_search[df_search['id'].astype(str).str.contains(id_search, case=False, na=False)]

if 'name' in df_filtered.columns:
    name_search = st.sidebar.text_input("Search by Horse Name", "")
    if name_search:
        df_search = df_search[df_search['name'].astype(str).str.contains(name_search, case=False, na=False)]

if 'age' in df_filtered.columns:
    age_options = ['All'] + sorted(df_filtered['age'].dropna().unique().tolist())
    age_filter = st.sidebar.selectbox("Filter by Age", age_options)
    if age_filter != 'All':
        
        df_search = df_search[df_search['age'] == age_filter]

if 'sex' in df_filtered.columns:
    sex_options = ['All'] + sorted(df_filtered['sex'].dropna().unique().tolist())
    sex_filter = st.sidebar.selectbox("Filter by Sex", sex_options)
    if sex_filter != 'All':
        df_search = df_search[df_search['sex'] == sex_filter]

if 'damHorseName' in df_filtered.columns:
    dam_search = st.sidebar.text_input("Search by Dam Name", "")
    if dam_search:
        df_search = df_search[df_search['damHorseName'].astype(str).str.contains(dam_search, case=False, na=False)]

if 'sireHorseName' in df_filtered.columns:
    sire_search = st.sidebar.text_input("Search by Sire Name", "")
    if sire_search:
        df_search = df_search[df_search['sireHorseName'].astype(str).str.contains(sire_search, case=False, na=False)]

if 'trainer_name' in df_filtered.columns:
    trainer_search = st.sidebar.text_input("Search by Trainer Name", "")
    if trainer_search:
        df_search = df_search[df_search['trainer_name'].astype(str).str.contains(trainer_search, case=False, na=False)]

if 'colour' in df_filtered.columns:
    colour_options = ['All'] + sorted(df_filtered['colour'].dropna().unique().tolist())
    colour_filter = st.sidebar.selectbox("Filter by Colour", colour_options)
    if colour_filter != 'All':
        df_search = df_search[df_search['colour'] == colour_filter]

if 'country' in df_filtered.columns:
    country_options = ['All'] + sorted(df_filtered['country'].dropna().unique().tolist())
    country_filter = st.sidebar.selectbox("Filter by Country", country_options)
    if country_filter != 'All':
        df_search = df_search[df_search['country'] == country_filter]

# Rating range filter
if 'rating' in df_filtered.columns:
    st.sidebar.subheader("Rating Range")
    min_rating = df_filtered['rating'].min()
    max_rating = df_filtered['rating'].max()
    rating_range = st.sidebar.slider(
        "Select Rating Range",
        min_value=float(min_rating),
        max_value=float(max_rating),
        value=(float(min_rating), float(max_rating))
    )
    df_search = df_search[(df_search['rating'] >= rating_range[0]) & (df_search['rating'] <= rating_range[1])]

# Clear filters button
if st.sidebar.button("Clear All Filters"):
    # Reset pagination when clearing filters
    if 'current_page' in st.session_state:
        del st.session_state.current_page
    st.rerun()

# Display results count
st.sidebar.markdown(f"**Results: {len(df_search)} horses**")

# Main content
st.title("Horse Table")

# Optimized pagination implementation
ITEMS_PER_PAGE = 20
total_items = len(df_search)
total_pages = max(1, math.ceil(total_items / ITEMS_PER_PAGE))

# Initialize current page if not set
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1

# Reset to page 1 if current page is invalid after filtering
if st.session_state.current_page > total_pages:
    st.session_state.current_page = 1

# Calculate start and end indices for current page
start_idx = (st.session_state.current_page - 1) * ITEMS_PER_PAGE
end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)

# Get data for current page
df_current_page = df_search.iloc[start_idx:end_idx]

# Display pagination info
st.write(f"**Showing {start_idx + 1}-{end_idx} of {total_items} horses (Page {st.session_state.current_page} of {total_pages})**")

# Display the dataframe for current page
st.dataframe(df_current_page, height=600, use_container_width=True)

# Optimized pagination controls
if total_pages > 1:
    st.write("---")
    
    # Create a more compact pagination interface
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    
    with col1:
        if st.button("⏮️ First", key="first_page", disabled=st.session_state.current_page == 1):
            st.session_state.current_page = 1
            st.rerun()
    
    with col2:
        if st.button("⬅️ Previous", key="prev_page", disabled=st.session_state.current_page == 1):
            st.session_state.current_page = max(1, st.session_state.current_page - 1)
            st.rerun()
    
    with col3:
        # Smart page number display
        st.write("**Page Navigation:**")
        page_range = get_page_range(st.session_state.current_page, total_pages)
        page_cols = st.columns(len(page_range))
        
        for i, page_num in enumerate(page_range):
            if page_cols[i].button(
                f"{page_num}", 
                key=f"page_{page_num}",
                type="primary" if page_num == st.session_state.current_page else "secondary"
            ):
                st.session_state.current_page = page_num
                st.rerun()
    
    with col4:
        if st.button("Next ➡️", key="next_page", disabled=st.session_state.current_page == total_pages):
            st.session_state.current_page = min(total_pages, st.session_state.current_page + 1)
            st.rerun()
    
    with col5:
        if st.button("Last ⏭️", key="last_page", disabled=st.session_state.current_page == total_pages):
            st.session_state.current_page = total_pages
            st.rerun()
