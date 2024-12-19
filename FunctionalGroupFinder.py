import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import io

st.markdown('# Functional group finder')

# Select whether we are doing XANES or IR
SpectrumType = st.sidebar.radio('Spectral type', ['IR','XANES'])


if SpectrumType == 'XANES':
    Groups = pd.read_csv('XANESFunctionalGroups.csv', index_col=0).sort_values('min eV')
    SpectrumUnit = 'eV'
    # A default spectrum in case the user doesn't load one.
    S = pd.DataFrame()
    S[SpectrumUnit] = np.linspace(250,1000,10000)
    S['I'] = np.zeros(len(S[SpectrumUnit]))
    MinimumFeatureWidth = 0.5
else:
    Groups = pd.read_csv('IRFunctionalGroups.csv', index_col=0).sort_values('min cm-1')
    SpectrumUnit = 'cm-1'
    # A default spectrum in case the user doesn't load one.
    S = pd.DataFrame()
    S[SpectrumUnit] = range(0,4000,4)
    S['I'] = np.zeros(len(S[SpectrumUnit]))
    MinimumFeatureWidth = 10.0

SpectrumMin = Groups[f'min {SpectrumUnit}'].astype(float).min()
SpectrumMax = Groups[f'max {SpectrumUnit}'].astype(float).max()
st.markdown('### List of all functional groups.')
st.write(Groups)

ShowGroups = st.sidebar.multiselect('Select Functional Groups by bond (up to 5)', np.sort(Groups['Group'].unique()))

ShowNames = st.sidebar.multiselect('Select Functional Groups by description (up to 5)', np.sort(Groups['Name'].unique()))

ColorList = ['red', 'green', 'orange', 'purple', 'gray']

SearchAround = st.sidebar.number_input(f'Search around {SpectrumUnit}:', value=10.0)
SearchWidth = st.sidebar.number_input(f'Search plus minus {SpectrumUnit}:', 0.0, (SpectrumMax+SpectrumMin)/10, 10.0, (SpectrumMax-SpectrumMin)/1000)
# SearchAround = st.sidebar.slider(f'Search around {SpectrumUnit}:', SpectrumMin, SpectrumMax, (SpectrumMax+SpectrumMin)/2, (SpectrumMax-SpectrumMin)/10000)
# SearchWidth = st.sidebar.slider(f'Search plus minus {SpectrumUnit}:', 0.0, (SpectrumMax+SpectrumMin)/10, 10.0, (SpectrumMax-SpectrumMin)/1000)

SearchForGroups = Groups[Groups[f'min {SpectrumUnit}'] < SearchAround+SearchWidth]
SearchForGroups = SearchForGroups[SearchForGroups[f'max {SpectrumUnit}'] > SearchAround-SearchWidth]
st.markdown(f'### Functional groups between {SearchAround-SearchWidth} and {SearchAround+SearchWidth} {SpectrumUnit}')
st.write(SearchForGroups)

# We can show multiple spectra, but we need to keep them in a list.
SpectrumDict = {} 
# Option to add a spectrum.
#st.set_option('deprecation.showfileUploaderEncoding', False)
SpectrumFiles = st.file_uploader(f'Choose a spectrum file(s) in csv two-column format: ({SpectrumUnit}, intensity [between 0 and 1]):', accept_multiple_files=True)
if SpectrumFiles is not None:
    for SpectrumFile in SpectrumFiles:
        try:
            SpectrumDict[SpectrumFile.name] = pd.read_csv(SpectrumFile, delim_whitespace=True)
        except IndexError:
            st.write('Not comma delimited.')

# If there is no spectrum, and the user isn't adding one, then we have to have a default (empty) spectrum so we can still show functional group positions in the plot.
if (len(SpectrumDict) == 0):
    st.write('Loading default spectrum.')
    SpectrumDict['Default'] = S

fig = go.Figure(layout_title_text='Experimental Spectrum')
for label,S in SpectrumDict.items():
    x,y = S.iloc[:,0], S.iloc[:,1]
    fig.add_trace(go.Line(x=x, y=y, name=label))
if len(ShowGroups) > 0:
    for i, g in enumerate(ShowGroups):
        Records = Groups[Groups['Group'] == g]
        r_x = []
        r_y = []
        for j,r in Records.iterrows():
            if r[f'min {SpectrumUnit}'] == r[f'max {SpectrumUnit}']:
                r_x.append(r[f'min {SpectrumUnit}']-MinimumFeatureWidth)
                r_x.append(r[f'min {SpectrumUnit}']+MinimumFeatureWidth)
                r_x.append(None)
                r_y.append(y.max()-1-i/10)
                r_y.append(y.max()-1-i/10)
                r_y.append(None)
            else:
                r_x.append(r[f'min {SpectrumUnit}'])
                r_x.append(r[f'max {SpectrumUnit}'])
                r_x.append(None)
                r_y.append(y.max()-1-i/10)
                r_y.append(y.max()-1-i/10)
                r_y.append(None)
        fig.add_trace(go.Line(x=r_x, y=r_y, name=f'{r["Group"]}', mode='lines', line=dict(color=ColorList[i%len(ColorList)], width=5)))
if len(ShowNames) > 0:
    for i, g in enumerate(ShowNames):
        Records = Groups[Groups['Name'] == g]
        r_x = []
        r_y = []
        for j,r in Records.iterrows():
            if r[f'min {SpectrumUnit}'] == r[f'max {SpectrumUnit}']:
                r_x.append(r[f'min {SpectrumUnit}']-10)
                r_x.append(r[f'min {SpectrumUnit}']+10)
                r_x.append(None)
                r_y.append(y.max()-1-i/10)
                r_y.append(y.max()-1-i/10)
                r_y.append(None)
            else:
                r_x.append(r[f'min {SpectrumUnit}'])
                r_x.append(r[f'max {SpectrumUnit}'])
                r_x.append(None)
                r_y.append(y.max()-1-i/10)
                r_y.append(y.max()-1-i/10)
                r_y.append(None)
        fig.add_trace(go.Line(x=r_x, y=r_y, name=f'{r["Name"]}', mode='lines', line=dict(color=ColorList[i%len(ColorList)], width=5)))

st.write(fig)
