import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import sklearn

# Load the dataset with a specified encoding
data = pd.read_csv('filled_df.csv', encoding='latin1')
data_cleaned = data.drop(columns = ["Unnamed: 0", "Comments"])

# Page 1: Dashboard
def dashboard():
    st.image('Logo.png', use_column_width=True)

    st.subheader("💡 Abstract:")

    inspiration = '''The origins of the "Food Drive App" can be traced back to meaningful discussions
    with the City of Edmonton, Just Serve, and Church of Jesus Christ and Latter-day Saints at Norquest.
    Faced with the challenges of manual processes—counting houses, mapping routes, and collecting data through
    a basic Google form—the need for innovation became evident. What began as a response to these challenges
    has evolved into a dynamic solution.

    Our engagement in the food drive became a catalyst for refining our machine learning model and crafting this
    app. Yet, our vision extends beyond mere optimization. We strive for an approach that not only streamlines
    processes but also ensures resource allocation is more strategic and community involvement is more profound.

    The "Food Drive App" is more than just a tool; it symbolizes our commitment to making a meaningful impact.
    It represents a bridge between technology and community, making the food drive experience more seamless,
    efficient, and impactful for volunteers and the communities we aim to support.

    '''

    st.write(inspiration)

    st.subheader("👨🏻‍💻 What our Project Does?")

    what_it_does = '''
    The "Food Drive App" is a game-changer for the Edmonton Food Drive Project, transitioning from manual
    processes to a simple digital solution. This user-friendly app predicts the number of volunteers, resources
    like bags needed, maps neighborhoods, and involves the community through a straightforward form. It's all
    about optimizing our food drive, ensuring efficient resource allocation of items like bags and time, and fostering community engagement.
    '''

    st.write(what_it_does)


# Page 2: Exploratory Data Analysis (EDA)
def exploratory_data_analysis():
    st.title("Exploratory Data Analysis")


    # Visualize the distribution of numerical features using Plotly
    fig = px.histogram(data_cleaned, x='AdultVolunteer', nbins=20, labels={'AdultVolunteer': 'Adult Volunteers'})
    st.plotly_chart(fig)

    fig = px.histogram(data_cleaned, x='YouthVolunteer', nbins=20, labels={'YouthVolunteer': 'Youth Volunteers'})
    st.plotly_chart(fig)

    fig = px.histogram(data_cleaned, x='Bags', nbins=20, labels={'Bags': 'Donation Bags Collected'})
    st.plotly_chart(fig)

    fig = px.histogram(data_cleaned, x='RouteTime', nbins=20, labels={'RouteTime': 'Time to Complete(min)'})
    st.plotly_chart(fig)

    # Create a Plotly bar chart for the 'MultiRoute' column with a label
    fig = px.bar(data_cleaned, x='MultiRoute', labels={'MultiRoute': 'Completed more than 1 route?'})
    st.plotly_chart(fig)

    # Count of categorical variables using Plotly
    categorical_columns = ['Location', 'Ward', 'Stake']
    for col in categorical_columns:
        # Calculate counts
        counts = data[col].value_counts().reset_index()
        counts.columns = [col, 'Count']

        # Create a Plotly bar chart
        fig = px.bar(counts, x=col, y='Count', title=f'Most Frequently Used {col}')
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig)

    # Calculate the mean bags collected for each stake
    stake_bags = data.groupby('Stake')['Bags'].mean().reset_index()

    # Create a Plotly bar chart sorted by 'Bags' collected
    fig = px.bar(stake_bags, x='Stake', y='Bags', title='Donation Bags Collected by Stake',
                category_orders={"Stake": stake_bags.sort_values('Bags', ascending=False)['Stake']})
    fig.update_xaxes(tickangle=45)
    fig.update_layout(xaxis_title='Stake', yaxis_title='Donation Bags Collected')
    st.plotly_chart(fig)


    # Create a new column 'Scaled_RouteDoors' by dividing 'RouteDoors' by 5
    data_cleaned['Scaled_RouteDoors'] = data_cleaned['RouteDoors'] / 5

    # Aggregate data by Ward, summing up 'Scaled_RouteDoors' and 'Bags'
    agg_data = data_cleaned.groupby('Ward').agg({'Scaled_RouteDoors': 'sum', 'Bags': 'sum'}).reset_index()


    # Sort the agg_data dataframe by the 'Bags' column in descending order
    agg_data_sorted = agg_data.sort_values(by='Bags', ascending=False)

    # Calculate the 2-per moving average
    agg_data_sorted['2per_moving_avg'] = agg_data_sorted['Scaled_RouteDoors'].rolling(window=2).mean()

    # Create the plotly figure
    fig = go.Figure()

    # Add the bars for 'Scaled_RouteDoors' and 'Bags' using the sorted data
    fig.add_trace(go.Bar(x=agg_data_sorted['Ward'], y=agg_data_sorted['Scaled_RouteDoors'], name='Scaled RouteDoors', marker_color='lightsalmon'))
    fig.add_trace(go.Bar(x=agg_data_sorted['Ward'], y=agg_data_sorted['Bags'], name='Bags', marker_color='lightblue'))

    # Add the line for the 2-per moving average
    fig.add_trace(go.Scatter(x=agg_data_sorted['Ward'], y=agg_data_sorted['2per_moving_avg'], mode='lines', name='2-per Moving Average', line=dict(color='black', width=2)))

    # Update the layout
    fig.update_layout(barmode='group', xaxis_tickangle=-45, title='Proportion of Bags to Scaled RouteDoors by Ward with 2-per Moving Average')

    # Display the plot in Streamlit
    st.plotly_chart(fig)

