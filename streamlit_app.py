import streamlit as st
import pandas as pd
import re
from xml.etree.ElementTree import Element, SubElement, ElementTree
from io import BytesIO

st.title("Fixture Library XML Generator")

st.markdown("""
This app allows you to:
1. Download a blank CSV template
2. Upload a filled CSV to generate a `fixtureLibrary.xml` file
""")

# Step 1: Downloadable empty CSV template
columns = ["Fixture Type", "Qty Type", "Source Type", "Description", "Wattage"]
empty_df = pd.DataFrame(columns=columns)

csv_bytes = empty_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Download CSV Template",
    data=csv_bytes,
    file_name="fixtureLibrary_template.csv",
    mime="text/csv"
)

# Step 2: Upload CSV to generate XML
uploaded_file = st.file_uploader("Upload filled CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)

    # Validate columns
    expected_columns = set(columns)
    if not expected_columns.issubset(df.columns):
        st.error("❌ Uploaded file is missing required columns.")
    else:
        # Clean the text
        def clean_text(text, allow_hyphen=False):
            if pd.isna(text):
                return ""
            pattern = r'[^A-Za-z0-9\- ]+' if allow_hyphen else r'[^A-Za-z0-9 ]+'
            return re.sub(pattern, '', str(text)).strip()

        df["Fixture Type"] = df["Fixture Type"].apply(lambda x: clean_text(x, allow_hyphen=True))
        for col in df.columns:
            if col != "Fixture Type":
                df[col] = df[col].apply(lambda x: clean_text(x))

        # Build XML from template
        fixture_library = Element("fixtureLibrary")

        for index, row in df.iterrows():
            fixture = SubElement(fixture_library, "fixture")

            SubElement(fixture, "listPosition").text = str(index + 1)
            SubElement(fixture, "fixtureUseType").text = "FIXTURE_USE_LIBRARY"
            SubElement(fixture, "lampWattage").text = "0.000"
            SubElement(fixture, "powerAdjustmentFactor").text = "0.000"
            SubElement(fixture, "pafDesc").text = "None"
            SubElement(fixture, "lightingType").text = "LED"
            SubElement(fixture, "description").text = row.get("Description", "")
            SubElement(fixture, "lampBallastDescription").text = ""
            SubElement(fixture, "lampType").text = "LED " + row.get("Wattage", "")
            SubElement(fixture, "ballast").text = "UNSPECIFIED_BALLAST"
            SubElement(fixture, "fixtureType").text = row.get("Fixture Type", "")
            SubElement(fixture, "typeOfFixture").text = ""
            SubElement(fixture, "numberOfLamps").text = "1"
            SubElement(fixture, "fixtureWattage").text = re.sub(r'\D', '', row.get("Wattage", "0"))
            SubElement(fixture, "trackLightingWattageBasis").text = "WATTAGE_BASIS_NOT_SET"
            SubElement(fixture, "trackTotalLuminaireWattage").text = "0"
            SubElement(fixture, "trackLength").text = "0"
            SubElement(fixture, "trackCircuitBreakerAmps").text = "0"
            SubElement(fixture, "trackCircuitBreakerVolts").text = "0"
            SubElement(fixture, "trackCurrentLimiterWattage").text = "0"
            SubElement(fixture, "trackTransformerWattage").text = "0"

        # Convert to XML string in memory
        xml_bytes = BytesIO()
        tree = ElementTree(fixture_library)
        tree.write(xml_bytes, encoding='utf-8', xml_declaration=True)
        st.download_button(
            label="📤 Download fixtureLibrary.xml",
            data=xml_bytes.getvalue(),
            file_name="fixtureLibrary.xml",
            mime="application/xml"
        )
