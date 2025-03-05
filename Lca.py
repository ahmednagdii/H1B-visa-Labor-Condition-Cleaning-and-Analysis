import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout='wide')

st.markdown("<h1 style='text-align: center;'>H1B LCA Disclosure Data (2020-2024)</h1>", unsafe_allow_html=True)

df = pd.read_csv("sample_data.csv")

df['RECEIVED_DATE'] = pd.to_datetime(df['RECEIVED_DATE'], errors='coerce')

min_year = max(2019, int(df['RECEIVED_DATE'].dt.year.min()))  
max_year = int(df['RECEIVED_DATE'].dt.year.max())
year_options = list(range(min_year, max_year+1)) + ['All Years']

selected_year = st.sidebar.selectbox("Select Year", year_options, index=year_options.index('All Years') if 'All Years' in year_options else 0)

if selected_year != 'All Years':
    df_filtered = df[df['RECEIVED_DATE'].dt.year == int(selected_year)]
else:
    df_filtered = df.copy()

pages = ["H1B Overview", "Job Analysis", "WorkSite Analysis", "Employer Analysis", "Agent Analysis", "Court Analysis"]

# ------------------ Page 1: H1B Overview ------------------
def page1():
    st.markdown("### H1B Overview", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    
    with col1:
        # Frequency by Year (using filtered data)
        df_freq = df_filtered['RECEIVED_DATE'].dt.year.value_counts().reset_index()
        df_freq.columns = ['YEAR', 'FREQ']
        df_freq = df_freq[df_freq['YEAR'] > 2018]
        df_freq = df_freq.sort_values('YEAR')
        fig = px.bar(
            data_frame=df_freq,
            x='YEAR',
            y='FREQ',
            title="Frequency of Received Dates by Year",
            labels={'YEAR': 'Year', 'FREQ': 'Frequency'},
            text_auto=True
        )
        st.plotly_chart(fig)
        
        # Number of Applications per Visa Type
        visa_counts = df_filtered.groupby('VISA_CLASS').size().reset_index(name='Count')
        fig4 = px.bar(
            visa_counts,
            x='VISA_CLASS', y='Count',
            title="Number of Applications per Visa Type",
            text_auto=True
        )
        st.plotly_chart(fig4)
    
    with col2:
        # Quarter Decision Distribution
        quarter_decision_counts = df_filtered['Quarter Decision'].value_counts()
        fig2 = px.histogram(
            x=quarter_decision_counts.index,
            y=quarter_decision_counts.values,
            text_auto=True,
            labels={'x': 'Quarter Decision', 'y': 'Count'},
            title='Distribution of Quarter Decision'
        )
        st.plotly_chart(fig2)
        
        # Number of Approved and Denied Applications per Year
        df_filtered['Year'] = df_filtered['RECEIVED_DATE'].dt.year
        status_counts = df_filtered.groupby(['Year', 'CASE_STATUS']).size().reset_index(name='Count')
        fig3 = px.bar(
            status_counts,
            x='Year',
            y='Count',
            color='CASE_STATUS',
            barmode='group',
            title="Number of Approved and Denied Applications per Year",
            labels={'CASE_STATUS': 'Application Status', 'Count': 'Number of Applications', 'Year': 'Year'}
        )
        st.plotly_chart(fig3)

# ------------------ Page 2: Job Analysis ------------------
def page2():
    st.markdown("### Job Analysis", unsafe_allow_html=True)
    # نستخدم البيانات المفلترة
    df_job = df_filtered.copy()
    df_job['BEGIN_DATE'] = pd.to_datetime(df_job['BEGIN_DATE'], errors='coerce')
    df_job['END_DATE'] = pd.to_datetime(df_job['END_DATE'], errors='coerce')
    df_job['Duration'] = ((df_job['END_DATE'] - df_job['BEGIN_DATE']).dt.days / 365).astype(int)
    
    # Employment Duration Distribution
    duration_counts = df_job['Duration'].value_counts().sort_index()
    fig_duration = px.bar(
        x=duration_counts.index,
        y=duration_counts.values,
        labels={'x': 'Employment Duration (Years)', 'y': 'Number of Jobs'},
        title="Distribution of Employment Duration",
        text_auto=True
    )
    st.plotly_chart(fig_duration)
    
    # Job Title Analysis: Top 5 Job Titles by Frequency
    sub_df = df_job['JOB_TITLE'].value_counts(ascending=False).head(5).reset_index()
    sub_df.columns = ['JOB_TITLE', 'Counts']
    fig = px.bar(sub_df, y='JOB_TITLE', x='Counts', title="Top 5 Job Titles by Frequency")
    st.plotly_chart(fig)
    
    # Full-Time vs Part-Time Positions Distribution
    counts = df_job['FULL_TIME_POSITION'].value_counts().reset_index()
    counts.columns = ['FULL_TIME_POSITION', 'Count']
    fig2 = px.pie(counts, names='FULL_TIME_POSITION', values='Count', title="Distribution of Full-Time vs Part-Time Positions")
    st.plotly_chart(fig2)
    
    # SOC Titles Analysis: Top 5 Most Frequent SOC Titles
    top_soc_titles = df_job['SOC_TITLE'].value_counts().head(5).reset_index()
    top_soc_titles.columns = ['SOC_TITLE', 'Count']
    fig3 = px.bar(top_soc_titles, y='SOC_TITLE', x='Count', title="Top 5 Most Frequent SOC Titles")
    st.plotly_chart(fig3)
    
    # Average Wage Analysis
    st.markdown("#### Average Wages Analysis", unsafe_allow_html=True)
    avg_wage_by_job = df_job.groupby(['JOB_TITLE'])['PREVAILING_WAGE'].mean().reset_index()
    avg_wage_by_job_sorted = avg_wage_by_job.sort_values(by='PREVAILING_WAGE', ascending=False).head(5)
    fig4 = px.bar(avg_wage_by_job_sorted, x='PREVAILING_WAGE', y='JOB_TITLE', title="Top 5 Jobs with Highest Average Wages")
    st.plotly_chart(fig4)
    
    avg_wage_by_unit = df_job.groupby('PW_UNIT_OF_PAY')['PREVAILING_WAGE'].mean().reset_index()
    avg_wage_by_unit['PREVAILING_WAGE'] = avg_wage_by_unit['PREVAILING_WAGE'].round(2)
    fig5 = go.Figure(data=[go.Table(
        header=dict(values=["PW_UNIT_OF_PAY", "Average Prevailing Wage"],
                    fill_color='paleturquoise', align='left'),
        cells=dict(values=[avg_wage_by_unit['PW_UNIT_OF_PAY'].tolist(), avg_wage_by_unit['PREVAILING_WAGE'].tolist()],
                   fill_color='lavender', align='left'))
    ])
    st.plotly_chart(fig5)
    
    # Wage Unit by Job Analysis
    if 'WAGE_UNIT_OF_PAY' in df_job.columns:
        wage_unit_by_job = df_job.groupby(['JOB_TITLE', 'WAGE_UNIT_OF_PAY'])['PREVAILING_WAGE'].max().reset_index()
        wage_unit_by_job = wage_unit_by_job.sort_values(by='PREVAILING_WAGE', ascending=False).head(10)
        fig6 = px.bar(wage_unit_by_job, x="JOB_TITLE", y="PREVAILING_WAGE", color="WAGE_UNIT_OF_PAY",
                      title="Average Prevailing Wage by Job Title and Wage Unit",
                      labels={'JOB_TITLE': 'Job Title', 'PREVAILING_WAGE': 'Average Prevailing Wage', 'WAGE_UNIT_OF_PAY': 'Wage Unit'})
        st.plotly_chart(fig6)
    else:
        st.warning("Column 'WAGE_UNIT_OF_PAY' not found in the dataset.")
    
    # Total Employees by Year
    df_job['Year'] = df_job['BEGIN_DATE'].dt.year
    employee_by_year = df_job.groupby("Year")["TOTAL_WORKER_POSITIONS"].sum().reset_index()
    fig_employee_year = px.line(
        employee_by_year,
        x="Year",
        y="TOTAL_WORKER_POSITIONS",
        labels={"Year": "Year", "TOTAL_WORKER_POSITIONS": "Number of Employees"},
        title="Total Employees by Year"
    )
    st.plotly_chart(fig_employee_year)
    
    # Distribution of PW_WAGE_LEVEL
    wage_level_counts = df_job['PW_WAGE_LEVEL'].value_counts().reset_index()
    wage_level_counts.columns = ['PW_WAGE_LEVEL', 'Count']
    fig_wage_level = px.histogram(
        wage_level_counts,
        x='Count',
        y='PW_WAGE_LEVEL',
        title="Distribution of PW_WAGE_LEVEL",
        labels={'PW_WAGE_LEVEL': 'Wage Level', 'Count': 'Frequency'},
        text_auto=True
    )
    st.plotly_chart(fig_wage_level)
    
    # Distribution of PW_UNIT_OF_PAY
    pay_unit_counts = df_job['PW_UNIT_OF_PAY'].value_counts().reset_index()
    pay_unit_counts.columns = ['PW_UNIT_OF_PAY', 'Count']
    fig_pay_unit = px.pie(
        pay_unit_counts,
        names='PW_UNIT_OF_PAY',
        values='Count',
        title="Distribution of PW_UNIT_OF_PAY",
        labels={'PW_UNIT_OF_PAY': 'Unit of Pay', 'Count': 'Frequency'}
    )
    st.plotly_chart(fig_pay_unit)

# ------------------ Page 3: WorkSite Analysis ------------------
def page3():
    st.markdown("### WorkSite Analysis", unsafe_allow_html=True)
    # For WorkSite Analysis we use the filtered dataset (df_filtered)
    state_dict = {
        'CA': 'California',
        'TX': 'Texas',
        'NY': 'New York',
        'WA': 'Washington',
        'NJ': 'New Jersey'
    }
    worksite_state_counts = df_filtered['WORKSITE_STATE'].value_counts().head(5)
    worksite_state_counts.index = worksite_state_counts.index.map(state_dict)
    fig = px.histogram(
        x=worksite_state_counts.index,
        y=worksite_state_counts.values,
        text_auto=True,
        labels={'x': 'Worksite State', 'y': 'Count'},
        title="Top 5 Worksite States"
    )
    st.plotly_chart(fig)
    
    worksite_city_counts = df_filtered['WORKSITE_CITY'].value_counts().head(5)
    fig2 = px.histogram(
        x=worksite_city_counts.index,
        y=worksite_city_counts.values,
        text_auto=True,
        labels={'x': 'Worksite City', 'y': 'Count'},
        title="Top 5 Worksite Cities"
    )
    st.plotly_chart(fig2)

# ------------------ Page 4: Employer Analysis ------------------
def page4():
    st.markdown("### Employer Analysis", unsafe_allow_html=True)
    df_emp = df_filtered.copy()
    # NAICS Codes Analysis
    naics_df = df_emp['NAICS_CODE'].value_counts().head(5).reset_index()
    naics_df.columns = ['NAICS_CODE', 'Count']
    naics_df['NAICS_CODE'] = naics_df['NAICS_CODE'].astype(str)
    naics_code_meanings = {
        '541211': 'Offices of Certified Public Accountants',
        '54151': 'Computer Systems Design and Related Services',
        '611310': 'Colleges, Universities, and Professional Schools',
        '541512': 'Computer Systems Design Services',
        '541511': 'Custom Computer Programming Services'
    }
    naics_df['NAICS_Description'] = naics_df['NAICS_CODE'].map(naics_code_meanings)
    fig = px.histogram(
        naics_df,
        x='Count',
        y='NAICS_Description',
        labels={'NAICS_Description': 'NAICS Description', 'Count': 'Count'},
        title='Top 5 NAICS Codes Distribution with Descriptions'
    )
    st.plotly_chart(fig)
    
    # Employer States
    emp_state = df_emp['EMPLOYER_STATE'].value_counts().head(5)
    fig2 = px.bar(
        x=emp_state.index,
        y=emp_state.values,
        text_auto=True,
        labels={'x': 'Employer State', 'y': 'Count'},
        title='Top 5 Employer States by Number of Employers'
    )
    st.plotly_chart(fig2)
    
    # Top Employers by Name
    emp_name = df_emp['EMPLOYER_NAME'].value_counts().head(5)
    fig3 = px.bar(
        y=emp_name.index,
        x=emp_name.values,
        text_auto=True,
        labels={'x': 'Count', 'y': 'Employer Name'},
        title='Top 5 Employers'
    )
    st.plotly_chart(fig3)
    
    # Employer Cities
    emp_city = df_emp['EMPLOYER_POC_CITY'].value_counts().head(5)
    fig4 = px.bar(
        x=emp_city.index,
        y=emp_city.values,
        text_auto=True,
        labels={'x': 'Employer City', 'y': 'Count'},
        title='Top 5 Employer Cities by Number of Employers'
    )
    st.plotly_chart(fig4)
    
    # Employment Categories Distribution
    emp_categories = {
        "New Employment": df_emp["NEW_EMPLOYMENT"].sum(),
        "Continued Employment": df_emp["CONTINUED_EMPLOYMENT"].sum(),
        "Change Previous Employment": df_emp["CHANGE_PREVIOUS_EMPLOYMENT"].sum(),
        "New Concurrent Employment": df_emp["NEW_CONCURRENT_EMPLOYMENT"].sum(),
        "Change Employer": df_emp["CHANGE_EMPLOYER"].sum()
    }
    emp_cat_df = pd.DataFrame(list(emp_categories.items()), columns=['Category', 'Count'])
    fig5 = px.pie(
        emp_cat_df,
        names='Category',
        values='Count',
        title="Distribution of Employment Types"
    )
    st.plotly_chart(fig5)
    
    # Top Employers by Total Worker Positions
    top_emps = df_emp.groupby("EMPLOYER_NAME")["TOTAL_WORKER_POSITIONS"].sum().nlargest(5).reset_index()
    fig6 = px.bar(
        top_emps,
        x="TOTAL_WORKER_POSITIONS",
        y="EMPLOYER_NAME",
        text_auto=True,
        labels={"TOTAL_WORKER_POSITIONS": "Total Hires", "EMPLOYER_NAME": "Employer"},
        title="Top 5 Employers by Total Worker Positions",
        orientation="h"
    )
    st.plotly_chart(fig6)
    
    # Employment Types Breakdown for Top Employers
    emp_type_df = df_emp.groupby("EMPLOYER_NAME")[["NEW_EMPLOYMENT", "CONTINUED_EMPLOYMENT", "CHANGE_PREVIOUS_EMPLOYMENT",
                                                    "NEW_CONCURRENT_EMPLOYMENT", "CHANGE_EMPLOYER"]].sum().nlargest(5, "NEW_EMPLOYMENT").reset_index()
    fig7 = px.bar(
        emp_type_df,
        x="EMPLOYER_NAME",
        y=["NEW_EMPLOYMENT", "CONTINUED_EMPLOYMENT", "CHANGE_PREVIOUS_EMPLOYMENT", "NEW_CONCURRENT_EMPLOYMENT", "CHANGE_EMPLOYER"],
        title="Employment Types Breakdown for Top Employers",
        labels={"EMPLOYER_NAME": "Employer", "value": "Count", "variable": "Employment Type"},
        barmode="group"
    )
    st.plotly_chart(fig7)

# ------------------ Page 5: Agent Analysis ------------------
def page5():
    st.markdown("### Agent Analysis", unsafe_allow_html=True)
    df_agent = df_filtered.copy()
    # Agent Representation Distribution
    agent_counts = df_agent['AGENT_REPRESENTING_EMPLOYER'].value_counts()
    fig = px.pie(
        agent_counts,
        names=agent_counts.index,
        values=agent_counts.values,
        title="Distribution of Employers Represented by Agent",
        labels={"names": "Agent Representing Employer", "values": "Count"}
    )
    st.plotly_chart(fig)
    
    # Case Status by Agent
    case_status_by_agent = df_agent.groupby(['AGENT_REPRESENTING_EMPLOYER', 'CASE_STATUS']).size().reset_index(name='Count')
    fig2 = px.bar(
        case_status_by_agent,
        x="AGENT_REPRESENTING_EMPLOYER",
        y="Count",
        color="CASE_STATUS",
        title="Case Status by Agent Representing Employer",
        labels={'AGENT_REPRESENTING_EMPLOYER': 'Agent Representing Employer', 'Count': 'Number of Cases'}
    )
    st.plotly_chart(fig2)
    
    # Attorney Analysis (filtering out 'No Agent')
    df_attorney = df_agent[df_agent['AGENT_ATTORNEY_FIRST_NAME'] != 'No Agent']
    attorney_first_name_counts = df_attorney['AGENT_ATTORNEY_FIRST_NAME'].value_counts().head(5)
    fig3 = px.bar(
        attorney_first_name_counts,
        x=attorney_first_name_counts.index,
        y=attorney_first_name_counts.values,
        text_auto=True,
        title="Top 5 Most Common First Names of Attorneys",
        labels={"x": "First Name", "y": "Count"}
    )
    st.plotly_chart(fig3)
    
    # Attorney Cities & States
    df_attorney = df_agent[(df_agent['AGENT_ATTORNEY_CITY'] != 'No Agent') & (df_agent['AGENT_ATTORNEY_STATE'] != 'No Agent')]
    attorney_city_counts = df_attorney['AGENT_ATTORNEY_CITY'].value_counts().head(5)
    fig4 = px.bar(
        attorney_city_counts,
        x=attorney_city_counts.index,
        y=attorney_city_counts.values,
        text_auto=True,
        title="Top 5 Most Common Attorney Cities",
        labels={"x": "City", "y": "Count"}
    )
    st.plotly_chart(fig4)
    
    attorney_state_counts = df_attorney['AGENT_ATTORNEY_STATE'].value_counts().head(5)
    # Rename states if desired (you can modify the mapping)
    state_dict = {"CA": "California", "NY": "New York", "TX": "Texas", "MA": "Massachusetts", "IL": "Illinois"}
    attorney_state_counts = attorney_state_counts.rename(state_dict)
    fig5 = px.bar(
        attorney_state_counts,
        x=attorney_state_counts.index,
        y=attorney_state_counts.values,
        text_auto=True,
        title="Top 5 Most Common Attorney States",
        labels={"x": "State", "y": "Count"}
    )
    st.plotly_chart(fig5)
    
    # Law Firm Analysis (filtering out 'No Agent')
    df_lawfirm = df_agent[df_agent['LAWFIRM_NAME_BUSINESS_NAME'] != 'No Agent']
    lawfirm_counts = df_lawfirm['LAWFIRM_NAME_BUSINESS_NAME'].value_counts().head(5)
    fig6 = px.bar(
        lawfirm_counts,
        x=lawfirm_counts.index,
        y=lawfirm_counts.values,
        text_auto=True,
        title="Top 5 Most Common Law Firms",
        labels={'x': 'Law Firm', 'y': 'Number of Cases'}
    )
    st.plotly_chart(fig6)

# ------------------ Page 6: Court Case Analysis ------------------
def page6():
    st.markdown("### Court Case Analysis", unsafe_allow_html=True)
    df_court = df_filtered.copy()
    # Filter out records where STATE_OF_HIGHEST_COURT equals 'No Agent'
    df_court = df_court[df_court['STATE_OF_HIGHEST_COURT'] != 'No Agent']
    state_dict = {'NY': 'New York', 'CA': 'California', 'TX': 'Texas', 'MA': 'Massachusetts', 'DC': 'District of Columbia'}
    state_counts = df_court['STATE_OF_HIGHEST_COURT'].value_counts().head(5)
    state_counts.index = state_counts.index.map(state_dict)
    fig = px.bar(
        state_counts,
        x=state_counts.index,
        y=state_counts.values,
        text_auto=True,
        title="Top 5 States with Most Cases in Highest Court",
        labels={'x': 'State', 'y': 'Number of Cases'}
    )
    st.plotly_chart(fig)
    
    case_status_by_court = df_court.groupby('STATE_OF_HIGHEST_COURT')['CASE_STATUS'].value_counts().reset_index(name='Count')
    top_5_courts = case_status_by_court.groupby('STATE_OF_HIGHEST_COURT')['Count'].sum().nlargest(5).index
    case_status_top_5 = case_status_by_court[case_status_by_court['STATE_OF_HIGHEST_COURT'].isin(top_5_courts)]
    case_status_top_5['STATE_OF_HIGHEST_COURT'] = case_status_top_5['STATE_OF_HIGHEST_COURT'].map(state_dict)
    fig2 = px.bar(
        case_status_top_5,
        x="STATE_OF_HIGHEST_COURT",
        y="Count",
        color="CASE_STATUS",
        title="Top 5 Courts with Most Cases by Case Status",
        labels={'STATE_OF_HIGHEST_COURT': 'State of Highest Court', 'Count': 'Number of Cases'}
    )
    st.plotly_chart(fig2)

# ------------------ Navigation ------------------
pages_dict = {
    "H1B Overview": page1,
    "Job Analysis": page2,
    "WorkSite Analysis": page3,
    "Employer Analysis": page4,
    "Agent Analysis": page5,
    "Court Analysis": page6
}

page = st.sidebar.selectbox("Choose a page", list(pages_dict.keys()))
pages_dict[page]()