# Page 3: Machine Learning Modeling
def machine_learning_modeling():
    st.title("Machine Learning Modeling")
    st.write("Enter the details to predict donation bags:")

    # Input fields for user to enter data

    # Stake options
    stake_options = [
        'Bonnie Doon Stake',
        'Edmonton North Stake',
        'Gateway Stake',
        'North Edmonton',
        'Riverbend Stake',
        'YSA Stake'
        ]

    # MultiRoute options
    multiroute_options = ['MultiRoute_No', 'MultiRoute_Yes']

    # Create dropdowns for user selection
    selected_stake = st.selectbox('Select Stake', stake_options)
    selected_multiroute = st.selectbox('Select MultiRoute', multiroute_options)

    # Numerical features
    routes_completed = st.slider("Routes Completed", 1, 10, 5) #CompletedRoutes
    doors_in_route = st.slider("Number of Doors in Route", 10, 500, 100) #RouteDoors
    time_spent = st.slider("Time Spent (minutes)", 10, 300, 60)


    # Map selected options to one-hot encoded values
    # Stake mapping
    stake_mapping = {
        'Bonnie Doon Stake': [1, 0, 0, 0, 0, 0],  # Replace with the corresponding one-hot encoded values
        'Edmonton North Stake': [0, 1, 0, 0, 0, 0],  # Replace with the corresponding one-hot encoded values
        'Gateway Stake': [0, 0, 1, 0, 0, 0],  # Replace with the corresponding one-hot encoded values
        'North Edmonton': [0, 0, 0, 1, 0, 0],  # Replace with the corresponding one-hot encoded values
        'Riverbend Stake': [0, 0, 0, 0, 1, 0],  # Replace with the corresponding one-hot encoded values
        'YSA Stake': [0, 0, 0, 0, 0, 1]  # Replace with the corresponding one-hot encoded values
        }

    # MultiRoute mapping
    multiroute_mapping = {
        'MultiRoute_No': [1, 0],  # Replace with the corresponding one-hot encoded values
        'MultiRoute_Yes': [0, 1]  # Replace with the corresponding one-hot encoded values
        }


    # Get one-hot encoded values for selected options
    one_hot_encoded_stake = stake_mapping[selected_stake]
    one_hot_encoded_multiroute = multiroute_mapping[selected_multiroute]



    # Predict button
    if st.button("Predict"):
        # Load the trained model
        model = joblib.load('linear_regression_bag.pkl')

        # Prepare input data for prediction, make sure to only put trained features
        # X = [['Stake','MultiRoute','CompletedRoutes','RouteDoors','OverallTime']] from modelling
        numerical_inputs = [routes_completed,doors_in_route, time_spent]

        input_data = numerical_inputs + one_hot_encoded_stake + one_hot_encoded_multiroute

        # Make prediction
        prediction = model.predict([input_data])

        # Display the prediction
        st.success(f"Predicted Donation Bags: {prediction[0]}")

        # You can add additional information or actions based on the prediction if needed


# Page 4: Neighbourhood Mapping
# Read geospatial data
geodata = pd.read_csv("EDA2_merged_data.csv")

def neighbourhood_mapping():
    st.title("Neighbourhood Mapping")

    # Get user input for neighborhood
    user_neighbourhood = st.text_input("Enter the neighborhood:")

    # Check if user provided input
    if user_neighbourhood:
        # Filter the dataset based on the user input
        filtered_data = geodata[geodata['Neighbourhood'].str.contains(user_neighbourhood, case=False)]
        no_data = (geodata['Neighbourhood'] == user_neighbourhood) & geodata['Latitude'].isna()
        naur_data = no_data.any()

        # Check if the filtered data is empty, if so, return a message indicating no data found
        if filtered_data.empty or naur_data == True:
            st.write("No data found for the specified neighborhood.")
        else:
            # Create the map using the filtered data
            fig = px.scatter_mapbox(filtered_data,
                                    lat='Latitude',
                                    lon='Longitude',
                                    hover_name='Neighbourhood',
                                    zoom=12)

            # Update map layout to use OpenStreetMap style
            fig.update_layout(mapbox_style='open-street-map')

            # Show the map
            st.plotly_chart(fig)
    else:
        st.write("Please enter a neighborhood to generate the map.")

def google_maps():
    st.title('Embedded My Google Map')
    st.write('Here is an example of embedded McConachie Map:')

    # Embedding Google Map using HTML iframe
    st.markdown("""
    <iframe src="https://www.google.com/maps/d/u/0/embed?mid=1i8duV7NujaB-oK2u6NyPcdtbrrGKttA&ehbc=2E312F&noprof=1" width="640" height="480"></iframe>
    """, unsafe_allow_html=True)

# Page 5: Data Collection
def data_collection():
    st.title("Data Collection")
    st.write("Please fill out the Google form to contribute to our Food Drive!")
    google_form_url = "https://docs.google.com/forms/d/e/1FAIpQLSdorTNQhJQ08pOFppD9zLWVoaHBmA33EIGYkDOJCA4_f5ru6A/viewform"#YOUR_GOOGLE_FORM_URL_HERE
    st.markdown(f"[Fill out the form]({google_form_url})")

# Main App Logic
def main():
    st.sidebar.title("Food Drive App")
    app_page = st.sidebar.radio("Select a Page", ["Dashboard", "EDA", "ML Modeling", "Neighbourhood Mapping", "Data Collection"])

    if app_page == "Dashboard":
        dashboard()
    elif app_page == "EDA":
        exploratory_data_analysis()
    elif app_page == "ML Modeling":
        machine_learning_modeling()
    elif app_page == "Neighbourhood Mapping":
        neighbourhood_mapping()
        google_maps()
    elif app_page == "Data Collection":
        data_collection()


if __name__ == "__main__":
    main()
