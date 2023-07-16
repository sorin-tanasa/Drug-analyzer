#!/usr/bin/env python
# coding: utf-8

# In[18]:


import requests
from pandas import DataFrame,ExcelWriter,read_csv

# Defining functions to analyze data
def classifier(value):
    """1. Function: classifier(value)
    - Description: Converts a given value to an integer or float if possible, or returns it as is.
    - Parameters:
        - value: The value to be converted.
    - Returns: The converted value (integer or float if conversion is successful, or the original value if not).
    """
    try:
        # Try converting the value to an integer
        return int(value)
    except ValueError:
        try:
            # Try converting the value to a float
            return float(value)
        except ValueError:
            # The value is not a number, return it as is
            return value

def propertizer(comp_list,prop_list):
    """2. Function: propertizer(comp_list, prop_list)
    - Description: Retrieves specific properties of compounds using their names from PubChem 
      database and populates a table with the retrieved data. Checks each feature to assign
      it to its respective data type (int, float, string).
    - Parameters:
        - comp_list: A list of compound names.
        - prop_list: A list of property names to retrieve for each compound.
    - Returns: None."""
    
    base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    for compound in compound_list:
        row=[compound]
        for prop in prop_list:
            search_url = f"{base_url}/compound/name/{compound}/property/{prop}/JSON"
            response = requests.get(search_url)
            if response.status_code == 200:
                # Request was successful
                data = response.json()
                prop_value = data["PropertyTable"]["Properties"][0][prop]
                if prop=="Title":
                    print(compound,":", prop_value.upper())
                    row.append(prop_value.upper())
                else:
                    try:
                        row.append(classifier(prop_value))
                    except:
                        print(prop_value," not found")
                        row.append("")
            else:
                # Request failed
                print("Request failed with status code:", response.status_code)
        table_data.append(row)

def ranker(df):
    """
    3. Function: ranker(df)
    - Description: Ranks compounds based on specific criteria and returns a DataFrame with the 
      ranked results.
    - Parameters:
        - df: The input DataFrame containing compound data.
    - Returns: A DataFrame with compounds ranked based on specific criteria.
    """
    criteria = {
        'TPSA': (0, 140),
        'XLogP': (1, 5),
        'MolecularWeight': (0, 500),
        'HBondAcceptorCount': (0, 10),
        'HBondDonorCount': (0, 5)
    }

    # Create a new DataFrame with the initial 5 criteria
    ranked_df = df[['Compound','Normalized name', 'TPSA', 'XLogP', 'MolecularWeight', 'HBondAcceptorCount', 'HBondDonorCount']].copy()

    # Calculate the score for each compound based on the criteria
    for feature, criterion in criteria.items():
        score_column = feature + ' Score'
        ranked_df[score_column] = (df[feature] - criterion[0]) / (criterion[1] - criterion[0])
        
    ranked_df=ranked_df.sort_index(axis=1)

    # Calculate the total score for each compound
    ranked_df['Total Score'] = ranked_df[[feature + ' Score' for feature in criteria]].sum(axis=1)

    # Assign ranks to the compounds based on their total score
    ranked_df['Rank'] = ranked_df['Total Score'].rank(ascending=False, method='dense').astype(int)

    # Sort the DataFrame by rank in ascending order
    ranked_df = ranked_df.sort_values(by='Rank', ascending=True)

    return ranked_df


"""4. Main Code Execution:
    - Dictates properties to be extracted from the Pubchem REST API named PUG.
    -Extracts the list of compounds from a file named "compounds.csv"
    - Creates an empty table with column names ["Compound", "Normalized name"].
    - Executes the propertizer() function to retrieve specific properties of compounds and 
      populate the table.
    - Executes the ranker() function to rank the compounds based on specific criteria.
    - Prints the ranked DataFrame.
"""

property_list=["Title","MolecularFormula","MolecularWeight","CanonicalSMILES","IsomericSMILES",
           "InChI","InChIKey","IUPACName","XLogP","ExactMass","MonoisotopicMass","TPSA",
           "Complexity","Charge","HBondDonorCount","HBondAcceptorCount","RotatableBondCount",]
compound_list=DataFrame(read_csv("compounds.csv"))["Compound"].values.tolist()

data=["Compound", "Normalized name"]
table_data=[data+property_list[1:]]

#Functions calling
propertizer(compound_list,property_list)
data=DataFrame(table_data[1:], columns=table_data[0])
finaldf=ranker(data)
print(finaldf)

# Writing data to file
with ExcelWriter("results.xlsx") as writer:
    data.to_excel(writer, sheet_name='Drug features table')
    finaldf.to_excel(writer, sheet_name='Ranking table')


# In[4]:




