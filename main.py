import pandas as pd
import pycountry
from matplotlib import pyplot as plt
import seaborn as sns
import plotly.express as px


def assign_broader_category(job_title):
	data_engineering = [
		"Data Engineer", "Data Analyst", "Analytics Engineer", "BI Data Analyst", "Business Data Analyst",
		"BI Developer", "BI Analyst", "Business Intelligence Engineer", "BI Data Engineer", "Power BI Developer"
	]
	data_scientist = [
		"Data Scientist", "Applied Scientist", "Research Scientist", "3D Computer Vision Researcher",
		"Deep Learning Researcher", "AI/Computer Vision Engineer", "Principal Data Scientist"
	]
	machine_learning = [
		"Machine Learning Engineer", "ML Engineer", "Lead Machine Learning Engineer",
		"Principal Machine Learning Engineer"
	]
	data_architecture = ["Data Architect", "Big Data Architect", "Cloud Data Architect", "Principal Data Architect"]
	management = [
		"Data Science Manager", "Director of Data Science", "Head of Data Science", "Data Scientist Lead",
		"Head of Machine Learning", "Manager Data Management", "Data Analytics Manager"
	]

	if job_title in data_engineering or "engineer" in job_title.lower():
		return "Data Engineering"
	elif job_title in data_scientist or "scientist" in job_title.lower():
		return "Data Science"
	elif job_title in machine_learning:
		return "Machine Learning"
	elif job_title in data_architecture or "architect" in job_title.lower():
		return "Data Architecture"
	elif job_title in management:
		return "Management"
	else:
		return "Other"


df = pd.read_csv('ds_salaries.csv')

df = df.dropna(subset=['salary_in_usd'])
df['company_location'] = df['company_location'].apply(lambda x: pycountry.countries.get(alpha_2=x).alpha_3)
df['employee_residence'] = df['employee_residence'].apply(lambda x: pycountry.countries.get(alpha_2=x).alpha_3)
df.drop(df[['salary', 'salary_currency']], axis=1, inplace=True)

df['experience_level'] = df['experience_level'].replace({
	'SE': 'Senior',
	'EN': 'Entry level',
	'EX': 'Executive level',
	'MI': 'Mid/Intermediate level',
})

df['employment_type'] = df['employment_type'].replace({
	'FL': 'Freelancer',
	'CT': 'Contractor',
	'FT': 'Full-time',
	'PT': 'Part-time'
})

df['company_size'] = df['company_size'].replace({
	'S': 'SMALL',
	'M': 'MEDIUM',
	'L': 'LARGE',
})

df['job_category'] = df['job_title'].apply(assign_broader_category)

value_counts = df['job_category'].value_counts(normalize=True) * 100

fig, ax = plt.subplots(figsize=(12, 6))
top_n = min(17, len(value_counts))
ax.barh(value_counts.index[:top_n], value_counts.values[:top_n])
ax.set_xlabel('Percentage')
ax.set_ylabel('Job Category')
ax.set_title('Job Titles Percentage')
plt.savefig('results/job_titles_percentage.png')

value_counts = df['job_category'].value_counts(normalize=True) * 100
avg_salary_by_location = df.groupby('company_location', as_index=False)['salary_in_usd'].mean()

fig1 = px.choropleth(
	avg_salary_by_location,
	locations='company_location',
	locationmode='ISO-3',
	color='salary_in_usd',
	hover_name='company_location',
	color_continuous_scale=px.colors.sequential.Plasma,
	title='Average Salary by Company Location',
	labels={'salary_in_usd': 'Average Salary'},
	projection='natural earth'
)

fig1.write_image('results/avg_salary_by_company_location_map.png')

avg_salary_by_location = df.groupby('company_location')['salary_in_usd'].mean().sort_values(ascending=False)
plt.figure(figsize=(14, 6))
sns.barplot(x=avg_salary_by_location.index, y=avg_salary_by_location, color='grey')
plt.title('Average Salary by Company Location (Yearly)')
plt.xlabel('Company Location')
plt.ylabel('Average Salary (Yearly)')
plt.xticks(rotation=90)
plt.savefig('results/avg_salary_by_company_location.png')

pivot_table = df.pivot_table(values='salary_in_usd', index='job_category', columns='work_year', aggfunc='median')
plt.figure(figsize=(14, 6))
sns.heatmap(pivot_table, annot=True, fmt=".2f", cmap="YlGnBu")
plt.title('Average Salary by Year')
plt.xlabel('Year')
plt.ylabel('Job Title')
plt.savefig('results/avg_salary_by_year.png')

group = df['company_size'].value_counts()
fig = px.bar(y=group.values, x=group.index, color=group.index, text=group.values, title='Distribution of Company Size')

fig.update_layout(xaxis_title="Company Size", yaxis_title="count")
fig.write_image('results/distribution_of_company_size.png')

work_year = df['work_year'].value_counts()
fig = px.pie(values=work_year.values, names=work_year.index, title='Work year distribution')
fig.write_image('results/work_year_distribution.png')

with open("README.md", "w+") as f:
	f.write(
		"# Data Science Salary\n"
		"## Data presentation\n"
		"The data is from Kaggle's dataset of [Data Science Salary 2023](https://www.kaggle.com/datasets/arnabchaki/data-science-salaries-2023)\n\n"	
		f"{df.head().to_markdown()}\n"
		"### Data cleaning\n"
		" - Removed local salary and currency columns\n"
		" - Removed all rows where `salary_in_usd` was null\n"
		" - Converted `company_location` and `employee_residence` to alpha-3 instead of alpha-2\n"
		"### Data distribution\n"
		"![Distribution of company size.png](results/distribution_of_company_size.png)\n"
		"![Kob titles percentage.png](results/job_titles_percentage.png)\n"
		"![Work year distribution.png](results/work_year_distribution.png)\n"
		"### Data analysis\n"
		"#### Average Salary by company location\n"
		"![Salary by country](results/avg_salary_by_company_location.png)\n"
		"![Salary by country (map)](results/avg_salary_by_company_location_map.png)\n"
		"### Average Salary by job title and year\n"
		"![Average salary by year.png](results/avg_salary_by_year.png)\n\n"
		"Github link: https://github.com/MateusZ36/dataScienceSalaries"
	)
